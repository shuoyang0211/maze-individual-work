from maze_core import Action, GameState, OccupancyGrid

class LocalizationAgent:
    def __init__(self) -> None:
        self._name = "Localization Agent"

    @property
    def name(self) -> str:
        return self._name

    def get_action(self, game_state: GameState, occupancy_grid: OccupancyGrid) -> Action:
        raise NotImplementedError("")