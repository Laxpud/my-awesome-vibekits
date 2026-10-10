import numpy as np

def create_image_source(coords: np.ndarray, normals: np.ndarray, 
                       surface_dir: np.ndarray, surface_pos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    根据平面反射计算镜像声源的坐标和法向量。
    
    参数:
        coords: 坐标数组 (3, ...)
        normals: 法向量数组 (3, ...)
        surface_dir: 反射平面的法向量 (A, B, C)
        surface_pos: 反射平面上的一点 (x0, y0, z0)
        
    返回:
        (image_coords, image_normals)
    """
    # 平面方程: Ax + By + Cz + D = 0
    # D = - dot(normal, point)
    D = -np.dot(surface_dir, surface_pos)
    S = np.dot(surface_dir, surface_dir) # |n|^2
    
    # 广播 surface_dir 以匹配 coords 形状
    # coords 形状通常是 (3, IMAX, JMAX, Time)
    
    shape_suffix = (1,) * (coords.ndim - 1)
    n_vec = surface_dir.reshape((3,) + shape_suffix)
    
    # t = dot(n, P) + D
    t = np.sum(n_vec * coords, axis=0) + D
    
    # 反射公式: P' = P - 2 * n * t / |n|^2
    image_coords = coords - 2 * n_vec * t / S
    
    # 法向量反射
    # n_dot_m = dot(surface_dir, normals)
    n_dot_m = np.sum(n_vec * normals, axis=0)
    image_normals = normals - 2 * n_vec * n_dot_m / S
    
    return image_coords, image_normals

def calculate_grazing_angle(surface_dir: np.ndarray, surface_pos: np.ndarray, 
                          obs_pos: np.ndarray) -> float:
    """
    计算水面反射的掠射角。
    """
    # 确保转换为 numpy 数组
    normal = np.array(surface_dir, dtype=float)
    surface_pos = np.array(surface_pos, dtype=float)
    obs_pos = np.array(obs_pos, dtype=float)
    source_pos = np.array([0.0, 0.0, 0.0])  # 假设声源位于原点 (旋翼中心)
    
    # 归一化法向量
    normal = normal / np.linalg.norm(normal)
    
    # 1. 声源到平面的向量
    vec_ps = source_pos - surface_pos
    # 2. 声源到平面的距离
    dist = np.dot(vec_ps, normal)
    # 3. 镜像声源位置
    image_source = source_pos - 2 * dist * normal
    
    # 镜像声源到观测点的向量
    vec_image_to_obs = obs_pos - image_source
    
    # 掠射角计算
    # sin(theta) = |vec . n| / |vec|
    numerator = np.abs(np.dot(vec_image_to_obs, normal))
    denominator = np.linalg.norm(vec_image_to_obs)
    
    if denominator == 0:
        return 0.0
        
    sin_grazing = numerator / denominator
    sin_grazing = np.clip(sin_grazing, 0.0, 1.0)
    
    return np.arcsin(sin_grazing)
