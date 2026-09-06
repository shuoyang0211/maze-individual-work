import numpy as np

from maze.justin_factor_graph import (
    combine,
    eliminate,
    measurement_factor,
    motion_factor,
    prior_factor,
    to_moment,
)
from maze.justin_kalman_filter import KalmanFilter2D


def test_factor_graph_elimination_matches_kalman_filter():
    """
    Runs a short synthetic trajectory through both `KalmanFilter2D` and the
    equivalent two-node factor graph (prior on x_prev, motion factor to
    x_curr, measurement factor on x_curr). Eliminating x_prev should exactly
    reproduce `predict()`, and folding in the measurement factor should
    exactly reproduce `update()`.
    """
    process_noise_stddev = 2.0
    position_stddev = 5.0
    measurement_stddev = 0.5
    dt = 0.1

    kf = KalmanFilter2D(process_noise_stddev=process_noise_stddev)
    kf.initialize((0.0, 0.0), position_stddev)

    prior_mean = np.array([[0.0], [0.0]])
    prior_cov = position_stddev ** 2 * np.eye(2)

    controls = [(1.0, 0.0), (0.5, 0.5), (-1.0, 2.0), (0.0, -1.0), (2.0, 2.0)]
    measurements = [(0.09, 0.02), (0.15, 0.12), (0.02, 0.32), (0.03, 0.22), (0.22, 0.42)]

    F = kf.F
    H = kf.H
    Q = (process_noise_stddev ** 2 * (dt ** 4) / 4.0) * np.eye(2)
    R = measurement_stddev ** 2 * np.eye(2)

    for velocity, measurement in zip(controls, measurements):
        u_dt = np.array(velocity, dtype=np.float64).reshape((2, 1)) * dt
        z = np.array(measurement, dtype=np.float64).reshape((2, 1))

        kf.predict(dt, velocity)
        kf_predicted_mean, kf_predicted_cov = kf.x.copy(), kf.P.copy()
        kf.update(measurement, measurement_stddev)
        kf_updated_mean, kf_updated_cov = kf.x.copy(), kf.P.copy()

        prior = prior_factor(prior_mean, prior_cov, "x_prev")
        motion = motion_factor(F, Q, u_dt, "x_prev", "x_curr")
        joint = combine([prior, motion])
        predictive = eliminate(joint, "x_prev")

        fg_predicted_mean, fg_predicted_cov = to_moment(predictive)
        assert np.allclose(fg_predicted_mean, kf_predicted_mean, atol=1e-6)
        assert np.allclose(fg_predicted_cov, kf_predicted_cov, atol=1e-6)

        measurement_potential = measurement_factor(H, R, z, "x_curr")
        posterior = combine([predictive, measurement_potential])
        fg_updated_mean, fg_updated_cov = to_moment(posterior)
        assert np.allclose(fg_updated_mean, kf_updated_mean, atol=1e-6)
        assert np.allclose(fg_updated_cov, kf_updated_cov, atol=1e-6)

        prior_mean, prior_cov = fg_updated_mean, fg_updated_cov
