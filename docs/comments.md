<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Comments

| [`GGConfig`](#ggconfig) | [`AgentConfig`](#agentconfig) | [`GobletConfig`](#gobletconfig) | [`WorldGenerationConfig`](#worldgenerationconfig) | [`GameState`](#gamestate) | [`Board`](#board) | [`Goblet`](#goblet) | [`Action`](#action) | [`GhostPolicy`](#ghostpolicy) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |

<br>

This file contains documentation for a subset of the classes and methods defined in `gg_core`.

## `GGConfig`

```python
class GGConfig:
    r"""
    Represents the entire configuration of the game.
    """

    @property
    def agent(self) -> AgentConfig:
    
    @property
    def goblets(self) -> GobletConfig:
    
    @property
    def world_generation(self) -> WorldGenerationConfig:
```

## `AgentConfig`

```python
class AgentConfig:
    r"""
    Stores the configuration of the agent and the ghost, if there is one.
    """

    @property
    def name(self) -> str:
        r"""
        Returns the name of the agent.
        """
    
    @property
    def ghost_policy(self) -> GhostPolicy | None:
        r"""
        Returns the ghost's policy, if there is one.
        """
    
    @property
    def ghost_penalty(self) -> builtins.int:
        r"""
        Returns the reward applied when the ghost catches the agent.
        """

    @property
    def ghost_occlusion(self) -> bool:
        r"""
        When true, a ghost hidden behind a wall (i.e., with no line of sight
        from the agent) is not observed for policy look-up purposes. Defaults
        to false. Invalid or hypothetical states where the ghost is inside a
        wall are also treated as hidden.
        """
    
    @property
    def transition(self) -> list[float]:
        r"""
        Returns the probabilities that the agent's actual action are
        [intended, right, back, left]. Entries must be nonnegative and sum to 1.
        """
```

## `GobletConfig`

```python
class GobletConfig:
    r"""
    Stores the configuration of all goblets.
    """

    @property
    def number(self) -> int:
        r"""
        Returns the initial number of goblets.
        """

    @property
    def max_reward(self) -> int:
        r"""
        Returns the maximum reward of any goblet.
        """
```

## `WorldGenerationConfig`

```python
class WorldGenerationConfig:
    r"""
    Stores the configuration of the gridworld.
    """
    
    @property
    def num_obstacles(self) -> int:
        r"""
        Returns the initial number of obstacles.
        """

    @property
    def obstacle_radius_cells(self) -> int:
        r"""
        Returns the maximum radius of an obstacle in number of cells.
        """

    @property
    def size(self) -> tuple[int, int]:
        r"""
        Returns the size of the world as a (width, height) tuple.
        """
```

## `GameState`

```python
class GameState:
    r"""
    Represents the game state and holds the bulk of the game logic.
    """

    @property
    def board(self) -> Board:
        r"""
        Returns the state of the board.
        """

    @property
    def reward(self) -> int:
        r"""
        Represents the immediate reward of the current state. Equals the
        configured ghost penalty if the agent has been caught by the ghost,
        the value of a goblet if the agent has found a goblet, and zero
        otherwise.
        """

    @property
    def done(self) -> bool:
        r"""
        Returns True if the agent has collected a goblet or has been caught
        by the ghost.
        """

    @property
    def agent_position(self) -> tuple[int, int]:
        r"""
        Returns the current position of the agent.
        """
    
    @property
    def observed_ghost_position(self) -> tuple[int, int] | None:
        r"""
        Returns the position of the ghost as observed by the agent. If there is
        no ghost, or if the ghost isn't currently visible (e.g., behind a wall)
        when `ghost_occlusion` is enabled, returns None. Invalid states (e.g.,
        where the ghost is inside a wall) are also treated as hidden.
        """

    @property
    def visible_goblet_positions(self) -> list[tuple[int, int]]:
        r"""
        Returns the positions of goblets visible from the agent's current
        position. Goblets hidden behind walls are omitted.
        """
    
    @property
    def visible_wall_positions(self) -> list[tuple[int, int]]:
        r"""
        Returns the positions of walls visible from the agent's current
        position. A wall is visible if no other wall lies between the agent
        and that wall.
        """

    @property
    def episode_seed(self) -> int:
        r"""
        Returns the episode seed driving this state's RNG.
        """

    def all_states(self) -> list[GameState]:
        r"""
        Returns a list of `width * height` game states where the agent's
        position is varied across all cells. Note that invalid states are not
        filtered out.
        """

    def next_state(self, action: Action) -> GameState:
        r"""
        Returns the game state that would result from the agent moving in the
        given direction. This move is deterministic, and does not update the
        ghost's position.
        """

    def step(self, action: Action) -> GameState:
        r"""
        Returns a new game state resulting from one full environment step.
        This step is not deterministic, and updates both the agent and the
        ghost's position using the episode seed. Fails for the Teleop ghost.
        """
    
    def with_seed(self, seed: int) -> GameState:
        r"""
        Returns a copy of the current game state with a fixed episode seed,
        used to determine the actions taken by the agent and the ghost.
        """

    def reset(self, seed: int | None = None) -> tuple[GameState, int]:
        r"""
        Returns a new game state set to the original configuration, along with
        the episode seed it uses. When `seed` is None, a fresh seed is sampled.
        """
```

## `Board`

```python
class Board:
    r"""
    Represents the state of the board.
    Stores the dimensions and board layout.
    """

    @property
    def width(self) -> int:

    @property
    def height(self) -> int:

    @property
    def agent_position(self) -> tuple[int, int]:

    @property
    def ghost_position(self) -> tuple[int, int] | None:

    @property
    def goblets(self) -> list[Goblet]:

    @property
    def wall_positions(self) -> set[tuple[int, int]]:
```

## `Goblet`

```python
class Goblet:
    r"""
    Represents the state of a single goblet.
    """

    @property
    def position(self) -> tuple[int, int]:

    @property
    def reward(self) -> int:
```

## `Action`

```python
class Action:
    r"""
    Represents an agent action.
    """
    Up = ...
    Down = ...
    Left = ...
    Right = ...
```

## `GhostPolicy`

```python
class GhostPolicy:
    r"""
    Represents a policy for the ghost.
    """
    Random = ...
    Chaser = ...
    Teleop = ...
```

<br>

---

| [`Back to top`](#comments) |
| :---: |
