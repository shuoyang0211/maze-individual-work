<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Comments

| [`GameState`](#gamestate) | [`AgentState`](#agentstate) | [`HitInfo`](#hitinfo) | [`SensorConfidence`](#sensorconfidence) | [`OccupancyGrid`](#occupancygrid) | [`OccupancyGridEntry`](#occupancygridentry) | [`Action`](#action) | [`EntityType`](#entitytype) |
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
```

## `AgentState`

```python
class AgentState:
    r"""
    Represents the state of the agent, including its observed information.
    """

    @property
    def id(self) -> int:
        r"""
        Returns the entity ID of the agent.
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
    def raycasts(self) -> list[HitInfo]:
        r"""
        Returns a list of range-sensor readings.
        """

    @property
    def flag_id(self) -> int | None:
        r"""
        Returns the ID of the flag carried, if any.
        """

    @property
    def max_speed(self) -> float:
        r"""
        Returns the maximum linear speed of the agent.
        """
```

## `HitInfo`

```python
class HitInfo:
    r"""
    Represents one range-sensor reading from the agent's current position.
    """

    @property
    def theta(self) -> float:
        r"""
        Returns the ray angle in radians clockwise from +x.
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
        Returns the reported distance, including range noise.
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
    def free_confidence(self) -> SensorConfidence:
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
```

## `OccupancyGridEntry`

```python
class OccupancyGridEntry:
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
        Mutable logit for free space.
        """

    @property
    def logit_wall(self) -> float:
        r"""
        Mutable logit for a wall.
        """

    @property
    def logit_flag(self) -> float:
        r"""
        Mutable logit for a flag.
        """

    @property
    def logit_capture_point(self) -> float:
        r"""
        Mutable logit for a capture point.
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
        Moves agent `agent_id` at `velocity`, capped to agent's max speed.

        Example: `Action.Move(agent_id, velocity)`.
        """

        @property
        def agent_id(self) -> int: ...

        @property
        def velocity(self) -> tuple[float, float]: ...

    class PickupFlag(Action):
        r"""
        Makes agent `agent_id` attempt to pick up a nearby flag.

        Example: `Action.PickupFlag(agent_id)`.
        """

        @property
        def agent_id(self) -> int: ...

    class DropFlag(Action):
        r"""
        Makes agent `agent_id` attempt to drop its flag at a capture point.

        Example: `Action.DropFlag(agent_id)`.
        """

        @property
        def agent_id(self) -> int: ...
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
