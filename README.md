# CS182 Individual Programming Assignment 3: Maze

Welcome back to the CS182 Arcade! Over the course of the semester we'll be taking a deeper dive into many of the topics covered in lecture through the individual and programming assignments. In particular, we will focus on how to apply the knowledge you've learned in class for agent planning and learning in games.

For this series of assignments, we’re now exploring _perception_, one of the fundamental challenges in robotics. In this programming assignment you will implement two key perception modules: localization and mapping within the Capture the Flag environment from the previous assignment.

As always, we highly recommend reading through the entire assignment and the stencil code before beginning with any parts of the assignment.

## Game

In the individual and group assignments, you will once again be playing Capture the Flag in a _continuous_ world. However, unlike the previous programming assignment, your agent no longer has access to perfect information about the environment. Instead, it must learn to _perceive_ its surroundings through noisy sensor data.

The goal of this assignment is to give your agent the ability to:

-   Build and maintain a map of the world through ray-based observations, and
-   Estimate its own position within that map using a simple Kalman Filter.

### World Structure

The world remains a rectangular arena enclosed by walls with capture points and flags. The environment exposes limited information through _raycasts_ that simulate a range sensor (think LIDAR). These are raycasts are equally spaced around the agent moving clockwise from the +x axis (pointing to the right of the screen). Just like assignment 2, the origin is placed in the center of the world with +x pointing to the right of the screen and +y pointing down.

At each time step, the agent receives a `GameState` that provides:

-   Noisy ray-based distance measurements to nearby objects,
-   Its noisy current position and velocity estimates,

You will maintain an _occupancy grid_, where each cell stores a logit of being occupied. Over time, your agent should refine this grid into an accurate map of explored areas. The occupancy grid is a discrete 2D array that is can be indexed by `(col_index, row_index)` where `0 <= col_index < width` and `0 <= row_index < height`. The cell at `(0, 0)` is in the upper left corner.

<div align="center">
    <img src="docs/maze.png" alt="world" width="500"/>
</div>

## Code Structure

This repository contains two major directories of interest: `src` and `configs`:

### `src/maze/agents`

This is where your work lives! There are three agents provided in this stencil:

-   `TeleopAgent`: A simple manually controlled agent that maps keyboard inputs to actions.
-   `MappingAgent`: An agent that updates an occupancy grid using simulated raycasts. It will work under the assumption that all of its received position estimates are perfect.
-   `LocalizationAgent`: An agent that estimates its position using a 2D Kalman Filter. It will work under the assumption that the received map is perfect.

