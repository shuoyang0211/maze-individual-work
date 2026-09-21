from dataclasses import dataclass, replace

import numpy as np
from maze_core import Position, Velocity

from maze.state_estimation.model import (
    control_vector,
    measurement_noise,
    process_noise,
)


@dataclass
class GaussianFactor:
    """
    A Gaussian potential in canonical form over the variables in `scope`, each
    of which has `dim` components.

    Note:
        `Lambda` and `eta` are laid out in scope order, i.e., `scope[i]` owns
        rows and columns `i * dim` through `(i + 1) * dim`.
    """

    scope: tuple[str, ...]
    dim: int
    Lambda: np.ndarray
    eta: np.ndarray

    def indices_for(self, *variables: str) -> np.ndarray:
        """
        Return the row and column indices that `variables` occupy in `Lambda`
        and `eta`, concatenated in the order given. Pair with `np.ix_(idx, idx)`
        to slice a square block out of `Lambda`.

        Parameters:
            `variables`: Variables to address.

        Returns:
            The concatenated indices of the requested blocks.
        """
        blocks = []
        for var in variables:
            start = self.scope.index(var) * self.dim
            blocks.append(np.arange(start, start + self.dim))
        return np.concatenate(blocks) if blocks else np.zeros(0, dtype=np.intp)


def to_moment(factor: GaussianFactor) -> tuple[np.ndarray, np.ndarray]:
    """Return the mean and covariance of a factor over a single variable."""
    Sigma = np.linalg.inv(factor.Lambda)
    mu = Sigma @ factor.eta
    return mu, Sigma


def prior_factor(mean: np.ndarray, cov: np.ndarray, var: str) -> GaussianFactor:
    """Canonical form of a Gaussian prior N(mean, cov) over a single variable."""
    try:
        Lambda = np.linalg.inv(cov)
    except np.linalg.LinAlgError:
        raise ValueError("prior_factor() requires a positive definite covariance") from None
    eta = Lambda @ mean
    return GaussianFactor(scope=(var,), dim=mean.shape[0], Lambda=Lambda, eta=eta)


def measurement_factor(H: np.ndarray, R: np.ndarray, z: np.ndarray, var: str) -> GaussianFactor:
    """Canonical form of the likelihood N(z; H @ x, R) as a factor over `var`."""
    Rinv = np.linalg.inv(R)
    Lambda = H.T @ Rinv @ H
    eta = H.T @ Rinv @ z
    return GaussianFactor(scope=(var,), dim=H.shape[1], Lambda=Lambda, eta=eta)


def combine(factors: list[GaussianFactor]) -> GaussianFactor:
    """
    Merge factors into a single joint over the union of their scopes, in
    first-seen order, by summing their blocks at the rows each variable
    occupies in the joint.
    """
    if not factors:
        raise ValueError("combine() requires at least one factor")

    dim = factors[0].dim
    if any(factor.dim != dim for factor in factors):
        raise ValueError("combine() requires every factor to use the same variable dimension")

    scope: list[str] = []
    for factor in factors:
        for var in factor.scope:
            if var not in scope:
                scope.append(var)

    n = len(scope) * dim
    joint = GaussianFactor(
        scope=tuple(scope),
        dim=dim,
        Lambda=np.zeros((n, n), dtype=np.float64),
        eta=np.zeros((n, 1), dtype=np.float64),
    )

    for factor in factors:
        idx = joint.indices_for(*factor.scope)
        joint.Lambda[np.ix_(idx, idx)] += factor.Lambda
        joint.eta[idx] += factor.eta

    return joint


def motion_factor(F: np.ndarray, Q: np.ndarray, u: np.ndarray, var_prev: str, var_curr: str) -> GaussianFactor:
    """
    Build the joint factor over (`var_prev`, `var_curr`) for the conditional
        x_curr | x_prev ~ N(F @ x_prev + u, Q).

    Note:
        The result has scope (`var_prev`, `var_curr`), so its `Lambda` is
        `2 * dim` wide with `var_prev` leading. Its `dim` is still the size of
        one variable, not the width of `Lambda`.

    Parameters:
        `F`: Transition matrix.
        `Q`: Process noise covariance.
        `u`: Control displacement over the step.
        `var_prev`: Variable before the step.
        `var_curr`: Variable after the step.

    Returns:
        A factor over both variables.
    """
    raise NotImplementedError


