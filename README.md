# CS182 Individual Programming Assignment 3: Maze 

Welcome back to the CS182 Arcade! Over the course of the semester we'll be taking a deeper dive into many of the topics covered in lecture through the individual and programming assignments. In particular, we will focus on how to apply the knowledge you've learned in class for agent planning and learning in games.

For this series of assignments, we’re now exploring _perception_, one of the fundamental challenges in robotics. In this programming assignment you will implement two key perception modules: Mapping and Localization within the Capture the Flag environment from the previous assignment.

As always, we highly recommend reading through the entire assignment and the stencil code before beginning with any parts of the assignment.


## Game

In the individual and group assignments, you will once again be playing Capture the Flag in a _continuous_ world. However, unlike the previous programming assignment, your agent no longer has access to perfect information about the environment. Instead, it must learn to _perceive_ its surroundings through noisy sensor data.

The goal of this assignment is to give your agent the ability to:
- Build and maintain map of the world through ray-based observations, and
- Estimate its own position within that map using a simple Kalman Filter.


### World Structure

The world remains a rectangular arena enclosed by walls with capture points and flags. The environment exposes limited information through _raycasts_ that simulate a range sensor.

Each time step, the agent receives a `GameState` that provides:
- Ray-based distance measurements to nearby obstacles,
- Its (noisy) current position and velocity,
- Limited observations of nearby entities.

You will maintain an _occupancy grid_, where each cell stores a _log-odds probability_ of being occupied. Over time, your agent should refine this grid into an accurate map of explored areas.


## Code Structure

This repository contains two major directories of interest: `src` and `configs`:

### `src/maze/agents`

This is where your work lives! There are three agents provided in this stencil:

- `TeleopAgent`: A simple manually controlled agent that maps keyboard inputs to actions.
- `MappingAgent`: A subclass of `TeleopAgent` that updates an occupancy grid using simulated raycasts.
- `LocalizationAgent`: An agent that estimates its position using a 2D Kalman Filter.

If you have any questions about what things do/how things work please feel free to post a question on [Ed](https://edstem.org/us/courses/82550/discussion)!

### `configs`

Configuration files define parameters such as which agent to run, number of rays, and world setup. The two of most interest for this assignment are:

- `configs/mapping.yaml`
- `configs/localization.yaml`

Please feel free to create copies and modify these files as you work through the assignment to make sure things are working as expected!

## Tasks

There are **two total tasks** in this assignment:

### Task 1: Mapping

In `src/maze/agents/mapping_agent.py`, you will implement an agent that constructs a map of the environment by updating an occupancy grid using simulated sensor readings. Use the raycasts provided by the `GameState` to update the passed-in `OccupancyGrid` within the `get_action` method. Each grid cell should keep track of its _log-odds_ of being occupied.

After sufficient exploration, your occupancy grid should closely resemble the ground truth map.

#### Implementation Steps

?


### Task 2: Localization

In `src/maze/agents/localization_agent.py`, you will implement a 2D Kalman Filter that continuously estimates the agent’s position (and optionally velocity) in the arena using noisy motion and noisy observations. The estimator should maintain a compact state and an associated uncertainty, predict the state forward using a simple motion model, and correct the estimate when new measurements arrive from the environment.

#### Implementation Steps

?



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

#### Installing the Maze Environment (Engine)
_? needed or not_

### Selecting your Python Interpreter

Using typed Python can highly improve your programming (and especially your debugging experience). To enable type checking in VSCode:

-   Open Settings (`CTRL`/`CMD` + `,`)
-   Search for `Type Checking Mode`
-   Set the mode to your desired level of strictness (`standard` is a good default!)

<div align="center">
    <img src="docs/imgs/type_checking.png" width="1000"/>
</div>

To ensure that all the type stubs are resolved for your installed dependencies, you have to select the correct Python interpreter. To do so:

-   Open the Command Pallette (`CTRL`/`CMD` + `SHIFT` + `P`)
-   Type and select `Python: Select Interpreter`
-   Choose the virtual environment located in the stencil directory.

<div align="center">
    <img src="docs/imgs/interpreter_selection.png" width="1000"/>
</div>

For this to be correctly detected, be sure that the opened folder in VSCode is your cloned Github repository!

#### Running the Maze Agents

To run the starter code use:

```
uv run python -m maze [--help] [--config CONFIG] [--agent AGENT_ID]
```

> [!NOTE]
> Items surrounded in `[]` are optional arguments while those in `<>` are required.  
> `--agent` can be one of `teleop`, `mapping`, or `localization`.

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
