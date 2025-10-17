from maze_core import Position, Velocity
import numpy as np

class KalmanFilter2D:
    """
    Constant-velocity 2D Kalman Filter.
    The internal state is represented as a column vector containing the 2D position: [x, y]^T
    The initial covariances are large (1e4) until initialized.

    The process model assumes constant velocity, with process noise representing acceleration uncertainty. Furthermore,
    assume that the position noise in each axis is independent.

    Parameters:
        - process_noise_stddev: Standard deviation of the acceleration noise (affects the process noise covariance Q
    """

    def __init__(self, process_noise_stddev: float = 2.0):
        # Estimated State
        self.x = np.zeros((2, 1), dtype=np.float64)
        # Estimated State Covariance
        self.P = np.eye(2, dtype=np.float64) * 1e4

        # Measurement Matrix
        self.H = np.eye(2, dtype=np.float64)
        # Transition Matrix
        self.F = np.eye(2, dtype=np.float64)

        # Process Noise Covariance
        self.process_noise_stddev = process_noise_stddev

    @property
    def position(self) -> tuple[float, float]:
        return float(self.x[0,0]), float(self.x[1,0])

    @property
    def variance(self) -> tuple[float, float]:
        return float(self.P[0,0]), float(self.P[1,1])

    def initialize(self, initial_position: Position, position_stddev: float):
        """
        Initialize the filter with an initial position and covariance.
        The initial velocity is set to zero with no uncertainty.

        Parameters:
            - initial_position: Tuple (x, y) representing the initial position.
            - position_var: Variance of the initial position estimate.
        """
        raise NotImplementedError

    def predict(self, dt: float, control_input: Velocity):
        """
        Predict the next state and covariance given the time step and the control input (velocity).
        Note that the process noise is applied here and corresponds to acceleration uncertainty.
        Since we assume that the noise in each axis is independent, the process noise covariance matrix Q is diagonal.
        Furthermore, the variance in position grows with dt^4/4 (due to double integration of acceleration)

        Parameters:
            - dt: Time step in seconds.
        """
        raise NotImplementedError

    def update(self, position_measurement: Position, position_stddev: float):
        """
        Update the state with a new position and velocity measurement.
        Parameters:
            - position_measurement: Tuple (x, y) representing the measured position.
            - position_stddev: Standard deviation of the position measurement noise.
        """
        raise NotImplementedError