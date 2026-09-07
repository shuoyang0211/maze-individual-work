from maze_core import Action, GameState, OccupancyGrid, Position

from maze.occupancy_mapping import update_grid


class MappingAgent:
    def __init__(self):
        self._name = "Mapping Agent"

    @property
    def name(self) -> str:
        return self._name

    @property
    def estimated_position(self) -> Position:
        raise NotImplementedError

    def get_action(self, game_state: GameState, occupancy_grid: OccupancyGrid, dt: float) -> Action:
        self._position = game_state.agent.position
        raise NotImplementedError
