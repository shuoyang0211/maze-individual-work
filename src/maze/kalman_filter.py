import numpy as np
from maze_core import Position, Velocity


def control_vector(dt: float, control_input: Velocity) -> np.ndarray:
    """
    Return the displacement from holding `control_input` for one step of `dt`.

    Parameters:
        `dt`: Time step in seconds.
        `control_input`: Tuple (vx, vy) representing the commanded velocity.

    Returns:
        The 2x1 displacement over one step.
    """
    return dt * np.array(control_input, dtype=np.float64).reshape(2, 1)


def process_noise(dt: float, process_noise_stddev: float) -> np.ndarray:
    """
    Return the process noise covariance Q for a single time step.

    Q represents acceleration uncertainty. The noise in each axis is
    independent, so Q is diagonal, and acceleration is integrated twice to
    reach position, so the variance over one step grows with `dt`^4 / 4.

    Parameters:
        `dt`: Time step in seconds.
        `process_noise_stddev`: Standard deviation of the acceleration noise.

    Returns:
        The 2x2 process noise covariance Q.
    """
    raise NotImplementedError


def measurement_noise(position_stddev: float) -> np.ndarray:
    """
    Return the measurement noise covariance R for a position observation.

    Observations are isotropic: the same standard deviation in each axis, with
    no correlation between them.

    Parameters:
        `position_stddev`: Standard deviation of the position measurement noise.

    Returns:
        The 2x2 measurement noise covariance R.
    """
    raise NotImplementedError


class KalmanFilter2D:
    """
    Constant-velocity 2D Kalman Filter over the position state [x, y]^T, whose
    covariance starts at 1e4 until `initialize` is called.

    The previous position is carried forward unchanged and the commanded motion
    enters separately through the control vector, so `F` is the identity; the
    agent observes its position directly, so `H` is as well. Q and R come from
    `process_noise` and `measurement_noise`, which `FactorGraphFilter2D` also
    calls — that shared model is what makes the two filters comparable.

    Parameters:
        `process_noise_stddev`: Standard deviation of the acceleration noise.
    """

    def __init__(self, process_noise_stddev: float = 2.0):
        # Estimated state and its covariance
        self.x = np.zeros((2, 1), dtype=np.float64)
        self.P = np.eye(2, dtype=np.float64) * 1e4

        # Measurement and transition matrices
        self.H = np.eye(2, dtype=np.float64)
        self.F = np.eye(2, dtype=np.float64)

        self.process_noise_stddev = process_noise_stddev

    @property
    def position(self) -> tuple[float, float]:
        return float(self.x[0, 0]), float(self.x[1, 0])

    @property
    def variance(self) -> tuple[float, float]:
        return float(self.P[0, 0]), float(self.P[1, 1])

    def initialize(self, initial_position: Position, position_stddev: float):
        """
        Set the belief to `initial_position` with the given uncertainty.

        Parameters:
            `initial_position`: Tuple (x, y) representing the initial position.
            `position_stddev`: Standard deviation of the initial estimate.
        """
        raise NotImplementedError

    def predict(self, dt: float, control_input: Velocity):
        """
        Advance the belief by one time step, applying the process noise.

        Parameters:
            `dt`: Time step in seconds.
            `control_input`: Tuple (vx, vy) representing the commanded velocity.
        """
        raise NotImplementedError

    def update(self, position_measurement: Position, position_stddev: float):
        """
        Fold a position measurement into the belief.

        Parameters:
            `position_measurement`: Tuple (x, y) of the measured position.
            `position_stddev`: Standard deviation of the measurement noise.
        """
        raise NotImplementedError
