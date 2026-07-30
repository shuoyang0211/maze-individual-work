"""
A minimal Gaussian factor graph library.

Each `GaussianFactor` represents a potential over one or more variables in
*canonical* (a.k.a. information) form:

    factor(x) ∝ exp(-1/2 x^T Lambda x + eta^T x)

Canonical form is convenient here for two reasons:
  - Combining factors that share variables is just summing their (padded)
    Lambda/eta blocks.
  - Eliminating (marginalizing out) a variable is a Schur complement.

This mirrors exactly what your `KalmanFilter2D.predict`/`update` already do
under the hood: a factor graph over `x_prev` (prior belief) and `x_curr`
(motion + measurement) collapses, via elimination, to the same recursive
filtering equations.
"""

from dataclasses import dataclass

import numpy as np


@dataclass
class GaussianFactor:
    scope: tuple[str, ...]
    Lambda: np.ndarray
    eta: np.ndarray


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
    return GaussianFactor(scope=(var,), Lambda=Lambda, eta=eta)


def measurement_factor(H: np.ndarray, R: np.ndarray, z: np.ndarray, var: str) -> GaussianFactor:
    """
    Canonical form of the Gaussian likelihood N(z; H @ x, R) as a factor
    over `x`, using the same H, R your `KalmanFilter2D.update` uses.
    """
    Rinv = np.linalg.inv(R)
    Lambda = H.T @ Rinv @ H
    eta = H.T @ Rinv @ z
    return GaussianFactor(scope=(var,), Lambda=Lambda, eta=eta)


def _block_size(n_vars: int, dim_per_var: int) -> int:
    return n_vars * dim_per_var


def combine(factors: list[GaussianFactor]) -> GaussianFactor:
    """
    Merge multiple factors into a single joint canonical factor over the
    union of their scopes, by embedding each factor's Lambda/eta blocks
    into the joint (via per-variable index maps) and summing.
    """
    scope: list[str] = []
    for factor in factors:
        for var in factor.scope:
            if var not in scope:
                scope.append(var)
    scope = tuple(scope)

    dim_per_var = factors[0].Lambda.shape[0] // len(factors[0].scope)
    n = _block_size(len(scope), dim_per_var)
    Lambda = np.zeros((n, n), dtype=np.float64)
    eta = np.zeros((n, 1), dtype=np.float64)

    offsets = {var: i * dim_per_var for i, var in enumerate(scope)}

    for factor in factors:
        idx = []
        for var in factor.scope:
            start = offsets[var]
            idx.extend(range(start, start + dim_per_var))
        idx = np.array(idx)
        Lambda[np.ix_(idx, idx)] += factor.Lambda
        eta[idx] += factor.eta

    return GaussianFactor(scope=scope, Lambda=Lambda, eta=eta)


def motion_factor(F: np.ndarray, Q: np.ndarray, u: np.ndarray, var_prev: str, var_curr: str) -> GaussianFactor:
    """
    Build the joint canonical factor over (var_prev, var_curr) for the
    linear-Gaussian conditional x_curr | x_prev ~ N(F @ x_prev + u, Q),
    i.e. the same motion model used in `KalmanFilter2D.predict`.
    """
    raise NotImplementedError


def eliminate(joint: GaussianFactor, var: str) -> GaussianFactor:
    """
    Marginalize `var` out of `joint` via the Schur complement, returning
    the resulting factor over the remaining variables.
    """
    raise NotImplementedError
