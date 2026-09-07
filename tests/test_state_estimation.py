import numpy as np

from maze.state_estimation import FactorGraphFilter2D, KalmanFilter2D

ACCELERATION_STDDEV = 100.0
INITIAL_POSITION_STDDEV = 5.0
MEASUREMENT_STDDEV = 0.5
DT = 0.1

CONTROLS = [(1.0, 0.0), (0.5, 0.5), (-1.0, 2.0), (0.0, -1.0), (2.0, 2.0)]
MEASUREMENTS = [(0.09, 0.02), (0.15, 0.12), (0.02, 0.32), (0.03, 0.22), (0.22, 0.42)]


def test_factor_graph_filter_matches_kalman_filter():
    """
    Runs a short synthetic trajectory through both `KalmanFilter2D` and
    `FactorGraphFilter2D`, which are two implementations of the same model.
    Eliminating `x_prev` from the two-node graph should reproduce `predict()`,
    and combining in the measurement factor should reproduce `update()`, so the
    two filters must agree on both the mean and the covariance at every step.
    """
    kalman = KalmanFilter2D(acceleration_stddev=ACCELERATION_STDDEV)
    factor_graph = FactorGraphFilter2D(acceleration_stddev=ACCELERATION_STDDEV)

    kalman.initialize((0.0, 0.0), INITIAL_POSITION_STDDEV)
    factor_graph.initialize((0.0, 0.0), INITIAL_POSITION_STDDEV)

    for step, (velocity, measurement) in enumerate(zip(CONTROLS, MEASUREMENTS)):
        kalman.predict(DT, velocity)
        factor_graph.predict(DT, velocity)
        assert np.allclose(factor_graph.x, kalman.x, atol=1e-6), (
            f"Predicted means disagree after {step + 1} step(s): "
            f"factor graph gave {factor_graph.x.ravel()}, Kalman filter gave {kalman.x.ravel()}."
        )
        assert np.allclose(factor_graph.P, kalman.P, atol=1e-6), (
            f"Predicted covariances disagree after {step + 1} step(s): "
            f"factor graph gave\n{factor_graph.P}\nKalman filter gave\n{kalman.P}"
        )

        kalman.update(measurement, MEASUREMENT_STDDEV)
        factor_graph.update(measurement, MEASUREMENT_STDDEV)
        assert np.allclose(factor_graph.x, kalman.x, atol=1e-6), (
            f"Updated means disagree after {step + 1} step(s): "
            f"factor graph gave {factor_graph.x.ravel()}, Kalman filter gave {kalman.x.ravel()}."
        )
        assert np.allclose(factor_graph.P, kalman.P, atol=1e-6), (
            f"Updated covariances disagree after {step + 1} step(s): "
            f"factor graph gave\n{factor_graph.P}\nKalman filter gave\n{kalman.P}"
        )
