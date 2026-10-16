import collections
import heapq
import math

from maze_core import (
    Action,
    EntityType,
    GameState,
    OccupancyGrid,
    Position,
    Velocity,
)

from maze.state_estimation import KalmanFilter2D
import numpy as np


# Minimum safe distance from walls (in grid units); closer to the wall means higher cost
WALL_CLEARANCE = 3
# How many cells to look ahead along the path as the current waypoint
LOOKAHEAD_CELLS = 4
# Attempt to pickup/drop when estimated distance to target is less than this value (true radius is 3.0, leaving some margin)
ACTION_RADIUS = 2.0
# Number of frames to remain stationary before interaction: the motion model is accurate when stationary, and the filter will converge to the true position
SETTLE_TICKS = 90
# Exponential moving average coefficient and threshold for innovation (measurement - prediction): it should be close to 0 when the filter is unbiased (noise ~ ±3),
# consistently large values indicate an incorrect motion model (e.g., stuck on a wall but commanded velocity is non-zero)
INNOVATION_ALPHA = 0.05
INNOVATION_THRESHOLD = 10.0


class LocalizationAgent:
    def __init__(self):
        self._name = "Localization Agent"

        # [Critical Tuning] Process noise variance per step is stddev^2 * dt^4 / 4. When dt=1/60, dt^4 is extremely small,
        # so stddev needs to be very large. Too small -> filter becomes an unforgetting average, unable to correct deviations after hitting a wall;
        # Too large -> almost equals raw measurements (noise ±20). At ~2000, steady-state error is ~2.5, correction time ~1s.
        self.kf = KalmanFilter2D(process_noise_stddev=2000.0)

        self.initialized = False
        self.last_commanded_velocity: Velocity = (0.0, 0.0)

        # Distance field cache: recomputed only when the target changes (pickup/drop flag)
        self._dist: np.ndarray | None = None
        self._dist_key = None
        self._target_cells: list[tuple[int, int]] = []
        self._walls: np.ndarray | None = None
        self._settle_ticks = 0
        self._innovation = np.zeros(2)
        self._cell_size = 1.0

    @property
    def name(self) -> str:
        return self._name

    @property
    def estimated_position(self) -> Position:
        # Return default origin before receiving the first frame of data for initialization
        if not self.initialized:
            return (0.0, 0.0)
        return self.kf.position

    def get_action(self, game_state: GameState, occupancy_grid: OccupancyGrid, dt: float) -> Action:
        # ==========================================
        # 1. State estimation loop (Kalman Filter)
        # ==========================================
        if not self.initialized:
            self.kf.initialize(game_state.agent.position, game_state.agent.position_stddev)
            self.initialized = True
        else:
            prev_x = self.kf.x.copy()
            self.kf.predict(dt, self.last_commanded_velocity)
            self._block_by_walls(prev_x)
            self._check_innovation(game_state.agent.position)
            self.kf.update(game_state.agent.position, game_state.agent.position_stddev)

        my_pos = self.estimated_position

        # ==========================================
        # 2. Determine target, recompute distance field if necessary
        # ==========================================
        is_holding_flag = game_state.agent.carrying_flag
        target_entity = EntityType.CapturePoint if is_holding_flag else EntityType.Flag

        key = (is_holding_flag, game_state.captured_flags)
        if key != self._dist_key or self._dist is None:
            self._dist, self._target_cells = self._compute_distance_field(occupancy_grid, target_entity)
            self._dist_key = key

        dist = self._dist

        # Case A: No reachable target, wait in place
        if not self._target_cells:
            return self._move((0.0, 0.0))

        # ==========================================
        # 3. If close enough to the target, attempt to pickup / drop
        # ==========================================
        nearest_target = min(
            (occupancy_grid.cell_to_world(c, r) for c, r in self._target_cells),
            key=lambda p: math.hypot(p[0] - my_pos[0], p[1] - my_pos[1]),
        )
        if math.hypot(nearest_target[0] - my_pos[0], nearest_target[1] - my_pos[1]) < ACTION_RADIUS:
            # Stop and wait for the estimation to converge first; interact only if still within range after convergence, otherwise it will naturally replan
            if self._settle_ticks < SETTLE_TICKS:
                self._settle_ticks += 1
                return self._move((0.0, 0.0))
            self.last_commanded_velocity = (0.0, 0.0)
            return Action.DropFlag() if is_holding_flag else Action.PickupFlag()
        self._settle_ticks = 0

        # ==========================================
        # 4. Descend along the distance field, look ahead several cells as a waypoint
        # ==========================================
        cell = self._nearest_reachable_cell(occupancy_grid, dist, my_pos)
        if cell is None:
            return self._move((0.0, 0.0))

        cols, rows = dist.shape
        c, r = cell
        for _ in range(LOOKAHEAD_CELLS):
            best = (c, r)
            for dc, dr in ((0, -1), (0, 1), (-1, 0), (1, 0), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                nc, nr = c + dc, r + dr
                if 0 <= nc < cols and 0 <= nr < rows and dist[nc, nr] < dist[best]:
                    best = (nc, nr)
            if best == (c, r):
                break
            c, r = best

        waypoint = occupancy_grid.cell_to_world(c, r)
        if (c, r) == cell:
            # Already in the target cell: move directly towards the nearest target point
            waypoint = nearest_target

        dir_x = waypoint[0] - my_pos[0]
        dir_y = waypoint[1] - my_pos[1]
        norm = math.hypot(dir_x, dir_y)
        speed = game_state.agent.max_speed
        if norm < 1e-4:
            return self._move((0.0, 0.0))
        return self._move((dir_x / norm * speed, dir_y / norm * speed))

    def _check_innovation(self, measurement: Position):
        innovation = np.array(measurement) - self.kf.x[:, 0]
        self._innovation = (1 - INNOVATION_ALPHA) * self._innovation + INNOVATION_ALPHA * innovation
        if np.linalg.norm(self._innovation) > INNOVATION_THRESHOLD:
            self.kf.x[:, 0] += self._innovation
            self._innovation[:] = 0.0

    def _block_by_walls(self, prev_x: np.ndarray):
        if self._walls is None:
            return
        x, y = float(self.kf.x[0, 0]), float(self.kf.x[1, 0])
        px, py = float(prev_x[0, 0]), float(prev_x[1, 0])
        if not self._is_wall(x, y):
            return
        if not self._is_wall(x, py):
            self.kf.x[1, 0] = py
        elif not self._is_wall(px, y):
            self.kf.x[0, 0] = px
        else:
            self.kf.x[0, 0], self.kf.x[1, 0] = px, py

    def _is_wall(self, x: float, y: float) -> bool:
        cols, rows = self._walls.shape
        c = int(math.floor(x / self._cell_size + cols / 2))
        r = int(math.floor(y / self._cell_size + rows / 2))
        return not (0 <= c < cols and 0 <= r < rows) or bool(self._walls[c, r])

    def _move(self, velocity: Velocity) -> Action:
        # 保存速度供下一帧滤波器的 Predict 使用
        self.last_commanded_velocity = velocity
        return Action.Move(velocity)

    @staticmethod
    def _cell_types(occupancy_grid: OccupancyGrid) -> np.ndarray:
        codes = {EntityType.Free: 0, EntityType.Wall: 1, EntityType.Flag: 2, EntityType.CapturePoint: 3}
        cols, rows = occupancy_grid.shape
        types = np.zeros((cols, rows), dtype=np.int8)
        for c in range(cols):
            for r in range(rows):
                cell = occupancy_grid[c, r]
                if cell.assignment in codes:
                    types[c, r] = codes[cell.assignment]
                else:
                    logits = (cell.logit_free, cell.logit_wall, cell.logit_flag, cell.logit_capture_point)
                    types[c, r] = int(np.argmax(logits))
        return types

    def _compute_distance_field(
        self, occupancy_grid: OccupancyGrid, target_entity: EntityType
    ) -> tuple[np.ndarray, list[tuple[int, int]]]:
        types = self._cell_types(occupancy_grid)
        cols, rows = types.shape
        target_code = 2 if target_entity == EntityType.Flag else 3
        walls = types == 1
        self._walls = walls
        self._cell_size = occupancy_grid.cell_size

        wall_dist = np.full((cols, rows), np.inf)
        queue = collections.deque()
        for c, r in zip(*np.nonzero(walls)):
            wall_dist[c, r] = 0
            queue.append((c, r))
        while queue:
            c, r = queue.popleft()
            for dc, dr in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nc, nr = c + dc, r + dr
                if 0 <= nc < cols and 0 <= nr < rows and wall_dist[nc, nr] > wall_dist[c, r] + 1:
                    wall_dist[nc, nr] = wall_dist[c, r] + 1
                    queue.append((nc, nr))

        targets = [(int(c), int(r)) for c, r in zip(*np.nonzero(types == target_code))]
        dist = np.full((cols, rows), np.inf)
        heap = []
        for t in targets:
            dist[t] = 0.0
            heap.append((0.0, t[0], t[1]))
        heapq.heapify(heap)

        while heap:
            d, c, r = heapq.heappop(heap)
            if d > dist[c, r]:
                continue
            for dc, dr in ((0, -1), (0, 1), (-1, 0), (1, 0)):
                nc, nr = c + dc, r + dr
                if not (0 <= nc < cols and 0 <= nr < rows) or walls[nc, nr]:
                    continue
                penalty = max(0.0, WALL_CLEARANCE - wall_dist[nc, nr]) * 5.0
                nd = d + 1.0 + penalty
                if nd < dist[nc, nr]:
                    dist[nc, nr] = nd
                    heapq.heappush(heap, (nd, nc, nr))

        return dist, targets

    @staticmethod
    def _nearest_reachable_cell(
        occupancy_grid: OccupancyGrid, dist: np.ndarray, pos: Position
    ) -> tuple[int, int] | None:
        cols, rows = dist.shape
        c = min(max(int(math.floor(pos[0] / occupancy_grid.cell_size + cols / 2)), 0), cols - 1)
        r = min(max(int(math.floor(pos[1] / occupancy_grid.cell_size + rows / 2)), 0), rows - 1)
        if np.isfinite(dist[c, r]):
            return c, r
        best, best_d = None, math.inf
        for radius in range(1, 6):
            for nc in range(max(0, c - radius), min(cols, c + radius + 1)):
                for nr in range(max(0, r - radius), min(rows, r + radius + 1)):
                    if np.isfinite(dist[nc, nr]):
                        d = (nc - c) ** 2 + (nr - r) ** 2
                        if d < best_d:
                            best, best_d = (nc, nr), d
            if best is not None:
                return best
        return None

