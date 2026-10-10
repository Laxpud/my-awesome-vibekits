import os
import numpy as np
import pandas as pd
import logging  
from typing import Dict, List, Tuple
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from .config import Config, Observer
from . import geometry
from . import utils
from .paths import resolve_output_dir
from .utils import time_tracker

logger = logging.getLogger(__name__)

def _process_single_observer_task(
    obs: Observer, 
    signal: np.ndarray, 
    config: Config, 
    suffix: str,
    output_dir: str,
    time_arr_ms: np.ndarray,
    ntime: int
) -> Tuple[List[float], int]:
    """
    单个观测点的处理任务（模块级函数，便于多进程 pickle）。
    返回: (spl_data, obs_id) 或 None
    """
    try:
        # 0. 粗糙表面修正 (仅针对 SR 且配置启用)
        # 移至最前，确保无论是单片输出还是叠加后输出，都是经过修正的信号
        if suffix == "SR" and config.solver_options.surface_reflection.roughness_filter:
            # 创建 filter 实例 (轻量级)
            roughness_filter = RoughSurfaceFilter(config)
            
            grazing_angle = geometry.calculate_grazing_angle(
                np.array(config.solver_options.surface_reflection.geometry.direction),
                np.array(config.solver_options.surface_reflection.geometry.position),
                obs.to_array()
            )
            
            thick_corrected = roughness_filter.apply(signal[0], grazing_angle)
            load_corrected = roughness_filter.apply(signal[1], grazing_angle)
            
            signal = np.stack([thick_corrected, load_corrected])

        # 1. 桨叶叠加逻辑
        if not config.is_airfoil and config.rotor.blade_count > 1:
            # 叠加前先输出单桨叶结果
            _export_csv(signal, config, output_dir, time_arr_ms, suffix, obs.id, is_rotor=False)
            
            # 执行叠加
            final_signal = _superpose_blades(signal, config.rotor.blade_count, ntime)
        else:
            final_signal = signal
        
        # 3. 输出旋翼结果 (CSV)
        _export_csv(final_signal, config, output_dir, time_arr_ms, suffix, obs.id, is_rotor=True)
        
        # 4. 计算 SPL
        total_fluc = utils.compute_fluctuations(final_signal[0]) + \
                     utils.compute_fluctuations(final_signal[1])
        spl = utils.compute_spl(total_fluc)
        
        return [obs.x, obs.y, obs.z, spl, obs.id], obs.id
        
    except Exception as e:
        logger.error(f"Error processing observer {obs.id}: {e}")
        raise e

def _superpose_blades(signal: np.ndarray, n_blades: int, n_time: int) -> np.ndarray:
    """叠加多桨叶噪声"""
    shift_step = int(n_time / n_blades)
    accumulated_signal = np.zeros_like(signal, dtype=np.float64)
    
    for i in range(n_blades):
        shift = i * shift_step
        blade_signal = np.roll(signal, -shift, axis=1)
        accumulated_signal += blade_signal
        
    return accumulated_signal

def _export_csv(signal: np.ndarray, config: Config, output_dir: str, time_arr_ms: np.ndarray, suffix: str, obs_id: int, is_rotor: bool):
    """输出单点时间历程 CSV"""
    # 翼段只输出实际积分的声源贡献，不执行桨叶移相，也不使用 Rotor 名称。
    prefix = "Section" if config.is_airfoil else ("Rotor" if is_rotor else "Blade")
    output_prefix = os.path.basename(config.project.output_prefix)
    fname = f"{output_prefix}_{prefix}_OBS{obs_id:04d}_{suffix}.csv"
    fpath = os.path.join(output_dir, fname)
    
    thick_fluc = utils.compute_fluctuations(signal[0])
    load_fluc = utils.compute_fluctuations(signal[1])
    total_fluc = thick_fluc + load_fluc
    
    df = pd.DataFrame({
        'Time': time_arr_ms,
        'Thickness': thick_fluc,
        'Load': load_fluc,
        'Total': total_fluc
    })
    df.to_csv(fpath, index=False)


class RoughSurfaceFilter:
    """
    粗糙表面滤波修正类。
    """
    def __init__(self, config: Config):
        self.config = config
        self.wave_height = 0.02 # 可以考虑移至配置
        # 常量定义
        self.Z_air = 415.0
        self.Z_water = 1.5e6
        self.R0 = (self.Z_water - self.Z_air) / (self.Z_water + self.Z_air)
        self.C = self.config.sound_speed

    def apply(self, signal: np.ndarray, grazing_angle: float) -> np.ndarray:
        """
        对信号应用粗糙表面滤波。
        参数:
            signal: 压力信号数组
            grazing_angle: 掠射角 (弧度)
            
        返回:
            修正后的信号数组
        """
        dt = self.config.dt_sample
        n = len(signal)
        
        # 1. 转换到频域
        freqs = np.fft.rfftfreq(n, d=dt)
        fft_vals = np.fft.rfft(signal)
        
        # 2. 计算相干反射系数 (Coherent Reflection Coefficient)
        # k = 2 * pi * f / C
        k = 2 * np.pi * freqs / self.C
        
        # Gamma = (2 * k * h * sin(theta))^2
        # h = wave_rms_height
        gamma = (2 * k * self.wave_height * np.sin(grazing_angle))**2
        
        # R_coh = R0 * exp(-Gamma / 2)
        r_coh = self.R0 * np.exp(-gamma / 2)
        
        # 3. 频域修正
        fft_corrected = r_coh * fft_vals
        
        # 4. 逆变换回时域
        signal_corrected = np.fft.irfft(fft_corrected, n=n)
        
        return signal_corrected


