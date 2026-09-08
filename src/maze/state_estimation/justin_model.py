import numpy as np
from maze_core import Velocity


def control_vector(dt: float, control_input: Velocity) -> np.ndarray:
    return dt * np.array(control_input, dtype=np.float64).reshape(2, 1)


def process_noise(dt: float, process_noise_stddev: float) -> np.ndarray:
    return (dt**4 / 4.0) * process_noise_stddev**2 * np.eye(2, dtype=np.float64)


def measurement_noise(position_stddev: float) -> np.ndarray:
    return position_stddev**2 * np.eye(2, dtype=np.float64)
