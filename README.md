<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# CS 1820 Individual Programming Assignment 3: Goblets and Ghouls

| [`README`] | [`Installation`](docs/1-installation.md#installation) | [`Game Overview`](docs/2-game-overview.md#game-overview) | [`Getting Started`](docs/3-getting-started.md#getting-started) | [`Individual Tasks`](docs/4-individual-tasks.md#individual-tasks) |
| :---: | :---: | :---: | :---: | :---: |

<br>

Welcome back to the CS 1820 Arcade! This time, you'll be controlling an adventurer on their quest to become rich by collecting goblets in a discrete gridworld. However, this world will prove difficult to navigate for our naive adventurer. Unlike our previous games, your agent doesn't always take its intended action!

To overcome this, you'll be implementing and experimenting with two reinforcement learning algorithms: value iteration and Q-learning. To get started, we have split this `README` into a series of Markdown files, which you can navigate through at the top. As always, we recommend reading through the entire assignment and the stencil code before you start working.

<figure style="text-align: center;">
    <img src="./docs/assets/game_preview.webp" alt="The adventurer is caught by the ghost." width="600">
</figure>

<br>

## Code Structure

This repository contains a couple major directories of interest.

### `configs/`

In this assignment, worlds are generated according to config YAML files, which specify environment rules, world generation behavior, and some GUI settings. We encourage you to inspect the default config and experiment with your own configs.

### `docs/`

In addition to the files in this `README`, we've provided a few handouts for your reference.

- `comments.md` contains documentation for important classes related to the game.
- `pseudocode.md` contains high-level pseudocode for the algorithms you'll be using.

### `policies/`

This folder is where your trained policies will be saved. Note that for our gridworld setting, a policy trained for one environment doesn't make sense when rendered in a different environment. For this reason, we encourage you to name your config files and policies carefully.

### `scripts/`

We've created a few helpful scripts to aid in the development of your agents.

- `creator.py` provides a simple GUI to edit and create *fixed* world YAML files. See the `worlds/` section below. You can run `uv run scripts/creator.py -h` for more details.

### `src/`

All code that you will be responsible for belongs here. In particular, you will be implementing value iteration and $Q$-learning, and using these algorithms to train policies for our game. Any Python script in this folder can be used to train policies, as long as the script defines a `train` function with the correct signature. We encourage you to create any other files, functions, and methods you need!

### `worlds/`

Optionally, you can override a config's random world generation by supplying a fixed world YAML file. These can can either be passed as arguments to the runner or through the `world_file` field in a config YAML. We've provided a simple fixed world to get started. Note that a config is still necessary to specify environment rules such as the agent's transition vector.

<br>

---

| [`Back to top`](#cs-1820-individual-programming-assignment-3-goblets-and-ghouls) | [`Installation` →](docs/1-installation.md#installation) |
| :---: | ---: |
