# 代码注释原始案例归档

保存日期：2026-10-10。

本目录按用户指定范围保存 7 个正例和 3 个反例的完整源文件。归档文件直接复制自下列原始路径，未运行、未修改；保存时逐一核对 SHA256 与原文件一致，保留原有换行和尾随空白。它们是该日期的快照，后续原项目修改不会自动同步到本目录。

正例用于参考用户的注释风格和说明粒度，不代表代码、参数和注释均已全面验证。反例仅指用户指出的具体注释，不表示整个文件的注释或实现都差；索引中的搜索文字用于定位这些片段。

本目录仅供维护技能时查阅，不是技能运行依赖，不参与插件安装。安装技能中的自包含教学案例位于 [comment-examples.md](../../plugins/code-quality/skills/code-comment-standard/references/comment-examples.md)，不会在运行时引用本目录或原始绝对路径。

## 正例

- [geometry.py](positive/geometry.py)：几何对象与数据处理的说明。
  - 原始路径：`/home/laxpud/workspace/pyracoustics/src/pyracoustics/geometry.py`

- [post_process.py](positive/post_process.py)：后处理流程、公式与变量对应。
  - 原始路径：`/home/laxpud/workspace/pyracoustics/src/pyracoustics/post_process.py`

- [solver.py](positive/solver.py)：求解流程与内部步骤说明。
  - 原始路径：`/home/laxpud/workspace/pyracoustics/src/pyracoustics/solver.py`

- [preprocess_ffsr.py](positive/preprocess_ffsr.py)：预处理流程与数据操作说明。
  - 原始路径：`/run/media/laxpud/YangFan/Cases/20251010_Bo105_StarCCM_WGE/Cases260417/Analysis/src/pipelines/preprocess_ffsr.py`

- [spectral_ffsr.py](positive/spectral_ffsr.py)：频谱处理流程与计算说明。
  - 原始路径：`/run/media/laxpud/YangFan/Cases/20251010_Bo105_StarCCM_WGE/Cases260417/Analysis/src/pipelines/spectral_ffsr.py`

- [freqdomain_obs01_load_ff_Case05-Case01_global.py](positive/freqdomain_obs01_load_ff_Case05-Case01_global.py)：频域绘图的数据准备与处理步骤。
  - 原始路径：`/run/media/laxpud/YangFan/Cases/20251010_Bo105_StarCCM_WGE/Cases260417/Analysis/script/paper_plot/freqdomain_obs01_load_ff_Case05-Case01_global.py`

- [Cn_Case01_OWSGE_cycle4.py](positive/Cn_Case01_OWSGE_cycle4.py)：数据读取、圈数截取、方位角转换与极坐标绘图流程。
  - 原始路径：`/run/media/laxpud/YangFan/Cases/20251010_Bo105_StarCCM_WGE/Cases260417/Analysis/script/draft/Cn_Case01_OWSGE_cycle4.py`

## 反例

- [main.rs](negative/main.rs)：搜索“surface face 分布在轻微起伏的椭圆柱面上”与“observer 放在远场圆周上”。
  - 原始路径：`/run/media/laxpud/T7 Shield/git-repo/cfd-kernel-bench/kernels/fwh_surface_integral/rust/src/main.rs`

- [adapter.py](negative/adapter.py)：搜索“一次 build 只拥有一个进程”与“资源从已安装 package 定位”。
  - 原始路径：`/home/laxpud/workspace/catia-autoblade/src/autoblade/adapters/cad/freecad/adapter.py`

- [runner.py](negative/runner.py)：搜索“无内部 knot 的多项式段”。
  - 原始路径：`/home/laxpud/workspace/catia-autoblade/src/autoblade/adapters/cad/freecad/runner.py`
