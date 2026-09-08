import numpy as np
from maze_core import Position, Velocity

from maze.state_estimation.justin_model import (
    control_vector,
    measurement_noise,
    process_noise,
)


class KalmanFilter2D:
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
        self.x = np.array(initial_position, dtype=np.float64).reshape(2, 1)
        self.P = position_stddev**2 * np.eye(2, dtype=np.float64)

    def predict(self, dt: float, control_input: Velocity):
        u = control_vector(dt, control_input)
        Q = process_noise(dt, self.process_noise_stddev)

        self.x = self.F @ self.x + u
        self.P = self.F @ self.P @ self.F.T + Q

    def update(self, position_measurement: Position, position_stddev: float):
        z = np.array(position_measurement, dtype=np.float64).reshape(2, 1)
        R = measurement_noise(position_stddev)

        y = z - self.H @ self.x
        S = self.H @ self.P @ self.H.T + R
        K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        self.P = (np.eye(2, dtype=np.float64) - K @ self.H) @ self.P
