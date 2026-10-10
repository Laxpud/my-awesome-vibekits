use std::env;
use std::error::Error;
use std::f64::consts::PI;
use std::fs::File;
use std::io::{BufWriter, Write};
use std::time::Instant;

// Rust 原生实现提供 compute 和 bench 两种模式：
// compute 输出完整 observer-time 信号给 Python runner 验证，bench 只计核心积分时间。
const DEFAULT_FACES: usize = 512;
const DEFAULT_OBSERVERS: usize = 8;
const DEFAULT_TIMES: usize = 128;
const DEFAULT_STEPS: usize = 3;
const SOURCE_TIME_PADDING: usize = 128;
const SOURCE_DT: f64 = 2.0e-4;
const SOUND_SPEED: f64 = 340.0;
const FOUR_PI: f64 = 4.0 * PI;

#[derive(Debug)]
struct Config {
    mode: String,
    faces: usize,
    observers: usize,
    times: usize,
    steps: usize,
    warmups: usize,
    runs: usize,
    output: Option<String>,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            mode: "compute".to_string(),
            faces: DEFAULT_FACES,
            observers: DEFAULT_OBSERVERS,
            times: DEFAULT_TIMES,
            steps: DEFAULT_STEPS,
            warmups: 1,
            runs: 5,
            output: None,
        }
    }
}

struct InputData {
    centers: Vec<f64>,
    normals: Vec<f64>,
    areas: Vec<f64>,
    signal_history: Vec<f64>,
    observers_xyz: Vec<f64>,
    observer_times: Vec<f64>,
    source_times: usize,
}

// 三维向量按 entity-major 存储：第 entity 个三维量的 component 映射到 entity * 3 + component。
fn vector3_index(entity_index: usize, component: usize) -> usize {
    entity_index * 3 + component
}

// 源项历史采用 row-major (face, source_time)，单个 face 的时间序列连续。
fn signal_index(face_index: usize, time_index: usize, source_times: usize) -> usize {
    face_index * source_times + time_index
}

// 输出采用 row-major (observer, observer_time)，单个 observer 的信号连续。
fn output_index(observer_index: usize, time_index: usize, times: usize) -> usize {
    observer_index * times + time_index
}

fn parse_args() -> Result<Config, Box<dyn Error>> {
    let mut config = Config::default();
    let mut args = env::args().skip(1);
    // 手写轻量级 CLI 解析，保持 native 可执行文件没有外部 crate 依赖。
    while let Some(arg) = args.next() {
        let mut value = || -> Result<String, Box<dyn Error>> {
            args.next()
                .ok_or_else(|| format!("missing value after {arg}").into())
        };
        match arg.as_str() {
            "--mode" => config.mode = value()?,
            "--faces" => config.faces = value()?.parse()?,
            "--observers" => config.observers = value()?.parse()?,
            "--times" => config.times = value()?.parse()?,
            "--steps" => config.steps = value()?.parse()?,
            "--warmups" => config.warmups = value()?.parse()?,
            "--runs" => config.runs = value()?.parse()?,
            "--output" => config.output = Some(value()?),
            _ => return Err(format!("unknown argument: {arg}").into()),
        }
    }
    validate_config(&config)?;
    Ok(config)
}

fn validate_config(config: &Config) -> Result<(), Box<dyn Error>> {
    // 至少一个 face 和 observer 才能构成 surface-to-observer 积分。
    if config.faces < 1 {
        return Err("faces must be at least 1".into());
    }
    if config.observers < 1 {
        return Err("observers must be at least 1".into());
    }
    if config.times < 1 {
        return Err("times must be at least 1".into());
    }
    if config.steps < 1 {
        return Err("steps must be at least 1".into());
    }
    if config.runs < 1 {
        return Err("runs must be at least 1".into());
    }
    Ok(())
}

fn source_value(face_index: usize, time_value: f64) -> f64 {
    let phase = 0.17 * (face_index % 19) as f64;
    let frequency = 85.0 + 3.0 * (face_index % 11) as f64;
    let amplitude = 1.0 + 0.05 * ((face_index % 7) as f64 - 3.0);
    amplitude
        * ((2.0 * PI * frequency * time_value + phase).sin()
            + 0.25 * (PI * frequency * time_value + 0.5 * phase).cos())
}

