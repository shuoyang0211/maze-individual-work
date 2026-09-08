<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Comments

| [`GameState`](#gamestate) | [`AgentState`](#agentstate) | [`Raycast`](#raycast) | [`SensorConfidence`](#sensorconfidence) | [`OccupancyGrid`](#occupancygrid) | [`OccupancyGridCell`](#occupancygridcell) | [`Action`](#action) | [`EntityType`](#entitytype) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |

<br>

This file contains documentation for a subset of the classes defined in `maze_core`.

## `GameState`

```python
class GameState:
    r"""
    Represents a snapshot of the game state.
    """

    @property
    def agent(self) -> AgentState:
        r"""
        Returns the state of the agent.
        """

    @property
    def total_flags(self) -> int:
        r"""
        Returns the total number of flags.
        """

    @property
    def captured_flags(self) -> int:
        r"""
        Returns the number of flags delivered to capture points.
        """

    @property
    def world_width(self) -> float:
        r"""
        Returns the width of the maze in world units.
        """

    @property
    def world_height(self) -> float:
        r"""
        Returns the height of the maze in world units.
        """
```

## `AgentState`

```python
class AgentState:
    r"""
    Represents the state of the agent, including its observed information.
    """

    @property
    def position(self) -> tuple[float, float]:
        r"""
        Returns the observed position, including position noise.
        """

    @property
    def position_stddev(self) -> float:
        r"""
        Returns the standard deviation of position observations.
        """

    @property
    def range_stddev(self) -> float:
        r"""
        Returns the standard deviation of the noise on each raycast distance.
        """

    @property
    def raycasts(self) -> list[Raycast]:
        r"""
        Returns the range-sensor readings, in increasing order of `theta`.
        """

    @property
    def carrying_flag(self) -> bool:
        r"""
        Returns whether the agent is currently carrying a flag.
        """

    @property
    def max_speed(self) -> float:
        r"""
        Returns the maximum linear speed of the agent.
        """
```

## `Raycast`

```python
class Raycast:
    r"""
    Represents one range-sensor reading from the agent's current position.
    """

    @property
    def theta(self) -> float:
        r"""
        Returns the ray angle in radians, measured from `+x` towards `+y`.
        """

    @property
    def endpoint_type(self) -> EntityType:
        r"""
        Returns the type observed at the raycast endpoint. Equals `Free` if
        no collision occurs before the endpoint.
        """

    @property
    def distance(self) -> float:
        r"""
        Returns the reported distance, including range noise for hits.
        """

    @property
    def max_distance(self) -> float:
        r"""
        Returns the maximum distance the raycast can travel.
        """

    @property
    def endpoint_confidence(self) -> SensorConfidence:
        r"""
        Returns the per-class confidence at the endpoint.
        """

    @property
    def path_confidence(self) -> SensorConfidence:
        r"""
        Returns the per-class confidence for cells before the endpoint.
        """
```

## `SensorConfidence`

```python
class SensorConfidence:
    r"""
    Represents per-class sensor confidence used to update an occupancy grid.
    Note that these are not normalized probabilities.
    """

    @property
    def conf_free(self) -> float:
        r"""
        Returns the confidence in a free space.
        """

    @property
    def conf_wall(self) -> float:
        r"""
        Returns the confidence in a wall.
        """

    @property
    def conf_flag(self) -> float:
        r"""
        Returns the confidence in a flag.
        """

    @property
    def conf_capture_point(self) -> float:
        r"""
        Returns the confidence in a capture point.
        """

    def as_tuple(self) -> tuple[float, float, float, float]:
        r"""
        Returns `(conf_free, conf_wall, conf_flag, conf_capture_point)`.
        """
```

## `OccupancyGrid`

```python
class OccupancyGrid:
    r"""
    Represents a mutable occupancy grid, indexed by `grid[column, row]`.
    """

    @property
    def cell_size(self) -> float:
        r"""
        Returns the edge length of each cell.
        """

    @property
    def columns(self) -> int:
        r"""
        Returns the number of columns.
        """

    @property
    def rows(self) -> int:
        r"""
        Returns the number of rows.
        """

    @property
    def shape(self) -> tuple[int, int]:
        r"""
        Returns `(columns, rows)`.
        """

    def world_to_cell(self, x: float, y: float) -> tuple[int, int] | None:
        r"""
        Returns the `(column, row)` containing `(x, y)`, or `None` if outside grid.
        """

    def cell_to_world(self, column: int, row: int) -> tuple[float, float] | None:
        r"""
        Returns the center of cell `(column, row)`, or `None` if outside grid.
        """
```

## `OccupancyGridCell`

```python
class OccupancyGridCell:
    r"""
    Represents a mutable occupancy-grid cell.
    """

    @property
    def assignment(self) -> EntityType | None:
        r"""
        Mutable cell type assignment. Must be updated manually.
        """

    @property
    def logit_free(self) -> float:
        r"""
        Mutable logit for free space. Clamps to `±6`.
        """

    @property
    def logit_wall(self) -> float:
        r"""
        Mutable logit for a wall. Clamps to `±6`.
        """

    @property
    def logit_flag(self) -> float:
        r"""
        Mutable logit for a flag. Clamps to `±6`.
        """

    @property
    def logit_capture_point(self) -> float:
        r"""
        Mutable logit for a capture point. Clamps to `±6`.
        """

    def probabilities(self) -> tuple[float, float, float, float]:
        r"""
        Returns softmax probabilities `(free, wall, flag, capture_point)`.
        """
```

## `Action`

```python
class Action:
    r"""An action returned by an agent policy."""

    class Move(Action):
        r"""
        Sets the `velocity`, capped to `max_speed`, until the next `Move`.
        """

        @property
        def velocity(self) -> tuple[float, float]: ...

    class PickupFlag(Action):
        r"""
        Picks up a flag, if one is on the ground within reach.
        """

    class DropFlag(Action):
        r"""
        Drops the flag the agent is carrying, capturing it if a capture point
        is within reach.
        """
```

## `EntityType`

```python
class EntityType(Enum):
    r"""
    Represents the type observed at the endpoint of a range-sensor reading.
    """
    Free = ...
    Wall = ...
    Flag = ...
    CapturePoint = ...
    Unknown = ...
```

<br>

---

| [`Back to top`](#comments) |
| :---: |
