from maze_core import Action, GameState, OccupancyGrid, Position

from maze.kalman_filter import KalmanFilter2D


class LocalizationAgent:
    def __init__(self):
        self._name = "Localization Agent"

    @property
    def name(self) -> str:
        return self._name

    @property
    def estimated_position(self) -> Position:
        raise NotImplementedError

    def get_action(self, game_state: GameState, occupancy_grid: OccupancyGrid, dt: float) -> Action:
        raise NotImplementedError
