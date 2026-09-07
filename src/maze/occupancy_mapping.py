from maze_core import (
    OccupancyGrid,
    OccupancyGridCell,
    Position,
    Raycast,
    SensorConfidence,
)

from maze.utils import line_between

ASSIGN_THRESHOLD = 0.5
LOG_ODDS_SCALE = 1.0


def update_cell(cell: OccupancyGridCell, confidence: SensorConfidence):
    """
    Updates logits for an occupancy grid cell in place, and sets the predicted
    assignment once a class's probability crosses `ASSIGN_THRESHOLD`.

    The cell's logits should be updated by adding the log-likelihoods computed
    from the sensor confidence, scaled by `LOG_ODDS_SCALE`. The log-likelihoods
    should be centered before adding, since the logits are clipped to a fixed
    range around zero.

    Parameters:
        `cell`: Occupancy grid cell.
        `confidence`: Per-class confidences from sensor.
    """
    raise NotImplementedError


def update_grid(grid: OccupancyGrid, raycasts: list[Raycast], position: Position):
    """
    Update the occupancy grid in place from a list of range sensor readings.

    The list of cells to update can be computed using `line_between` on the
    cell at the source position and the end of the raycast. If the ray hits an object, the last cell should be updated via `endpoint_confidence`.
    Remaining cells along the ray should be updated via `path_confidence`.

    Parameters:
        `grid`: A mutable occupancy grid.
        `raycasts`: A list of range sensor readings.
        `position`: Source position.
    """
    raise NotImplementedError
