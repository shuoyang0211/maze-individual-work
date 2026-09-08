import numpy as np
from maze_core import Velocity


def control_vector(dt: float, control_input: Velocity) -> np.ndarray:
    """
    Return the displacement from holding `control_input` for one step of `dt`.

    Parameters:
        `dt`: Time step in seconds.
        `control_input`: Commanded velocity.

    Returns:
        The 2x1 displacement over one step.
    """
    return dt * np.array(control_input, dtype=np.float64).reshape(2, 1)


def process_noise(dt: float, process_noise_stddev: float) -> np.ndarray:
    """
    Return the process noise covariance Q for a single time step.

    Note:
        Errors behave like unknown accelerations, and are independent in each axis.
        Acceleration is integrated twice to reach position, so the variance over
        one step grows with `dt`^4 / 4.

    Parameters:
        `dt`: Time step in seconds.
        `process_noise_stddev`: Standard deviation of unexpected acceleration.

    Returns:
        The 2x2 process noise covariance Q.
    """
    raise NotImplementedError


def measurement_noise(position_stddev: float) -> np.ndarray:
    """
    Return the measurement noise covariance R for a position observation.

    Note:
        Errors are independent in each axis.

    Parameters:
        `position_stddev`: Standard deviation of the position measurement noise.

    Returns:
        The 2x2 measurement noise covariance R.
    """
    raise NotImplementedError
