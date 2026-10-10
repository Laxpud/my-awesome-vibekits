# 注释正反例与改写方法

这些案例展示注释的说明位置、粒度和上下文，不规定所有代码都套用同一格式。片段是自包含的教学场景；实际整改应先确认目标代码的行为和数据约定，再选择适用的表达。

按当前阅读障碍选择案例：

- [流程阶段与内部子步骤](#流程阶段与内部子步骤)：函数总述和局部细节之间缺少处理路线。
- [具体对象和进程资源流程](#具体对象和进程资源流程)：抽象名词掩盖了文件、进程和结果之间的关系。
- [原因到当前动作的完整因果](#原因到当前动作的完整因果)：注释只给结论，没有解释代码为何这样处理。
- [数据组织单位与公式变量对应](#数据组织单位与公式变量对应)：读者无法把数组维度、物理量和运算对应起来。
- [注释真实性](#注释真实性)：注释添加了代码和资料没有支持的行为。

## 流程阶段与内部子步骤

场景：根据离散时刻的表面位置计算速度，再求速度沿表面法向的分量。位置单位为 m，时间单位为 s；`normals` 已由调用方提供为与位置逐项对应的单位法向量。此处用有限差分近似速度，具体差分由 `numpy.gradient` 完成。

反例把注意力放在广播和求和语法上，主流程需要读者自行拼接：

```python
import numpy as np

def normal_velocity(positions, times, normals):
    """计算法向速度。"""
    # 沿 axis 0 求 gradient。
    velocity = np.gradient(positions, times, axis=0)
    # 逐元素乘法后 sum。
    return np.sum(velocity * normals, axis=-1)
```

**阅读障碍：** 没有说明哪个维度表示时间、差分得到什么物理量，也没有说明最后一步为什么得到法向速度。局部语法解释无法代替领域操作。

改写后的同一代码：

```python
import numpy as np

def normal_velocity(positions, times, normals):
    """由表面位置随时间的变化，计算各表面点的法向速度。

    positions 和 normals 的 shape 均为 (n_time, n_point, 3)，
    最后一维依次表示 x、y、z；times 为对应的采样时刻，严格递增且至少两个。
    normals 为单位向量，正负方向由调用方采用的表面法向约定决定。
    返回 shape 为 (n_time, n_point) 的法向速度，单位为 m/s。
    """
    # 1. 对每个表面点的位置沿时间方向差分，得到三维速度。
    velocity = np.gradient(positions, times, axis=0)

    # 2. 将速度投影到对应的单位法向量上，保留有符号的法向分量。
    return np.sum(velocity * normals, axis=-1)
```

**改写理由：** 函数说明建立输入和输出关系，内部步骤说明“位置→速度→法向分量”。两行实现仍然值得分成两个步骤，因为它们完成不同的物理操作。更长的实现可以在阶段内部继续解释有意义的子步骤，编号层级按实际需要选择。

## 具体对象和进程资源流程

场景：调用外部建模程序。已知该程序接受请求 JSON 路径和 STEP 输出路径两个参数；成功退出时应生成 STEP 文件。片段只检查文件是否存在，不验证模型几何或文件内容。

反例常把实现约束压成一句话：

```python
# 一次 build 只拥有一个进程和一个暂存目录，结束后发布结果。
```

**阅读障碍：** “拥有”“发布”“结果”没有具体指代；读者不知道什么被写入目录、怎样启动程序、什么条件下复制哪个文件。

改写时，保留代码并把说明放到各个对象实际出现的位置：

```python
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

def build_model(executable, request, destination):
    """将建模请求交给外部程序，并把生成的 STEP 文件复制到目标路径。

    executable 接受两个位置参数：请求 JSON 路径、STEP 输出路径。
    request 必须可序列化为 JSON；destination 的父目录须已存在。
    目标文件已存在时会被覆盖。程序失败或没有生成文件时抛出异常。
    """
    # 1. 为本次调用建立暂存目录，隔离请求文件和程序生成的 STEP 文件。
    # 离开 with 块时清理目录，包括程序失败或复制失败的情况。
    with tempfile.TemporaryDirectory() as directory:
        request_path = Path(directory) / "request.json"
        output_path = Path(directory) / "model.step"
        request_path.write_text(json.dumps(request), encoding="utf-8")

        # 2. 启动建模程序并等待结束；非零退出码直接作为调用失败处理。
        subprocess.run(
            [str(executable), str(request_path), str(output_path)], check=True
        )

        # 3. 确认程序确实留下了输出文件，再复制到调用方指定的位置。
        # 这里只检查文件存在，模型内容是否正确需要另行验证。
        if not output_path.is_file():
            raise FileNotFoundError(output_path)
        shutil.copy2(output_path, destination)
```

**改写理由：** 请求文件、建模进程、输出文件和目标路径形成完整处理路线。暂存目录的清理约束也有了明确对象和时机。如果实际任务涉及已安装包中的资源，还应说明资源的具体名称、定位结果及后续使用位置；不能用“资源不依赖 checkout”替代这些信息。

## 原因到当前动作的完整因果

场景：极坐标绘图数据覆盖一整圈，但采样方位角不包含终点。调用方已确认该数据按周向周期重复；`azimuth` 按递增顺序排列，单位为 rad，`values` 是相应的标量采样值。此例不适用于未经确认的有限时间记录。

反例只留下操作结论：

```python
import numpy as np

# 多取一个点，保证闭合。
closed_azimuth = np.concatenate([azimuth, azimuth[:1] + 2 * np.pi])
closed_values = np.concatenate([values, values[:1]])
```

**阅读障碍：** 没有说明哪个方向闭合、为什么复制首点，以及复制值与增加角度之间的关系。“多取”还可能让人误以为读取了额外的原始数据。

改写后的同一代码：

```python
import numpy as np

# 方位角采样不包含一圈的终点。为让极坐标曲线连接最后一个采样点
# 和起点，在末尾追加“起始角 + 2π”及起点的数值。
# 这利用了已确认的周向周期性；追加的是首点副本，不是新测量值。
closed_azimuth = np.concatenate([azimuth, azimuth[:1] + 2 * np.pi])
closed_values = np.concatenate([values, values[:1]])
```

**改写理由：** 前提“缺少终点”、动作“追加首点副本”和用途“连接曲线首尾”连在一起。周期性是该操作成立的条件，必须先确认；不能因为代码使用了复制或插值，就反推数据必然周期重复。

## 数据组织单位与公式变量对应

场景：声源和观测点均固定在同一笛卡尔坐标系中，介质静止，声速为空间和时间上的常数；用距离除以声速估计传播时间。此处仅生成声源时刻数组，不完成声源信号插值。

反例省略了数组轴与物理量的对应：

```python
import numpy as np

def source_times(observed_times, observers, sources, sound_speed):
    # 广播计算 retarded time，覆盖多个插值位置。
    displacement = observers[:, None, :] - sources[None, :, :]
    distance = np.linalg.norm(displacement, axis=-1)
    return observed_times[:, None, None] - distance[None, :, :] / sound_speed
```

**阅读障碍：** 不知道每一轴对应时间、观测点还是声源；也不知道输出时刻如何与后续声源信号关联。“覆盖多个插值位置”无法解释当前运算，而且该函数尚未执行插值。

改写后的同一代码：

```python
import numpy as np

def source_times(observed_times, observers, sources, sound_speed):
    """计算各观测时刻对应的声源时刻，供后续查询声源信号使用。

    observed_times: shape (n_time,)，观测时刻，单位 s；与声源信号共用时间原点。
    observers: shape (n_observer, 3)，观测点坐标，单位 m。
    sources: shape (n_source, 3)，固定声源坐标，单位 m。
    sound_speed: 正的常数声速，单位 m/s。
    坐标均使用同一坐标系；返回 shape 为 (n_time, n_observer, n_source)。
    """
    # 1. 为每对观测点和声源计算空间距离 R。
    # 两个点集分别扩展一条轴，形成 (n_observer, n_source, 3) 的位移数组。
    displacement = observers[:, None, :] - sources[None, :, :]
    distance = np.linalg.norm(displacement, axis=-1)

    # 2. 按 t_source = t_observed - R/c 扣除传播时间。
    # distance 对应 R，sound_speed 对应 c；新增时间轴后，输出逐项对应
    # “观测时刻、观测点、声源”，可用于后续查询该声源在发声时刻的信号。
    return observed_times[:, None, None] - distance[None, :, :] / sound_speed
```

**改写理由：** 数据契约解释各轴、单位和坐标约定，内部说明连接距离计算、公式与广播结果。专业术语可以保留，但需要让读者知道当前算出了什么。此公式以固定声源和恒定声速为前提，不能直接推广到运动声源的传播求解。

## 注释真实性

场景：只看到一个更新计数的函数，没有重试调度、上限判断或熔断实现，也没有其他已确认资料。

反例：

```python
def record_attempt(attempt_count):
    # 最多重试三次，超过后触发熔断。
    attempt_count += 1
    return attempt_count
```

**阅读障碍：** 读者会误以为函数限制了调用次数并实施熔断。代码实际上只更新一个数字；次数上限、何时算一次尝试和停止条件均无法从这里确认。

改写后的同一代码：

```python
def record_attempt(attempt_count):
    """将传入的尝试次数增加一次，并返回更新后的计数。"""
    attempt_count += 1
    return attempt_count
```

**改写理由：** 简短说明已经覆盖该函数能够确认的行为，无需为单次加法强加编号步骤。若当前任务还要求解释重试策略，应继续阅读调用方及相应配置，找到上限判断和停止动作后再说明；没有证据时在审查结论中记录待核实项。不能用一条注释宣告代码已具备这些行为。
