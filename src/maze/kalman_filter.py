import numpy as np
from maze_core import Position, Velocity


def transition_matrix() -> np.ndarray:
    """
    Return the state transition matrix F.

    Under the constant-velocity model the previous position is carried forward unchanged; the commanded motion enters
    separately through the control vector, so F is the identity.
    """
    return np.eye(2, dtype=np.float64)


def control_vector(dt: float, control_input: Velocity) -> np.ndarray:
    """
    Return the displacement u contributed by holding a commanded velocity for one time step.

    Parameters:
        - dt: Time step in seconds.
        - control_input: Tuple (vx, vy) representing the commanded velocity.
    """
    return dt * np.array(control_input, dtype=np.float64).reshape(2, 1)


def process_noise(dt: float, process_noise_stddev: float) -> np.ndarray:
    """
    Return the process noise covariance Q.

    The process noise represents acceleration uncertainty. Since we assume the noise in each axis is independent, Q is
    diagonal, and since acceleration is integrated twice to reach position, the variance grows with dt^4/4.

    Parameters:
        - dt: Time step in seconds.
        - process_noise_stddev: Standard deviation of the acceleration noise.
    """
    return (dt**4 / 4.0) * process_noise_stddev**2 * np.eye(2, dtype=np.float64)


def measurement_matrix() -> np.ndarray:
    """
    Return the measurement matrix H.

    The agent observes its own position directly, so H is the identity.
    """
    return np.eye(2, dtype=np.float64)


def measurement_noise(position_stddev: float) -> np.ndarray:
    """
    Return the measurement noise covariance R for an isotropic position observation.

    Parameters:
        - position_stddev: Standard deviation of the position measurement noise.
    """
    return position_stddev**2 * np.eye(2, dtype=np.float64)


class KalmanFilter2D:
    """
    Constant-velocity 2D Kalman Filter.
    The internal state is represented as a column vector containing the 2D position: [x, y]^T
    The initial covariances are large (1e4) until initialized.

    The process model assumes constant velocity, with process noise representing acceleration uncertainty. Furthermore,
    assume that the position noise in each axis is independent. The matrices of that model are defined by the module
    level functions above, which you should use rather than rebuilding F, Q, H, and R by hand. `FactorGraphFilter2D` in
    `factor_graph.py` is built from the same functions, which is what lets the two filters be compared directly.

    Parameters:
        - process_noise_stddev: Standard deviation of the acceleration noise (affects the process noise covariance Q
    """

    def __init__(self, process_noise_stddev: float = 2.0):
        # Estimated State
        self.x = np.zeros((2, 1), dtype=np.float64)
        # Estimated State Covariance
        self.P = np.eye(2, dtype=np.float64) * 1e4

        # Measurement Matrix
        self.H = measurement_matrix()
        # Transition Matrix
        self.F = transition_matrix()

        # Process Noise Covariance
        self.process_noise_stddev = process_noise_stddev

    @property
    def position(self) -> tuple[float, float]:
        return float(self.x[0, 0]), float(self.x[1, 0])

    @property
    def variance(self) -> tuple[float, float]:
        return float(self.P[0, 0]), float(self.P[1, 1])

    def initialize(self, initial_position: Position, position_stddev: float):
        """
        Initialize the filter with an initial position and covariance.
        The initial velocity is set to zero with no uncertainty.

        Parameters:
            - initial_position: Tuple (x, y) representing the initial position.
            - position_stddev: Standard deviation of the initial position estimate.
        """
        raise NotImplementedError

    def predict(self, dt: float, control_input: Velocity):
        """
        Predict the next state and covariance given the time step and the control input (velocity).
        Note that the process noise is applied here and corresponds to acceleration uncertainty.

        Parameters:
            - dt: Time step in seconds.
            - control_input: Tuple (vx, vy) representing the commanded velocity.
        """
        raise NotImplementedError

    def update(self, position_measurement: Position, position_stddev: float):
        """
        Update the state with a new position measurement.

        Parameters:
            - position_measurement: Tuple (x, y) representing the measured position.
            - position_stddev: Standard deviation of the position measurement noise.
        """
        raise NotImplementedError