fn normalize3(x: f64, y: f64, z: f64) -> Result<(f64, f64, f64), Box<dyn Error>> {
    let length = (x * x + y * y + z * z).sqrt();
    if length == 0.0 {
        return Err("cannot normalize a zero vector".into());
    }
    Ok((x / length, y / length, z / length))
}

fn generate_input(config: &Config) -> Result<InputData, Box<dyn Error>> {
    let source_times = config.times + SOURCE_TIME_PADDING;
    let mut data = InputData {
        centers: vec![0.0; config.faces * 3],
        normals: vec![0.0; config.faces * 3],
        areas: vec![0.0; config.faces],
        signal_history: vec![0.0; config.faces * source_times],
        observers_xyz: vec![0.0; config.observers * 3],
        observer_times: vec![0.0; config.times],
        source_times,
    };

    // surface face 分布在轻微起伏的椭圆柱面上，与 Python reference 的公式一致。
    for face in 0..config.faces {
        let angle = 2.0 * PI * (face as f64 + 0.5) / config.faces as f64;
        let z_fraction = (((17 * face) % config.faces) as f64 + 0.5) / config.faces as f64;
        let z = -0.45 + 0.90 * z_fraction;
        let radius = 1.0 + 0.08 * (3.0 * angle).cos();
        data.centers[vector3_index(face, 0)] = radius * angle.cos();
        data.centers[vector3_index(face, 1)] = 0.75 * radius * angle.sin();
        data.centers[vector3_index(face, 2)] = z;
        let (nx, ny, nz) = normalize3(angle.cos(), angle.sin(), 0.20 * z.sin())?;
        data.normals[vector3_index(face, 0)] = nx;
        data.normals[vector3_index(face, 1)] = ny;
        data.normals[vector3_index(face, 2)] = nz;
        data.areas[face] =
            FOUR_PI / config.faces as f64 * (1.0 + 0.02 * ((face % 5) as f64 - 2.0));
    }

    // observer 放在远场圆周上，z 方向轻微错开以覆盖多个 retarded-time 插值位置。
    for observer in 0..config.observers {
        let angle = 2.0 * PI * observer as f64 / config.observers as f64;
        data.observers_xyz[vector3_index(observer, 0)] = 6.0 * angle.cos();
        data.observers_xyz[vector3_index(observer, 1)] = 6.0 * angle.sin();
        data.observers_xyz[vector3_index(observer, 2)] = 0.35 * ((observer % 3) as f64 - 1.0);
    }

    let mut max_delay = 0.0_f64;
    for observer in 0..config.observers {
        for face in 0..config.faces {
            let dx = data.observers_xyz[vector3_index(observer, 0)]
                - data.centers[vector3_index(face, 0)];
            let dy = data.observers_xyz[vector3_index(observer, 1)]
                - data.centers[vector3_index(face, 1)];
            let dz = data.observers_xyz[vector3_index(observer, 2)]
                - data.centers[vector3_index(face, 2)];
            max_delay = max_delay.max((dx * dx + dy * dy + dz * dz).sqrt() / SOUND_SPEED);
        }
    }
    let observer_start = max_delay + 2.0 * SOURCE_DT;
    for time in 0..config.times {
        data.observer_times[time] = observer_start + SOURCE_DT * time as f64;
    }

    // 合成源项时间历程按 face-major 写入；插值时固定 face 后访问相邻时间样本。
    for face in 0..config.faces {
        for time in 0..data.source_times {
            data.signal_history[signal_index(face, time, data.source_times)] =
                source_value(face, time as f64 * SOURCE_DT);
        }
    }

    Ok(data)
}

fn interpolate_sample(data: &InputData, face: usize, retarded_time: f64) -> f64 {
    let scaled = retarded_time / SOURCE_DT;
    let lower = scaled.floor() as isize;
    if lower < 0 || lower as usize >= data.source_times - 1 {
        return 0.0;
    }
    let lower = lower as usize;
    let fraction = scaled - lower as f64;
    let left = data.signal_history[signal_index(face, lower, data.source_times)];
    let right = data.signal_history[signal_index(face, lower + 1, data.source_times)];
    (1.0 - fraction) * left + fraction * right
}

