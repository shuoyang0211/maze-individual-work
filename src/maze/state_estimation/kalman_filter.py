import numpy as np
from maze_core import Position, Velocity

from maze.state_estimation.model import (
    control_vector,
    measurement_noise,
    process_noise,
)


class KalmanFilter2D:
    """
    Constant-velocity 2D Kalman Filter over the position state [x, y]^T.

    Parameters:
        `process_noise_stddev`: Standard deviation of unexpected acceleration.
    """

    def __init__(self, process_noise_stddev: float):
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
            `initial_position`: Initial position.
            `position_stddev`: Standard deviation of the initial estimate.
        """
        raise NotImplementedError

    def predict(self, dt: float, control_input: Velocity):
        """
        Advance the belief by one time step, applying the process noise.

        Parameters:
            `dt`: Time step in seconds.
            `control_input`: Commanded velocity.
        """
        raise NotImplementedError

    def update(self, position_measurement: Position, position_stddev: float):
        """
        Correct the belief using a new position measurement.

        Parameters:
            `position_measurement`: Noisy measured position.
            `position_stddev`: Standard deviation of the measurement noise.
        """
        raise NotImplementedError
