from maze_core import (
    Action,
    GameState,
    OccupancyGrid,
    OccupancyGridCell,
    Position,
    SensorConfidence,
)


def update_occupancy_grid_entry(cell: OccupancyGridCell, confidence: SensorConfidence):
    """
    Updates the passed in occupancy grid entry in place using the passed in confidence.
    Sets the predicted assignment of the cell when the corresponding probability crosses a user-defined threshold.

    The logits in the occupancy grid entry should be updated using the log-likelihoods computed from the sensor confidence.
    These logits are automatically clipped to a reasonable range, however, to ensure the the logits don't always grow to
    the negative end of this range, you should center the log-likelihoods before modifying the logits.

    Parameters:
        cell (OccupancyGridCell): The occupancy grid entry to update.
        confidence (SensorConfidence): The confidence to use for the update.
    """
    raise NotImplementedError

class MappingAgent:
    def __init__(self) -> None:
        self._name = "Mapping Agent"
        self._position = (0.0, 0.0)

    @property
    def name(self) -> str:
        return self._name

    @property
    def estimated_position(self) -> Position:
        return self._position

    def update_occupancy_grid(self, game_state: GameState, occupancy_grid: OccupancyGrid):
        raise NotImplementedError

    def get_action(self, game_state: GameState, occupancy_grid: OccupancyGrid, dt: float) -> Action:
        self._position = game_state.agent.position
        raise NotImplementedError
