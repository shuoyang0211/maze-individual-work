from maze_core import Action, GameState, OccupancyGrid, Position

from maze.mapping import update_grid
from maze.state_estimation import KalmanFilter2D


class SlamAgent:
    def __init__(self):
        self._name = "Slam Agent"

    @property
    def name(self) -> str:
        return self._name

    @property
    def estimated_position(self) -> Position:
        raise NotImplementedError

    def get_action(self, game_state: GameState, occupancy_grid: OccupancyGrid, dt: float) -> Action:
        raise NotImplementedError