If you have any questions about what things do/how things work please feel free to post a question on [Ed](https://edstem.org/us/courses/82550/discussion)!

### `src/maze/factor_graph.py`

A small Gaussian factor graph library used in Task 2b to re-express your Kalman Filter as a factor graph and run variable elimination on it.

### `configs`

Configuration files define parameters such as which agent to run, number of rays, and world setup. The two of most interest for this assignment are:

-   `configs/mapping.yaml`
-   `configs/localization.yaml`

Please feel free to create copies and modify these files as you work through the assignment to make sure things are working as expected! In particular, you may want to change the seed to generate a new maze or play around with the noise standard deviations!

## Game Controls, API, and Occupancy Grid

### Game Controls

-   `W` / `A` / `S` / `D` — Move the agent.
-   `Space` — Pick up or drop a flag (must be within 3 units of the flag or capture point).
-   `O` — Toggle your agent's estimated occupancy grid.
-   `T` — Toggle the true occupancy grid.
-   `Esc` — Exit.

### API

Your agent's `get_action(game_state, occupancy_grid, dt)` receives a `GameState`. The key fields:

-   `game_state.agent.id` — the ID to pass when constructing an `Action`.
-   `game_state.agent.position` — noisy `(x, y)` position in world coordinates.
-   `game_state.agent.raycasts` — list of `HitInfo`, spaced clockwise from the +x axis.
-   `game_state.agent.flag` — entity ID of the carried flag, or `None`.

Each `HitInfo` provides:

-   `theta` — ray angle in radians (+y points **down**).
-   `hit` — one of `Wall`, `Empty`, `Flag`, `CapturePoint`.
-   `distance` — distance to the hit (or `max_distance` if nothing was hit).
-   `hit_confidence` / `free_confidence` — per-class `SensorConfidence` (`p_free`, `p_wall`, `p_flag`, `p_capture_point`) for the hit cell and for cells the ray passed through.

Return one of:

-   `Action.Move(id=..., velocity=(vx, vy))`
-   `Action.PickupFlag(id=...)`
-   `Action.DropFlag(id=...)`

### Occupancy Grid

`OccupancyGrid` is indexed as `occupancy_grid[col, row]` with `(0, 0)` in the upper-left. Use `.width`, `.height`, and `.cell_size` for the layout.

Each cell (`OccupancyGridEntry`) stores four per-class logits (clamped to $[-L, L]$):

-   `logit_free`, `logit_wall`, `logit_flag`, `logit_capture_point` — read/write; higher means more likely.
-   `probabilities()` — softmax over the logits.
-   `assignment: EntityType | None` — the cell's predicted class. **You must set this yourself** (e.g. once one probability crosses a threshold); it is not derived from the logits automatically.

## Tasks

For the individual portion of this assignment, we'll be tackling SLAM by looking at its two constituent parts separately: the localization problem and the mapping problem. By the end of this assignment, you should have agents that are individually able to map their environment and localize themselves within that map.

The first task will focus on mapping, where your agent will use simulated range measurements to incrementally build a 2D occupancy grid representing the world.

The second task will focus on localization, where your agent will maintain an estimate of its own position within that map using a simple 2D Kalman Filter (found in `src/maze/kalman_filter.py`). A follow-up piece (Task 2b) will have you re-express that same Kalman Filter as a small factor graph and implement variable elimination on it, to see firsthand that these are two views of the same underlying idea.

Together, these components form the foundation for autonomous perception to enable your agent to navigate a partially unknown world using uncertain sensor data.

### Task 1: Mapping

In `src/maze/agents/mapping_agent.py`, you will implement an agent that constructs a map of the environment by updating an occupancy grid using simulated sensor readings. Use the raycasts provided by the `GameState` to update the passed-in `OccupancyGrid` within the `get_action` method. Each grid cell should keep track of a logit corresponding to which class the cell is supposed to represent.

After sufficient exploration, your occupancy grid should somewhat resemble the ground truth map. You can toggle your occupancy grid and the true occupancy grid on and off using the `O` and `T` keys on your keyboard. Hovering over these grids will give you debug information about hovered cell.

#### Implementation Steps

Let's begin by taking a look at mapping. Mapping is the process of building a representation of the environment from range-based observations. In this assignment, the environment provides simulated _raycasts_ that report the distance to the nearest obstacle in several directions around the agent. Your goal is to use these readings to update a two-dimensional _occupancy grid_, where each cell maintains a logit for one of four classes: `free`, `wall`, `flag`, `capture_point`.

When a ray detects a hit, modify the logit of the corresponding cell (making it more likely to be occupied by the object of the appropriate class). To do so, you should use the appropriate sensor confidence probability which indicates how likely an object of a given type occupies that cell.

> [!NOTE]
> The logits are automatically clamped between $[-L, L]$ for reasons pertaining to numerical stability. For similar reasons, you may find that it helps to modify the logits using the centered log probabilities of the classes (i.e subtract off the mean of the log probabilities from each class)!

Here’s the procedure at a high level:

-   For each raycast:
    -   Compute the cells along the ray using the agent’s current position and the ray’s angle.
    -   For each cell along the ray:
        -   If the cell is before the hit point, modify the logits so that the flag is more likely
        -   If the cell corresponds to the hit, modify the logits so that the entity type of the ray hit is more likely

Once you've implemented this logic move your agent around to explore the map! Think back to some of the earlier search strategies we've seen in the course to attempt to explore and map the maze. We'll be verifying that the error between your occupancy grid and the true occupancy grid is not too large after a sufficient amount of time.

You should aim to have an autonomous agent explore a randomly generated maze and reach a mapping error of under 40% in 5 minutes.

> [!TIP]
> When you're getting started, it may help to have manual control of your mapping agent to debug how you're filling the occupancy grid.
> To do so, you can have the `MappingAgent` subclass the `TeleopAgent` and make sure to return the output of `super().get_action(...)` in the implementation of `MappingAgent`'s `get_action` method.

### Task 2: Localization

In `src/maze/agents/localization_agent.py`, you will implement a 2D Kalman Filter that continuously estimates the agent’s position in the arena using noisy observations from a simulated inertial measurement unit (IMU). The IMU provides you with a noisy position estimate of the agent's current location in the world. You may assume that this noise is zero-mean additive Gaussian noise with a known standard deviation (provided in `GameState`). We'll furthermore, make the simplifying assumption that the noise in each axis is uncorrelated (this is a strong assumption to make. why?).

#### Implementation Steps

Localization is the process of determining where the agent is within the world based on imperfect motion and sensor data. In this task, you’ll implement a Kalman Filter where at each timestep, your estimator should perform two stages:

1. **Prediction:**

    - Use the agent’s previous state and control input to predict the new position.
    - Propagate the uncertainty forward according to the transition model.
    - Add process noise to account for uncertainty in the motion dynamics.

2. **Correction:**
    - When a new noisy position measurement is received from the environment (`game_state.agent.position`), use the sensor model to relate the measurement to the predicted state.
    - Compute the Kalman gain to determine how much to trust the new measurement relative to the prediction.
    - Update both the estimated state and covariance to refine the belief.

Once implemented:

-   In `src/maze/agents/localization_agent.py`, complete the `get_action` method to:
    -   Perform the prediction and correction steps on each call.
    -   Maintain and update the agent’s internal position estimate over time.
-   When visualized, your estimated trajectory should closely follow the agent’s true path, despite the noise present in both the motion and measurements. Your estimated agent position is shown as an translucent copy of your agent which gets its position from the `position` property on the `LocalizationAgent` class.

The `LocalizationAgent` has access to the true underlying occupancy grid. Use this occupancy grid to plan a route from the flag to the capture point. Your agent should be able to capture a single flag in 5 minutes.

> [!NOTE]
> Unlike the previous assignment, flag pickup and dropoff is no longer automatic! You'll have to manually send the appropriate action to pickup and drop off the flags. To succesfully perform these actions, you must be within 3 units of the flag/capture point.

> [!NOTE]
> There are many approaches you can take to plan this route! Think back to assignments 1 + 2 to determine which of these options might be best suited for this task. (Are you really planning in continuous space?)

> [!TIP]
> Just like with the `MappingAgent`, you may find it helpful to subclass the `TeleopAgent` when getting started. If you need help figuring out how to do this, post on Ed, stop by office hours, or catch Hammad after class!

### Task 2b: A Factor Graph View of Localization

Your Kalman Filter recursively tracks a belief over the agent's position by alternating between two steps: predicting forward through a motion model, and correcting with a measurement model. It turns out this recursion is a special case of a much more general idea: representing a probabilistic estimation problem as a **factor graph** and running **variable elimination** on it.

A factor graph represents a joint distribution as a graph of _variables_ (the things we don't know, e.g. the agent's position at each timestep) connected to _factors_ (potentials that constrain those variables, e.g. a prior belief, a motion model, or a measurement model). For Gaussian beliefs, it's convenient to write each factor in _canonical_ (information) form as a pair $(\Lambda, \eta)$ such that

$$\text{factor}(x) \propto \exp\left(-\tfrac{1}{2} x^\top \Lambda x + \eta^\top x\right).$$

In this form, combining factors that share variables is just adding their (padded) $\Lambda$/$\eta$ blocks together, and **eliminating** (marginalizing out) a variable is a Schur complement over those blocks. You'll build a two-node factor graph — one variable for the agent's previous position (`x_prev`) and one for its current position (`x_curr`) — using the exact same `F`, `Q`, `H`, and `R` your Kalman Filter already uses:

-   A **prior factor** over `x_prev`, from the previous timestep's belief (given: `prior_factor`).
-   A **motion factor** over `(x_prev, x_curr)`, encoding the conditional $x_\text{curr} \mid x_\text{prev} \sim \mathcal{N}(F x_\text{prev} + u, Q)$ — the same motion model used in `predict()`.
-   A **measurement factor** over `x_curr`, encoding the likelihood $\mathcal{N}(z; H x_\text{curr}, R)$ — the same sensor model used in `update()` (given: `measurement_factor`).

#### Implementation Steps

In `src/maze/factor_graph.py`, implement:

1. `motion_factor(F, Q, u, var_prev, var_curr)`: build the joint canonical factor over `(var_prev, var_curr)` for the linear-Gaussian motion conditional described above.
2. `eliminate(joint, var)`: given a joint canonical factor, marginalize out `var` via the Schur complement, returning the resulting factor over the remaining variable(s).

Once both are implemented, eliminating `x_prev` from `combine([prior_factor(...), motion_factor(...)])` should reproduce your Kalman Filter's `predict()` step exactly, and combining that result with a `measurement_factor(...)` should reproduce your `update()` step exactly — down to floating point tolerance. Run `uv run pytest tests/test_factor_graph_equivalence.py -v` to check your implementation against your own Kalman Filter.

> [!NOTE]
> Think about it: eliminating `x_prev` in temporal order is what collapses this graph back down to just two variables every timestep — which is exactly why the Kalman Filter can run in constant time and memory per step. What would happen to this graph, and to elimination, if you also had variables for landmark positions that got observed and re-observed over time? (You won't need to answer this anywhere — just something to chew on before the group assignment.)

### Task 3: Writeup

In a short writeup, describe what you did and tried on this assignment. This is a chance to reflect on your approach and design choices, not a formal report — bullet points are fine.

Please address the following for each task:

-   **What you implemented.** Briefly summarize the approach you took for mapping, localization, and the factor graph.
-   **What you tried that didn't work.** Design choices you explored and abandoned, bugs that took a while to track down, or parameter values that gave bad results and why you think they did.

You are also welcome to include plots, screenshots, or short snippets of code that illustrate what you're describing. Submit the writeup as a markdown file 

## Installation

### `uv`

You should have `uv` installed from the previous programming assignment. If so, you should feel free to skip to [Installing Project Dependencies](#installing-project-dependencies). Otherwise, we've duplicated the instructions for installing `uv` below. We highly recommend that you use `uv` to manage your virtual environments for this course. Feel free to post on Ed or stop by office hours if you have any questions or trouble setting up your environment!

#### Installing `uv`

A headache-free way to start running the starter code is via the [`uv`](https://docs.astral.sh/uv/getting-started/installation/) package manager. To install (on Mac, Linux, WSL):

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> [!NOTE]
> The above command requires `curl` installed! You'll most likely have this installed, already but if not it should be a small `brew/apt/pacman install` away. Alternatively, if you have `wget` already installed you can use
>
> ```
> wget -qO- https://astral.sh/uv/install.sh | sh
> ```

Alternative approaches exist to install `uv` which you are invited to explore in the [Astral documentation](https://docs.astral.sh/uv/getting-started/installation/).

#### Installing Project Dependencies

One of the major superpowers of `uv` is its ability to manage different versions of Python using a combination of virtual environments and configuration files. Initialize this project's virtual environment and install all the required dependencies by running the following command **in the root of your cloned GitHub repository**:

```
uv sync
```

> [!NOTE]
> You'll need to create a new virtual environment for each assignment!

This should install an appropriate Python version (3.13) and all the project's dependencies including `pytest`.

### Selecting your Python Interpreter

Using typed Python can highly improve your programming (and especially your debugging experience). To enable type checking in VSCode:

-   Open Settings (`CTRL`/`CMD` + `,`)
-   Search for `Type Checking Mode`
-   Set the mode to your desired level of strictness (`standard` is a good default!)

<div align="center">
    <img src="docs/type_checking.png" width="1000"/>
</div>

To ensure that all the type stubs are resolved for your installed dependencies, you have to select the correct Python interpreter. To do so:

-   Open the Command Pallette (`CTRL`/`CMD` + `SHIFT` + `P`)
-   Type and select `Python: Select Interpreter`
-   Choose the virtual environment located in the stencil directory.

<div align="center">
    <img src="docs/interpreter_selection.png" width="1000"/>
</div>

For this to be correctly detected, be sure that the opened folder in VSCode is your cloned Github repository!

#### Running the Maze Agents

To launch and interact with any of the Maze agents, use:

```
uv run python -m maze [--help] [--config CONFIG] [--agent AGENT_ID]
```

> [!NOTE]
> Items surrounded in `[]` are optional arguments.
> `--agent` can be one of `teleop`, `mapping`, or `localization`.
> The simulation will open a window showing the maze, agent, and flags.

1. The TeleopAgent allows you to control the red agent manually to explore the maze, pick up the flag, and drop it at the capture point.
2. The MappingAgent builds an internal map of the maze using simulated raycast data. It updates an occupancy grid as the agent moves through the environment.
3. The LocalizationAgent estimates the agent’s position in the maze using noisy motion and sensor data through a 2D Kalman Filter.

Some helpful commands:

```bash
# Run the Mapping Agent
uv run python -m maze --config configs/mapping.yaml --agent mapping

# Run the Localization Agent
uv run python -m maze --config configs/localization.yaml --agent localization
```

To run the provided tests (or ones you created) use:

```
uv run pytest
```

> [!NOTE]
> No sourcing required! If you prefer the virtual environment folder to not be called `.venv` then you can pass a name to the `uv venv` command. However, this would require setting the `UV_PROJECT_ENVIRONMENT` variable to this name either prior to every `uv sync` and `uv run` command, exporting the variable in every terminal session, or using some external dependency to manage your environment variables like [`direnv`](https://direnv.net/).

## Tips and Debugging

We use `pytest` to write and run tests for your assignments. `pytest` comes with a ton of handy and useful flags to help you test and debug parts of your code! Here's a list of useful flags to pass to `pytest` when debugging your assignment.

### Selecting Tests

```
pytest                      # run all tests (auto-discovery)
pytest path/                # run tests under a directory
pytest tests/test_x.py      # run tests in a file
```

### Failure Control

```
pytest -x                  # stop after first failure
pytest --maxfail=3         # stop after 3 failures
pytest --lf                # run last-failed tests only
pytest --ff                # run failures first, then the rest
pytest --sw                # stepwise: stop on first fail, resume next time
```

### Output

```
pytest -q                  # quiet (less output)
pytest -v                  # verbose (test names)
pytest -vv                 # extra verbose
pytest -s                  # don't capture stdout/stderr (show prints)
pytest -rA                 # show summary for all outcomes (reasons)
pytest -l                  # show local variables in tracebacks
pytest --tb=short          # shorter tracebacks
pytest --tb=line           # one-line tracebacks
pytest --durations=10      # show 10 slowest tests
```

### Common Combinations

```
# Fail fast with clear reasons
pytest -x -vv -rA --tb=short

# Re-run only what failed last time, show prints
pytest --lf -s -vv

# Redirecting output to a file for readability
pytest -s > foo.txt
```
