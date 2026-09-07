"""
A minimal Gaussian factor graph library, and a 2D filter built on top of it.

Each `GaussianFactor` represents a potential over one or more variables in
*canonical* (a.k.a. information) form:

    factor(x) ∝ exp(-1/2 x^T Lambda x + eta^T x)

Canonical form is convenient here for two reasons:
  - Combining factors that share variables is just summing their (padded)
    Lambda/eta blocks.
  - Eliminating (marginalizing out) a variable is a Schur complement.

`FactorGraphFilter2D`, at the bottom of this file, wires those two operations
into the same interface `KalmanFilter2D` exposes, over the same motion and
measurement model. One `predict` is a two-node graph over `x_prev` and
`x_curr` whose elimination of `x_prev` reproduces the Kalman prediction; one
`update` is a single `combine` with the measurement likelihood. Because both
filters are drop-in replacements for each other, `LocalizationAgent` can run
on either, and `tests/test_state_estimation.py` checks that they agree step
for step over a whole trajectory.
"""

from dataclasses import dataclass, replace

import numpy as np
from maze_core import Position, Velocity

from maze.kalman_filter import (
    control_vector,
    measurement_matrix,
    measurement_noise,
    process_noise,
    transition_matrix,
)


@dataclass
class GaussianFactor:
    """
    A Gaussian potential in canonical form over the variables in `scope`, each
    of which has `dim` components.

    `Lambda` and `eta` are laid out in scope order: variable `scope[i]` owns
    rows (and columns) `i * dim` through `(i + 1) * dim`. Every function in
    this module relies on that convention, so use `indices_for` to address a
    variable's block rather than recomputing offsets.
    """

    scope: tuple[str, ...]
    dim: int
    Lambda: np.ndarray
    eta: np.ndarray

    def indices_for(self, *variables: str) -> np.ndarray:
        """
        Return the row/column indices that `variables` occupy in this factor's
        `Lambda` and `eta`, concatenated in the order given. Pair with
        `np.ix_(idx, idx)` to slice a square block out of `Lambda`.
        """
        blocks = [
            np.arange(self.scope.index(var) * self.dim, (self.scope.index(var) + 1) * self.dim)
            for var in variables
        ]
        return np.concatenate(blocks) if blocks else np.zeros(0, dtype=np.intp)


def to_moment(factor: GaussianFactor) -> tuple[np.ndarray, np.ndarray]:
    """
    Convert a canonical-form factor over a single variable back to
    (mean, covariance) so it can be compared against the Kalman Filter's
    (x, P).
    """
    Sigma = np.linalg.inv(factor.Lambda)
    mu = Sigma @ factor.eta
    return mu, Sigma


def prior_factor(mean: np.ndarray, cov: np.ndarray, var: str) -> GaussianFactor:
    """Canonical form of a Gaussian prior N(mean, cov) over a single variable."""
    Lambda = np.linalg.inv(cov)
    eta = Lambda @ mean
    return GaussianFactor(scope=(var,), dim=mean.shape[0], Lambda=Lambda, eta=eta)


def measurement_factor(H: np.ndarray, R: np.ndarray, z: np.ndarray, var: str) -> GaussianFactor:
    """
    Canonical form of the Gaussian likelihood N(z; H @ x, R) as a factor
    over `x`, using the same H, R your `KalmanFilter2D.update` uses.
    """
    Rinv = np.linalg.inv(R)
    Lambda = H.T @ Rinv @ H
    eta = H.T @ Rinv @ z
    return GaussianFactor(scope=(var,), dim=H.shape[1], Lambda=Lambda, eta=eta)


def combine(factors: list[GaussianFactor]) -> GaussianFactor:
    """
    Merge multiple factors into a single joint canonical factor over the union
    of their scopes, by adding each factor's Lambda/eta blocks into the joint
    at the rows its variables occupy there.
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
    Build the joint canonical factor over (var_prev, var_curr) for the
    linear-Gaussian conditional x_curr | x_prev ~ N(F @ x_prev + u, Q),
    i.e. the same motion model used in `KalmanFilter2D.predict`.

    The returned factor has scope `(var_prev, var_curr)`, so its `Lambda` is
    2 * dim wide with `var_prev` occupying the leading block.
    """
    raise NotImplementedError


def eliminate(joint: GaussianFactor, var: str) -> GaussianFactor:
    """
    Marginalize `var` out of `joint` via the Schur complement, returning
    the resulting factor over the remaining variables.

    `joint.indices_for` gives you the eliminated block and the surviving
    blocks; the result keeps the surviving variables in their original scope
    order.
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
    Constant-velocity 2D filter exposing the same interface as
    `KalmanFilter2D`, implemented by building a small factor graph on every
    step and eliminating it.

    The belief is carried in canonical form rather than as (x, P). `predict`
    combines it with a motion factor and eliminates the previous time step;
    `update` combines it with a measurement factor, which in canonical form is
    just addition. Both use the model functions from `kalman_filter.py`, so any
    difference from `KalmanFilter2D` is a difference in your `motion_factor` or
    `eliminate`, not in the model.

    Parameters:
        - process_noise_stddev: Standard deviation of the acceleration noise (affects the process noise covariance Q)
    """

    def __init__(self, process_noise_stddev: float = 2.0):
        self.process_noise_stddev = process_noise_stddev
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
        return float(self.x[0, 0]), float(self.x[1, 0])

    @property
    def variance(self) -> tuple[float, float]:
        return float(self.P[0, 0]), float(self.P[1, 1])

    def initialize(self, initial_position: Position, position_stddev: float):
        """
        Replace the belief with a prior factor at the given position.

        Parameters:
            - initial_position: Tuple (x, y) representing the initial position.
            - position_stddev: Standard deviation of the initial position estimate.
        """
        mean = np.array(initial_position, dtype=np.float64).reshape(2, 1)
        cov = position_stddev**2 * np.eye(2, dtype=np.float64)
        self.belief = prior_factor(mean, cov, _CURRENT)

    def predict(self, dt: float, control_input: Velocity):
        """
        Advance the belief by one time step, by joining it to a motion factor
        and marginalizing out the previous position.

        Parameters:
            - dt: Time step in seconds.
            - control_input: Tuple (vx, vy) representing the commanded velocity.
        """
        joint = combine([
            _relabel(self.belief, _PREVIOUS),
            motion_factor(
                transition_matrix(),
                process_noise(dt, self.process_noise_stddev),
                control_vector(dt, control_input),
                _PREVIOUS,
                _CURRENT,
            ),
        ])
        self.belief = eliminate(joint, _PREVIOUS)

    def update(self, position_measurement: Position, position_stddev: float):
        """
        Fold a position measurement into the belief.

        Parameters:
            - position_measurement: Tuple (x, y) representing the measured position.
            - position_stddev: Standard deviation of the position measurement noise.
        """
        z = np.array(position_measurement, dtype=np.float64).reshape(2, 1)
        self.belief = combine([
            self.belief,
            measurement_factor(
                measurement_matrix(),
                measurement_noise(position_stddev),
                z,
                _CURRENT,
            ),
        ])
