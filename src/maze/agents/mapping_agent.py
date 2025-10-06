from maze_core import Action, GameState, OccupancyGrid

class MappingAgent:
    def __init__(self) -> None:
        self._name = "Mapping Agent"

    @property
    def name(self) -> str:
        return self._name

    def get_action(self, game_state: GameState, occupancy_grid: OccupancyGrid) -> Action:
        raise NotImplementedError("")