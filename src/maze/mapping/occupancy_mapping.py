from maze_core import (
    OccupancyGrid,
    OccupancyGridCell,
    Position,
    Raycast,
    SensorConfidence,
)

from maze.mapping.utils import line_between


def update_cell(
    cell: OccupancyGridCell,
    confidence: SensorConfidence,
    log_odds_scale: float,
    assign_threshold: float,
):
    """
    Update an occupancy grid cell in place from one observation.

    Note:
        The cell's logits should be updated by adding the log-likelihood
        computed from the sensor confidence, scaled by `log_odds_scale`.
        The log-likelihoods should be centered before adding, since the logits
        are clipped to a fixed range around zero. The cell's assignment
        should be updated once the most likely class's probability crosses
        `assign_threshold`, and reset if no such class satisfies this.

    Parameters:
        `cell`: Mutable occupancy grid cell.
        `confidence`: Per-class confidences from the sensor.
        `log_odds_scale`: Scale factor for new log-likelihoods.
        `assign_threshold`: Probability a class must reach to be assigned.
    """
    raise NotImplementedError


def update_grid(
    grid: OccupancyGrid,
    raycasts: list[Raycast],
    position: Position,
    log_odds_scale: float,
    assign_threshold: float,
):
    """
    Update the occupancy grid in place from a list of range sensor readings.

    Note:
        The list of cells to update can be computed using `line_between` on the
        cell at the source position and the end of the raycast, which can be
        inferred from `theta` and `distance`. If the ray hits an object early
        (i.e., when `endpoint_type` is not `Free`), the last cell is observed
        with `endpoint_confidence`, and remaining cells are observed with
        `path_confidence`.

    Parameters:
        `grid`: Mutable occupancy grid.
        `raycasts`: List of range sensor readings.
        `position`: Source position.
        `log_odds_scale`: Scale factor for new log-likelihoods.
        `assign_threshold`: Probability a class must reach to be assigned.
    """
    raise NotImplementedError
