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
        # 将初始坐标转换为 2x1 的列向量
        self.x = np.array(initial_position, dtype=np.float64).reshape(2, 1)
        
        # 初始的不确定性（协方差 P）等同于这第一次测量带来的噪声协方差 R
        self.P = measurement_noise(position_stddev)

    def predict(self, dt: float, control_input: Velocity):
        """
        Advance the belief by one time step, applying the process noise.

        Parameters:
            `dt`: Time step in seconds.
            `control_input`: Commanded velocity.
        """
        # 1. 计算控制量位移 u 和过程噪声矩阵 Q (使用你在 Task 0 写的函数)
        u = control_vector(dt, control_input)
        Q = process_noise(dt, self.process_noise_stddev)
        
        # 2. 预测状态 (State Extrapolation): x_{k|k-1} = F * x_{k-1|k-1} + u
        self.x = self.F @ self.x + u
        
        # 3. 预测协方差 (Covariance Extrapolation): P_{k|k-1} = F * P_{k-1|k-1} * F^T + Q
        self.P = self.F @ self.P @ self.F.T + Q

    def update(self, position_measurement: Position, position_stddev: float):
        """
        Correct the belief using a new position measurement.

        Parameters:
            `position_measurement`: Noisy measured position.
            `position_stddev`: Standard deviation of the measurement noise.
        """
        # 1. 准备观测向量 z 和测量噪声协方差 R
        z = np.array(position_measurement, dtype=np.float64).reshape(2, 1)
        R = measurement_noise(position_stddev)
        
        # 2. 计算残差/创新 (Innovation): y = z - H * x
        y = z - self.H @ self.x
        
        # 3. 计算残差协方差 (Innovation Covariance): S = H * P * H^T + R
        S = self.H @ self.P @ self.H.T + R
        
        # 4. 计算卡尔曼增益 (Kalman Gain): K = P * H^T * S^-1
        K = self.P @ self.H.T @ np.linalg.inv(S)
        
        # 5. 更新状态估计 (State Update): x_{k|k} = x_{k|k-1} + K * y
        self.x = self.x + K @ y
        
        # 6. 更新协方差 (Covariance Update): P_{k|k} = (I - K * H) * P_{k|k-1}
        I = np.eye(self.P.shape[0])
        self.P = (I - K @ self.H) @ self.P