def eliminate(joint: GaussianFactor, var: str) -> GaussianFactor:
    """
    Marginalize `var` out of `joint` via the Schur complement.

    Note:
        `joint.indices_for` gives you the eliminated and surviving blocks,
        with the latter in their original scope order.

    Parameters:
        `joint`: Factor to marginalize.
        `var`: Variable to remove.

    Returns:
        A factor over `joint.scope` without `var`.
    """
    raise NotImplementedError


_PREVIOUS = "x_prev"
_CURRENT = "x_curr"


def _relabel(factor: GaussianFactor, var: str) -> GaussianFactor:
    """
    Rename the single variable a factor is defined over. Prediction needs the
    incoming and outgoing beliefs to be distinct graph variables even though
    both describe the agent's position, one time step apart.
    """
    return replace(factor, scope=(var,))


class FactorGraphFilter2D:
    """
    Constant-velocity 2D filter exposing the same interface as `KalmanFilter2D`,
    implemented by building a small factor graph each step and eliminating it.

    Parameters:
        `process_noise_stddev`: Standard deviation of unexpected acceleration.
    """

    def __init__(self, process_noise_stddev: float):
        self.process_noise_stddev = process_noise_stddev

        # Measurement and transition matrices
        self.H = np.eye(2, dtype=np.float64)
        self.F = np.eye(2, dtype=np.float64)

        self.belief = prior_factor(
            np.zeros((2, 1), dtype=np.float64),
            np.eye(2, dtype=np.float64) * 1e4,
            _CURRENT,
        )

    @property
    def x(self) -> np.ndarray:
        mean, _ = to_moment(self.belief)
        return mean

    @property
    def P(self) -> np.ndarray:
        _, cov = to_moment(self.belief)
        return cov

    @property
    def position(self) -> tuple[float, float]:
        mean, _ = to_moment(self.belief)
        return float(mean[0, 0]), float(mean[1, 0])

    @property
    def variance(self) -> tuple[float, float]:
        _, cov = to_moment(self.belief)
        return float(cov[0, 0]), float(cov[1, 1])

    def initialize(self, initial_position: Position, position_stddev: float):
        """
        Replace the belief with a prior factor at `initial_position`.

        Parameters:
            `initial_position`: Initial position.
            `position_stddev`: Standard deviation of the initial estimate.
        """
        mean = np.array(initial_position, dtype=np.float64).reshape(2, 1)
        cov = position_stddev**2 * np.eye(2, dtype=np.float64)
        self.belief = prior_factor(mean, cov, _CURRENT)

    def predict(self, dt: float, control_input: Velocity):
        """
        Advance the belief by joining it to a motion factor and marginalizing
        out the previous position.

        Parameters:
            `dt`: Time step in seconds.
            `control_input`: Commanded velocity.
        """
        joint = combine([
            _relabel(self.belief, _PREVIOUS),
            motion_factor(
                self.F,
                process_noise(dt, self.process_noise_stddev),
                control_vector(dt, control_input),
                _PREVIOUS,
                _CURRENT,
            ),
        ])
        self.belief = eliminate(joint, _PREVIOUS)

    def update(self, position_measurement: Position, position_stddev: float):
        """
        Correct the belief using a new position measurement.

        Parameters:
            `position_measurement`: Noisy measured position.
            `position_stddev`: Standard deviation of the measurement noise.
        """
        z = np.array(position_measurement, dtype=np.float64).reshape(2, 1)
        self.belief = combine([
            self.belief,
            measurement_factor(
                self.H,
                measurement_noise(position_stddev),
                z,
                _CURRENT,
            ),
        ])