fn run_kernel(data: &InputData, output: &mut [f64], config: &Config) {
    for _ in 0..config.steps {
        // steps 只重复同一段积分以扩大计时量，不推进源项或 observer 时间。
        for observer in 0..config.observers {
            let ox = data.observers_xyz[vector3_index(observer, 0)];
            let oy = data.observers_xyz[vector3_index(observer, 1)];
            let oz = data.observers_xyz[vector3_index(observer, 2)];
            for time in 0..config.times {
                let observer_time = data.observer_times[time];
                let mut accumulator = 0.0;
                for face in 0..config.faces {
                    let dx = ox - data.centers[vector3_index(face, 0)];
                    let dy = oy - data.centers[vector3_index(face, 1)];
                    let dz = oz - data.centers[vector3_index(face, 2)];
                    let radius = (dx * dx + dy * dy + dz * dz).sqrt();
                    let directivity = (data.normals[vector3_index(face, 0)] * dx
                        + data.normals[vector3_index(face, 1)] * dy
                        + data.normals[vector3_index(face, 2)] * dz)
                        / radius;
                    let retarded_time = observer_time - radius / SOUND_SPEED;
                    let sampled_source = interpolate_sample(data, face, retarded_time);
                    accumulator += data.areas[face] * directivity * sampled_source / (FOUR_PI * radius);
                }
                output[output_index(observer, time, config.times)] = accumulator;
            }
        }
    }
}

fn checksum(values: &[f64]) -> f64 {
    values.iter().sum()
}

fn write_field(values: &[f64], config: &Config) -> Result<(), Box<dyn Error>> {
    let output = config
        .output
        .as_ref()
        .ok_or("--output is required in compute mode")?;
    let file = File::create(output)?;
    let mut writer = BufWriter::new(file);
    writeln!(writer, "{} {}", config.observers, config.times)?;
    // Python runner 按 observer-major row-major 顺序读回，再 reshape 成 (observers, times)。
    for value in values {
        writeln!(writer, "{value:.17e}")?;
    }
    Ok(())
}

fn run_compute(config: &Config) -> Result<(), Box<dyn Error>> {
    // compute 模式只生成 observer-time 信号，用于统一验证，不记录 timing。
    let data = generate_input(config)?;
    let mut output = vec![0.0; config.observers * config.times];
    run_kernel(&data, &mut output, config);
    write_field(&output, config)
}

fn timed_run_seconds(data: &InputData, output: &mut [f64], config: &Config) -> f64 {
    let started_at = Instant::now();
    run_kernel(data, output, config);
    started_at.elapsed().as_secs_f64()
}

fn run_bench(config: &Config) -> Result<(), Box<dyn Error>> {
    // 输入生成和数组分配在计时区间外完成，只让 Instant 包住核心积分。
    let data = generate_input(config)?;
    let mut output = vec![0.0; config.observers * config.times];

    for _ in 0..config.warmups {
        let _ = timed_run_seconds(&data, &mut output, config);
    }

    let mut samples = Vec::with_capacity(config.runs);
    for _ in 0..config.runs {
        samples.push(timed_run_seconds(&data, &mut output, config));
    }
    // 与其他原生实现一致，报告排序后的中位样本。
    samples.sort_by(|left, right| left.partial_cmp(right).unwrap());

    let median = samples[samples.len() / 2];
    let total_time_samples = (config.times * config.steps) as f64;
    let time_per_step = median / total_time_samples;
    let active_cells = (config.faces * config.observers) as f64;
    let throughput = active_cells * total_time_samples / median / 1.0e6;

    println!("kernel_name=fwh_surface_integral");
    println!("language=rust");
    println!("implementation=rust_native");
    println!("compiler_or_runtime=rust");
    println!("compiler_flags=unknown");
    println!("precision=float64");
    println!("data_layout=row_major_surface_time_history_faces_by_time_observers_by_time_output");
    println!("array_size={}x{}", config.observers, config.faces);
    println!("num_steps={}", config.times * config.steps);
    println!("runs={}", config.runs);
    println!("wall_time_seconds={median:.17e}");
    println!("time_per_step_seconds={time_per_step:.17e}");
    println!("throughput_mcells_per_second={throughput:.17e}");
    println!("checksum={:.17e}", checksum(&output));
    Ok(())
}

fn main() -> Result<(), Box<dyn Error>> {
    let config = parse_args()?;
    match config.mode.as_str() {
        "compute" => run_compute(&config)?,
        "bench" => run_bench(&config)?,
        other => return Err(format!("unknown mode: {other}").into()),
    }
    Ok(())
}