class PostProcessor:
    """
    后处理类，负责：
    1. 桨叶噪声叠加 (如果需要)
    2. 粗糙表面修正 (如果启用)
    3. 结果输出 (CSV 和 DAT)
    """
    def __init__(self, config: Config):
        self.config = config
        # 声学需要至少一个观测点，空配置不能被统计为成功导出。
        if not config.observers:
            raise ValueError("Acoustics requires at least one observer")
        # 输出根目录由 output_prefix 决定；OUTPUT 的大小写兼容逻辑保留旧算例目录。
        output_root = os.path.dirname(config.project.output_prefix)
        self.output_dir = resolve_output_dir(output_root, "OUTPUT")
            
        self.filter = RoughSurfaceFilter(config)
        
        # 输出时间网格 (ms)
        self.ntime = self.config.time_settings.total_sampling_points
        self.reception_times = np.arange(self.ntime, dtype=np.float64) * self.config.dt_sample
        self.time_arr_ms = self.reception_times * 1000.0

    @time_tracker
    def process_and_export(self, results: Dict[int, np.ndarray], suffix: str = "FF",
                           reception_times: np.ndarray | None = None):
        """
        处理并输出结果。
        参数:
            results: {obs_id: (2, NTIME) array} -> [Thickness, Load]
            suffix: "FF" (自由场) 或 "SR" (反射场)
            reception_times: 求解器实际使用的接收时间，单位 s。有限翼段记录的
                有效区间由传播延迟决定，不能重新生成从零开始的时间轴。
        """
        # 0. 旋翼继续沿用旧时间网格。翼段要求显式传入求解器时间，防止有限
        # 记录裁剪后导出错位；不同传播路径（FF/SR）的有效窗口可能不同。
        if self.config.is_airfoil:
            if reception_times is None:
                raise ValueError("Airfoil export requires solver reception_times")
            times = np.asarray(reception_times, dtype=np.float64)
            if (times.ndim != 1 or times.size < 2 or not np.all(np.isfinite(times))
                    or not np.all(np.diff(times) > 0)):
                raise ValueError("Reception times must be a finite increasing 1D array")
            if not np.allclose(np.diff(times), self.config.dt_sample, rtol=1e-8, atol=1e-12):
                raise ValueError("Reception time spacing does not match dt_sample")
            self.reception_times = times
            self.ntime = times.size
            self.time_arr_ms = times * 1000.0
            for obs_id, signal in results.items():
                if np.shape(signal) != (2, self.ntime) or not np.all(np.isfinite(signal)):
                    raise ValueError(f"Invalid airfoil signal for observer {obs_id}")
        # 1. 要求结果覆盖配置中的全部观测点，避免部分缺失仍报告成功。
        missing_ids = [obs.id for obs in self.config.observers if obs.id not in results]
        if missing_ids:
            raise ValueError(f"Missing calculation results for observers: {missing_ids}")
        spl_list = []
        
        # 提前打印日志
        if suffix == "SR" and self.config.solver_options.surface_reflection.roughness_filter:
            logger.info("Applying roughness filter to all observers...")

        # 准备并行任务
        with ProcessPoolExecutor(max_workers=self.config.project.num_workers) as executor:
            futures = []
            for obs in self.config.observers:
                if obs.id not in results:
                    continue
                
                signal = results[obs.id]
                
                # 提交任务
                # 注意：传递 self.config 可能会比较大，但 ProcessPoolExecutor 需要序列化参数
                # 如果 config 很大，可以考虑只传递必要的参数
                future = executor.submit(
                    _process_single_observer_task,
                    obs,
                    signal,
                    self.config,
                    suffix,
                    self.output_dir,
                    self.time_arr_ms,
                    self.ntime
                )
                futures.append(future)
            
            # 收集结果
            for future in tqdm(as_completed(futures), total=len(futures), desc="Exporting Results", unit="obs"):
                try:
                    res = future.result()
                    if res:
                        spl_data, obs_id = res
                        spl_list.append(spl_data)
                except Exception as e:
                    logger.error(f"Post-processing failed for a task: {e}")
                    raise
            
        # 5. 输出 Tecplot DAT 文件
        if spl_list:
            # 保持输出顺序一致性，按 ID 排序
            spl_list.sort(key=lambda x: x[4]) # x[4] is obs.id
            self._export_dat(spl_list, suffix)

    def _export_dat(self, spl_list: list, suffix: str):
        """
        输出 Tecplot DAT 文件。
        """
        output_prefix = os.path.basename(self.config.project.output_prefix)
        section = "_Section" if self.config.is_airfoil else ""
        fname = f"{output_prefix}{section}_SPL_{suffix}.dat"
        fpath = os.path.join(self.output_dir, fname)
        
        with open(fpath, 'w') as f:
            f.write('title="plot"\n')
            f.write('variables="X","Y","Z","SPL(dB)","IOBS"\n')
            nobs = len(spl_list)
            f.write(f'zone,i={nobs},datapacking=point\n')
            for row in spl_list:
                f.write(f"{row[0]:.5f} {row[1]:.5f} {row[2]:.5f} {row[3]:.5f} {row[4]}\n")
