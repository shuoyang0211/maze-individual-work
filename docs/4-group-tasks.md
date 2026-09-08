<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Group Tasks

| [`README`](../README.md#cs-1820-group-programming-assignment-2-maze) | [`Installation`](1-installation.md#installation) | [`Game Overview`](2-game-overview.md#game-overview) | [`Getting Started`](3-getting-started.md#getting-started) | [`Group Tasks`] |
| :---: | :---: | :---: | :---: | :---: |

<br>

Congrats on completing the individual assignment! Now, we'll be shifting to the task of *mapping*. Like a real robot, our agent doesn't already know its environment. Instead, the environment is exposed through simulated *raycasts* that report the distance to the nearest obstacle in several directions around the agent. Your goal is to use these readings to build a two-dimensional *occupancy grid*, and then to combine that map with the localization you already wrote into a single agent that does both at once.

<br>

## Task 1: Occupancy mapping

Your agents no longer get the true occupancy grid. From here on, the grid handed to `get_action` starts empty and is yours to fill in. Each cell carries a *logit* for each of four classes — free space, wall, flag, and capture point — and `probabilities()` turns those four logits into a softmax distribution over the classes.

In [`mapping/occupancy_mapping.py`](../src/maze/mapping/occupancy_mapping.py), you will implement two functions.

- `update_cell` folds one sensor observation into one cell. Each `SensorConfidence` gives a per-class confidence, so the log-likelihood of each class is added to that class's logit, scaled by `log_odds_scale`. The cell's `assignment` is not derived from the logits automatically — you must set it yourself once the most likely class's probability crosses `assign_threshold`, and clear it when no class does.
- `update_grid` walks a whole list of raycasts. For each ray, work out which cells it passes through, and update each of them.

> [!NOTE]
> The logits are clamped to a fixed range around zero for numerical stability. Because a softmax is unchanged by adding a constant to every logit, you can subtract the mean of the four log-likelihoods before adding them without changing what the cell believes — but it does keep the logits from all drifting to the clamp together and losing their differences. This is worth doing.

The geometry of a single ray is the fiddly part. `line_between` gives you the grid cells along a segment, so you need the cell the ray starts in and the cell it ends in, which you can get from `theta` and `distance`. The cells *before* the endpoint were passed through, and are evidence of free space, so they get `path_confidence`. The endpoint cell is evidence of whatever was hit, so it gets `endpoint_confidence`.

> [!IMPORTANT]
> A ray that hits nothing reports `endpoint_type` of `Free` and a `distance` equal to its `max_distance`. That means "I saw nothing out to my range", not "there is something at exactly this distance". Only treat the last cell as a hit when `endpoint_type` is *not* `Free`.

<br>

## Task 2: A mapping agent

Now put that to work. Your agent in [`agents/mapping_agent.py`](../src/maze/agents/mapping_agent.py) should call `update_grid` every tick and drive somewhere useful. In `configs/mapping.yaml` there is no position noise and there are no flags, so this task is purely about building a good map: the only thing that limits you is where you choose to go.

```sh
uv run maze --config configs/mapping.yaml --agent mapping
```

Think back to the search strategies from earlier in the course. A reasonable place to start is to steer toward the boundary between what you have mapped and what you haven't, since that is where new information is; picking *which* piece of that boundary to head for is where the interesting design choices live.

`tests/test_mapping.py` scores you on two numbers over several fixed mazes: the fraction of truly-free cells you labelled free, and the fraction of true wall cells you labelled wall. You need **85% free-space recall and 45% wall recall**.

> [!NOTE]
> Those two bars are deliberately far apart. Every ray sweeps a corridor of free space, so free cells are cheap to collect and the bar mostly checks that you explored at all. Walls are harder: a ray only ever touches the *face* of a wall, never its interior, so a chunk of every wall is permanently invisible and even a perfect mapper lands well short of 100%. Don't read a wall recall of 0.6 as a bug.

<br>

> [!TIP]
> When you're getting started, it helps to drive the agent yourself and watch the grid fill in. Pass `--teleop` to take manual control: your policy still runs, so the map still updates, but your movement commands are ignored in favour of the keyboard. Press `C` in the GUI to see the occupancy grid your agent has built.

<br>

## Task 3: A SLAM agent

Now both halves at once. In `configs/slam.yaml` the position readings are noisy *and* the map starts empty, so your agent in [`agents/slam_agent.py`](../src/maze/agents/slam_agent.py) has to localize and map simultaneously — this is the *SLAM* problem, and it is harder than either piece alone because each half depends on the other. You are writing your map using an estimated position, so a bad estimate smears the map; and a smeared map makes the free space you plan through less trustworthy.

Start by gluing together what you already have: run your `KalmanFilter2D` as in the individual assignment, feed `update_grid` your *estimated* position rather than the raw reading, and plan over the map you're building.

Two behaviours are worth calling out explicitly, because they are easy to miss and both cost you points.

- **Keep mapping after the last flag is captured.** You are graded on the map as well as the flags, and the run does not end early. An agent that parks once it has captured everything will score well on flags and badly on the map.
- **A capture point holds exactly one flag.** Once it is full it is spent, and it disappears from the grid, as does a flag you are carrying. So the entities you can still see are exactly the ones you can still use, and you don't need to track which capture points you've already filled.

`tests/test_slam.py` asks for **at least one flag captured on every maze, and a mean mapping accuracy of at least 65%**. Capturing *both* flags every time is not required: a flag can sit in a corner of the maze you never reach within the time budget, so how many you find depends partly on where exploration happens to take you. Getting both consistently is a good target for the leaderboard rather than a requirement to pass.

<br>

## Going further

Our SLAM implementation is far from perfect, and you're invited to improve either half. None of this is required, but it can improve your standing on the Gradescope leaderboard. Some starting points:

- The localization code ignores the raycasts entirely. Once you have a decent map, the ranges themselves say a lot about where you are — a reading that only makes sense from one spot in a corridor is a measurement you're currently throwing away. And we only ever explored Kalman filters; how would a particle filter do here?
- You may notice cells that were confidently walls drifting back to free as the agent moves. That is expected — the grid is a discrete approximation of continuous rays, so a ray sometimes slips through a cell that contains a wall without hitting it there. You might change how logits update once a class is already very likely. You might also exploit the fact that walls in this maze tend to run in long straight lines.
- Exploration is where the time budget actually goes. Cruising well below `max_speed` costs you coverage, and coverage is what decides whether you ever find the second flag.

<br>

## Written task

In a short writeup, describe what you did and tried. This is a chance to reflect on your approach and design choices, not a formal report — bullet points are fine. Please address both of the following.

- **What you implemented.** Briefly summarize the approach you took for mapping, for localization, and for combining them into SLAM.
- **What you tried that didn't work.** Design choices you explored and abandoned, bugs that took a while to track down, or parameter values that gave bad results, and why you think they did.

You're welcome to include plots, screenshots, or short code snippets that illustrate what you're describing. Submit the writeup as a Markdown file alongside your code.

Feel free to post on Ed or stop by office hours if you have any questions or want to brainstorm ideas!

<br>

---

| [← `Getting Started`](3-getting-started.md#getting-started) | [`Back to top`](#group-tasks) |
| :--- | :---: |
