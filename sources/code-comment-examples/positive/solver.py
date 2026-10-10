import numpy as np
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Tuple, List
from tqdm import tqdm
from queue import Queue
from .config import Config, Observer
from . import acoustics
from . import geometry
from . import utils
from .record_time import (
    common_finite_window,
    interpolate_finite,
    interpolate_periodic,
    uniform_finite_grid,
    validate_strictly_increasing,
)
from .utils import time_tracker

logger = logging.getLogger(__name__)

class BaseSolver:
    """
    求解器基类，包含通用的运动学准备、差分计算和声学求解逻辑。
    """
    def __init__(self, config: Config, data: Dict[str, np.ndarray]):
        self.config = config
        self.data = data
        self.imax = data['imax']
        self.jmax = data['jmax']
        self.time_steps = data['time_steps']
        
        self.psi_cx = self.config.time_settings.total_time_steps
        
        # 网格数据的发射时间数组
        # Fortran: TIME_TEMP = DT_step * (K - 1)
        # K 从 -1 到 PSI_CX+2
        self.k_indices = np.arange(self.time_steps, dtype=np.float64) - 1
        self.emission_times = self.config.dt_step * (self.k_indices - 1)
        
        # 输出时间网格 (接收时间)
        self.ntime = self.config.time_settings.total_sampling_points
        self.reception_times = np.arange(self.ntime, dtype=np.float64) * self.config.dt_sample
        
    def solve(self) -> Dict[int, np.ndarray]:
        """
        执行求解流程，由子类实现具体逻辑。
        返回: {obs_id: (2, NTIME) array} -> [Thickness, Load]
        """
        raise NotImplementedError

    def _prepare_kinematics(self, coords_base: np.ndarray, norms_base: np.ndarray,
                          advance_vel: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        准备运动学数据：计算每一时刻的位置、速度、法向速度。
        """
        # FW-H 声学方程中外向法矢（从物体指向流体）为正向约定。
        # CFD 数据中的法矢为内向法矢（从物体表面指向内部），此处取反以适配声学公式。
        norms_base = -norms_base

        # 1. 计算位置 = 基础坐标 + 前飞位移
        # 利用广播机制: advance_vel (3, 1, 1, 1) * time (1, 1, 1, T)
        adv_disp = advance_vel.reshape(3, 1, 1, 1) * self.emission_times.reshape(1, 1, 1, -1)
        coords = coords_base + adv_disp

        # 2. 计算速度 = 坐标的中心差分
        # Fortran: VEL = (COOR(K+1) - COOR(K-1)) / (2*dt)
        vel = acoustics.calculate_derivatives(coords, self.config.dt_step)

        # 3. 截取法向量以匹配速度的时间维度 (去掉头尾各1个点)
        norms_inner = norms_base[..., 1:-1]

        # 4. 计算法向速度 VN = VEL . NORM（外向法矢）
        vn = np.sum(vel * norms_inner, axis=0)
        
        return coords[..., 1:-1], vel, vn, norms_inner

    def _calculate_derivatives(self, vel, vn, norm, pre):
        """
        计算用于声学公式的物理量对时间的导数。
        """
        dt = self.config.dt_step
        
        vel_dot = acoustics.calculate_derivatives(vel, dt)
        vn_dot = acoustics.calculate_derivatives(vn, dt)
        norm_dot = acoustics.calculate_derivatives(norm, dt)
        
        # 压力导数计算
        # pre 是全时间序列，需要计算对应于声学循环 (K=1 到 PSI_CX) 的导数
        full_pre_dot = acoustics.calculate_derivatives(pre, dt)
        # 需要截取中间段以匹配其他导数的维度
        pre_dot = full_pre_dot[..., 1:-1]
        
        return vel_dot, vn_dot, norm_dot, pre_dot

    def _solve_acoustics(self, coords, vel, vn, pre, norm, area,
                       vel_dot, vn_dot, pre_dot, norm_dot) -> Dict[int, np.ndarray]:
        """
        执行核心声学计算 (F1A 公式)。
        """
        # 对齐所有输入数据到有效计算范围 (K=1 到 PSI_CX)
        n_active = vel_dot.shape[-1]
        
        vel_active = vel[..., 1:-1]
        vn_active = vn[..., 1:-1]
        norm_active = norm[..., 1:-1]
        coords_active = coords[..., 1:-1]
        
        # 压力和面积从原始数据中截取对应段 (索引 2 到 2+n_active)
        pre_active = pre[..., 2:2+n_active]
        area_active = area[..., 2:2+n_active]
        
        # 对应的发射时间
        emit_times_active = self.emission_times[2:2+n_active]

        # 翼段记录的接收时间和周期语义与历史旋翼不同，单独走新路径。
        # 旋翼分支以下代码保持原有执行顺序，以便回归基准继续可比。
        if getattr(self.config, "is_airfoil", False):
            return self._solve_acoustics_airfoil(
                coords_active,
                vel_active,
                vn_active,
                pre_active,
                norm_active,
                area_active,
                vel_dot,
                vn_dot,
                pre_dot,
                norm_dot,
                emit_times_active,
            )
        
        results = {}
        
        # 并行计算每个观测点
        num_workers = self.config.project.num_workers
        
        # 创建位置队列，用于管理多行进度条的位置 (1 到 num_workers)
        position_queue = Queue()
        for i in range(num_workers):
            position_queue.put(i + 1)
            
        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {}
            for obs in self.config.observers:
                futures[obs.id] = executor.submit(
                    self._solve_single_observer,
                    obs, emit_times_active, 
                    coords_active, vel_active, vn_active, pre_active, norm_active, area_active,
                    vel_dot, vn_dot, pre_dot, norm_dot,
                    position_queue
                )
            
            # 主进度条 (position=0)
            for future in tqdm(as_completed(futures.values()), total=len(futures), desc="Total Progress", position=0, leave=True):
                try:
                    # 获取结果，但不在这里处理，因为 submit 返回的 future 已经包含了结果
                    # 我们需要在 futures 字典中找到对应的 obs_id 比较麻烦，
                    # 但其实我们只需要确保所有任务完成。
                    # 为了构建 results 字典，我们可以遍历 futures.items()
                    pass
                except Exception as e:
                    # 异常会在下面遍历时再次捕获
                    pass

            # 收集结果
            for obs_id, future in futures.items():
                try:
                    results[obs_id] = future.result()
                except Exception as e:
                    logger.error(f"Calculation error at observer {obs_id}: {e}")
                    raise
                    
        return results

    def _solve_single_observer(self, obs: Observer, emit_times, 
                             coords, vel, vn, pre, norm, area,
                             vel_dot, vn_dot, pre_dot, norm_dot,
                             position_queue: Queue):
        """
        单个观测点的声学计算逻辑。
        """
        from scipy.interpolate import interp1d
        
        # 获取进度条位置
        pos = position_queue.get()
        
        try:
            shape_t = emit_times.shape[0]
            n_cells = self.imax * self.jmax
            
            # 展平空间维度以便向量化计算
            coords_flat = coords.reshape(3, n_cells, shape_t)
            vel_flat = vel.reshape(3, n_cells, shape_t)
            vn_flat = vn.reshape(n_cells, shape_t)
            pre_flat = pre.reshape(n_cells, shape_t)
            norm_flat = norm.reshape(3, n_cells, shape_t)
            area_flat = area.reshape(n_cells, shape_t)
            
            vel_dot_flat = vel_dot.reshape(3, n_cells, shape_t)
            vn_dot_flat = vn_dot.reshape(n_cells, shape_t)
            pre_dot_flat = pre_dot.reshape(n_cells, shape_t)
            norm_dot_flat = norm_dot.reshape(3, n_cells, shape_t)
            
            # 结果累加器 (厚度噪声, 载荷噪声)
            total_signal = np.zeros((2, self.ntime), dtype=np.float64)
            
            obs_pos_arr = obs.to_array()
            
            # 遍历每个网格单元
            # 使用 tqdm 显示进度
            iterator = tqdm(range(n_cells), desc=f"Obs {obs.id}", position=pos, leave=False, unit="cell", mininterval=1.0, miniters=1000)
            
            for idx in iterator:
    
                # 提取单元的时间序列数据
                c_coords = coords_flat[:, idx, :]
                c_vel = vel_flat[:, idx, :]
                c_vn = vn_flat[idx, :]
                c_pre = pre_flat[idx, :]
                c_norm = norm_flat[:, idx, :]
                c_area = area_flat[idx, :]
                
                c_vel_dot = vel_dot_flat[:, idx, :]
                c_vn_dot = vn_dot_flat[idx, :]
                c_pre_dot = pre_dot_flat[idx, :]
                c_norm_dot = norm_dot_flat[:, idx, :]

                    # 1. 计算延迟时间 (Retarded Time)
                reception_times, obs_pos_emit, time_prop = acoustics.calculate_retarded_time_and_emission_pos(
                    c_coords, obs_pos_arr, self.config.obs_velocity, emit_times, self.config.sound_speed
                )
                
                # 计算接收时刻观测点位置
                # OBS_RECEIVE = OBS_START + V_OBS * TIME_RECEIVE
                # TIME_RECEIVE = TIME_EMIT + TIME_PROP
                # 或者 OBS_RECEIVE = OBS_EMIT + V_OBS * TIME_PROP
                
                obs_pos_receive = obs_pos_emit + self.config.obs_velocity[:, np.newaxis] * time_prop[np.newaxis, :]
                
                # 2. 计算声压 (F1A 公式)
                # 注意：传入 obs_pos_receive，使得 F1A 内部使用接收时刻的几何关系
                sp_thick, sp_load = acoustics.f1a_formulation(
                    c_vel, c_vn, c_pre, c_norm, c_area,
                    c_vel_dot, c_vn_dot, c_pre_dot, c_norm_dot,
                    obs_pos_receive, c_coords,
                    self.config.sound_speed, self.config.rho
                )
                
                # 3. 插值到均匀时间网格 (处理周期性)
                time_per_cycle = self.config.time_per_cycle
                
                # 对接收时间进行排序
                sort_idx = np.argsort(reception_times)
                t_sorted = reception_times[sort_idx]
                thick_sorted = sp_thick[sort_idx]
                load_sorted = sp_load[sort_idx]
    
                # 构造周期扩展数据 (t-T, t, t+T) 以覆盖插值范围
                t_ext = np.concatenate([t_sorted - time_per_cycle, t_sorted, t_sorted + time_per_cycle])
                thick_ext = np.concatenate([thick_sorted, thick_sorted, thick_sorted])
                load_ext = np.concatenate([load_sorted, load_sorted, load_sorted])
                
                # 创建线性插值函数
                f_thick = interp1d(t_ext, thick_ext, kind='linear', bounds_error=False, fill_value=0.0)
                f_load = interp1d(t_ext, load_ext, kind='linear', bounds_error=False, fill_value=0.0)
                
                # 重采样到输出时间点
                interp_thick = f_thick(self.reception_times)
                interp_load = f_load(self.reception_times)
                
                total_signal[0] += interp_thick
                total_signal[1] += interp_load
            
        finally:
            # 释放进度条位置
            position_queue.put(pos)
            
        return total_signal


    def _airfoil_common_reception_window(
        self,
        coords: np.ndarray,
        emit_times: np.ndarray,
    ) -> tuple[float, float]:
        """求全部源面元和观察者共同有效的有限记录接收窗口。

        亚声速声源的迟滞时间映射应当严格递增，因此首尾样本给出每个
        面元的有效区间。这里先对全部观察者和面元检查单调性，再取区间
        交集；这样后续插值可以完全禁止边缘补零。
        """

        if not self.config.observers:
            raise ValueError("airfoil finite record requires at least one observer")
        n_cells = self.imax * self.jmax
        shape_t = emit_times.shape[0]
        coords_flat = coords.reshape(3, n_cells, shape_t)
        bounds: list[tuple[float, float]] = []

        for obs in self.config.observers:
            obs_bounds: list[tuple[float, float]] = []
            obs_pos_arr = obs.to_array()
            for idx in range(n_cells):
                reception_times, _, _ = acoustics.calculate_retarded_time_and_emission_pos(
                    coords_flat[:, idx, :],
                    obs_pos_arr,
                    self.config.obs_velocity,
                    emit_times,
                    self.config.sound_speed,
                )
                validate_strictly_increasing(
                    reception_times,
                    context=f"observer {obs.id} source cell {idx} reception times",
                )
                obs_bounds.append((float(reception_times[0]), float(reception_times[-1])))
            bounds.append((max(item[0] for item in obs_bounds), min(item[1] for item in obs_bounds)))

        return common_finite_window(bounds)

    def _validate_airfoil_periodic_source(self, emit_times: np.ndarray) -> None:
        """检查完整周期块及其二阶差分辅助帧的源数据闭合性。

        活动记录首尾之间相隔 ``cycles*T``，原始输入还包含首尾各两帧的
        中心差分辅助数据。因此比较原始数组的 ``0:5`` 与按完整记录步数
        平移后的 ``period_steps:period_steps+5``，同时覆盖活动端点和两侧
        导数 stencil。压力使用相对容差，接近零的量由绝对容差控制。
        """

        period_steps = int(emit_times.size - 1)
        pressure = np.asarray(self.data["pressure"])
        raw_steps = pressure.shape[-1]
        if raw_steps < period_steps + 5:
            raise ValueError(
                "airfoil periodic source does not contain the two-frame endpoint "
                "stencils required for closure validation"
            )
        rtol = 1.0e-5
        atol = 1.0e-8
        for name in ("coords", "normals", "area", "pressure"):
            values = np.asarray(self.data[name])
            if values.shape[-1] < period_steps + 5:
                raise ValueError(
                    f"airfoil periodic source field {name!r} is shorter than the configured record"
                )
            first_stencil = values[..., :5]
            repeated_stencil = values[..., period_steps:period_steps + 5]
            if not np.allclose(first_stencil, repeated_stencil, rtol=rtol, atol=atol):
                raise ValueError(
                    f"airfoil periodic source field {name!r} closure failed over the endpoint "
                    f"two-frame stencil (rtol={rtol:g}, atol={atol:g}); use record_type=finite "
                    "unless the complete source block is known to repeat"
                )

    def _solve_acoustics_airfoil(
        self,
        coords,
        vel,
        vn,
        pre,
        norm,
        area,
        vel_dot,
        vn_dot,
        pre_dot,
        norm_dot,
        emit_times,
    ) -> Dict[int, np.ndarray]:
        """计算翼段记录，按有限或完整周期块分别处理接收时间。"""

        record_type = str(getattr(self.config.time_settings, "record_type", "finite")).casefold()
        if record_type not in {"finite", "periodic"}:
            raise ValueError("airfoil record_type must be 'finite' or 'periodic'")
        if emit_times.size < 2:
            raise ValueError("airfoil acoustic record requires at least two active emission times")

        # 活动发射时间包含整个配置记录的首尾点；使用实际跨度作为周期，
        # 允许导出时间间隔存在配置容差内的浮点差异。
        record_period = float(emit_times[-1] - emit_times[0])
        expected_period = float(self.config.time_per_cycle * self.config.time_settings.cycles)
        if not np.isclose(record_period, expected_period, rtol=1.0e-6, atol=1.0e-12):
            raise ValueError(
                "airfoil active emission span is inconsistent with configured cycles: "
                f"span={record_period:.12g}, expected={expected_period:.12g}"
            )

        if record_type == "finite":
            start, end = self._airfoil_common_reception_window(coords, emit_times)
            self.reception_times = uniform_finite_grid(start, end, self.config.dt_sample)
        else:
            self._validate_airfoil_periodic_source(emit_times)
            # 周期模式把 cycles*T 作为一个完整可重复块；目标网格不从传播
            # 延迟起算，而是通过每个面元自己的相位映射覆盖任意远场延迟。
            self.reception_times = np.arange(
                self.config.time_settings.total_sampling_points,
                dtype=np.float64,
            ) * self.config.dt_sample
            if self.reception_times.size < 2:
                raise ValueError("airfoil periodic record requires at least two output samples")
        self.ntime = self.reception_times.size

        results: Dict[int, np.ndarray] = {}
        num_workers = self.config.project.num_workers
        position_queue = Queue()
        for i in range(num_workers):
            position_queue.put(i + 1)

        with ThreadPoolExecutor(max_workers=num_workers) as executor:
            futures = {}
            for obs in self.config.observers:
                futures[obs.id] = executor.submit(
                    self._solve_single_observer_airfoil,
                    obs,
                    emit_times,
                    coords,
                    vel,
                    vn,
                    pre,
                    norm,
                    area,
                    vel_dot,
                    vn_dot,
                    pre_dot,
                    norm_dot,
                    record_type,
                    record_period,
                    position_queue,
                )

            for future in tqdm(
                as_completed(futures.values()),
                total=len(futures),
                desc="Total Progress",
                position=0,
                leave=True,
            ):
                future.result()

            for obs_id, future in futures.items():
                try:
                    results[obs_id] = future.result()
                except Exception as exc:
                    logger.error(f"Calculation error at observer {obs_id}: {exc}")
                    raise

        return results

    def _solve_single_observer_airfoil(
        self,
        obs: Observer,
        emit_times,
        coords,
        vel,
        vn,
        pre,
        norm,
        area,
        vel_dot,
        vn_dot,
        pre_dot,
        norm_dot,
        record_type: str,
        record_period: float,
        position_queue: Queue,
    ) -> np.ndarray:
        """计算单观察者翼段信号，并使用真实接收时间插值。"""

        pos = position_queue.get()
        try:
            shape_t = emit_times.shape[0]
            n_cells = self.imax * self.jmax
            coords_flat = coords.reshape(3, n_cells, shape_t)
            vel_flat = vel.reshape(3, n_cells, shape_t)
            vn_flat = vn.reshape(n_cells, shape_t)
            pre_flat = pre.reshape(n_cells, shape_t)
            norm_flat = norm.reshape(3, n_cells, shape_t)
            area_flat = area.reshape(n_cells, shape_t)
            vel_dot_flat = vel_dot.reshape(3, n_cells, shape_t)
            vn_dot_flat = vn_dot.reshape(n_cells, shape_t)
            pre_dot_flat = pre_dot.reshape(n_cells, shape_t)
            norm_dot_flat = norm_dot.reshape(3, n_cells, shape_t)
            total_signal = np.zeros((2, self.ntime), dtype=np.float64)
            obs_pos_arr = obs.to_array()

            iterator = tqdm(
                range(n_cells),
                desc=f"Obs {obs.id}",
                position=pos,
                leave=False,
                unit="cell",
                mininterval=1.0,
                miniters=1000,
            )
            for idx in iterator:
                c_coords = coords_flat[:, idx, :]
                c_vel = vel_flat[:, idx, :]
                c_vn = vn_flat[idx, :]
                c_pre = pre_flat[idx, :]
                c_norm = norm_flat[:, idx, :]
                c_area = area_flat[idx, :]
                c_vel_dot = vel_dot_flat[:, idx, :]
                c_vn_dot = vn_dot_flat[idx, :]
                c_pre_dot = pre_dot_flat[idx, :]
                c_norm_dot = norm_dot_flat[:, idx, :]

                source_reception_times, obs_pos_emit, time_prop = acoustics.calculate_retarded_time_and_emission_pos(
                    c_coords,
                    obs_pos_arr,
                    self.config.obs_velocity,
                    emit_times,
                    self.config.sound_speed,
                )
                validate_strictly_increasing(
                    source_reception_times,
                    context=f"observer {obs.id} source cell {idx} reception times",
                )
                obs_pos_receive = obs_pos_emit + self.config.obs_velocity[:, np.newaxis] * time_prop[np.newaxis, :]

                sp_thick, sp_load = acoustics.f1a_formulation(
                    c_vel,
                    c_vn,
                    c_pre,
                    c_norm,
                    c_area,
                    c_vel_dot,
                    c_vn_dot,
                    c_pre_dot,
                    c_norm_dot,
                    obs_pos_receive,
                    c_coords,
                    self.config.sound_speed,
                    self.config.rho,
                )

                if record_type == "finite":
                    interp_thick = interpolate_finite(
                        source_reception_times,
                        sp_thick,
                        self.reception_times,
                        context=f"observer {obs.id} source cell {idx} thickness",
                    )
                    interp_load = interpolate_finite(
                        source_reception_times,
                        sp_load,
                        self.reception_times,
                        context=f"observer {obs.id} source cell {idx} load",
                    )
                else:
                    interp_thick = interpolate_periodic(
                        source_reception_times,
                        sp_thick,
                        self.reception_times,
                        record_period,
                        context=f"observer {obs.id} source cell {idx} thickness",
                    )
                    interp_load = interpolate_periodic(
                        source_reception_times,
                        sp_load,
                        self.reception_times,
                        record_period,
                        context=f"observer {obs.id} source cell {idx} load",
                    )

                total_signal[0] += interp_thick
                total_signal[1] += interp_load
        finally:
            position_queue.put(pos)
        return total_signal


class FreeFieldSolver(BaseSolver):
    """
    自由场求解器。
    """
    @time_tracker
    def solve(self) -> Dict[int, np.ndarray]:
        logger.info("Preparing Free Field kinematics...")
        ff_coords, ff_vel, ff_vn, ff_norm = self._prepare_kinematics(
            self.data['coords'],
            self.data['normals'],
            self.config.advance_velocity
        )

        logger.info("Calculating Free Field derivatives...")
        ff_vel_dot, ff_vn_dot, ff_norm_dot, ff_pre_dot = self._calculate_derivatives(
            ff_vel, ff_vn, ff_norm, self.data['pressure']
        )

        logger.info("Solving Free Field acoustics...")
        results = self._solve_acoustics(
            ff_coords, ff_vel, ff_vn, self.data['pressure'], ff_norm, self.data['area'],
            ff_vel_dot, ff_vn_dot, ff_pre_dot, ff_norm_dot
        )

        return results


class SurfaceReflectionSolver(BaseSolver):
    """
    水面反射求解器。
    """
    @time_tracker
    def solve(self) -> Dict[int, np.ndarray]:
        logger.info("Preparing Surface Reflection kinematics...")
        
        # 1. 创建镜像声源
        sr_coords_base, sr_norm_base = geometry.create_image_source(
            self.data['coords'], 
            self.data['normals'],
            np.array(self.config.solver_options.surface_reflection.geometry.direction),
            np.array(self.config.solver_options.surface_reflection.geometry.position)
        )
        
        # 2. 准备运动学数据
        sr_coords, sr_vel, sr_vn, sr_norm = self._prepare_kinematics(
            sr_coords_base,
            sr_norm_base,
            self.config.advance_velocity
        )
        
        logger.info("Calculating Surface Reflection derivatives...")
        sr_vel_dot, sr_vn_dot, sr_norm_dot, sr_pre_dot = self._calculate_derivatives(
            sr_vel, sr_vn, sr_norm, self.data['pressure']
        )
        
        logger.info("Solving Surface Reflection acoustics...")
        results = self._solve_acoustics(
            sr_coords, sr_vel, sr_vn, self.data['pressure'], sr_norm, self.data['area'],
            sr_vel_dot, sr_vn_dot, sr_pre_dot, sr_norm_dot
        )
        
        return results
