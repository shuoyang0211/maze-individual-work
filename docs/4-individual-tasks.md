<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Individual Tasks

| [`README`](../README.md#cs-1820-individual-programming-assignment-2-maze) | [`Installation`](1-installation.md#installation) | [`Game Overview`](2-game-overview.md#game-overview) | [`Getting Started`](3-getting-started.md#getting-started) | [`Individual Tasks`] |
| :---: | :---: | :---: | :---: | :---: |

<br>

In the individual assignment, we'll be looking at the task of *localization*. (We'll leave *mapping* for later.) Like a real robot, our agent only sees a noisy reading of its own position. In particular, you may assume that this is zero-mean additive Gaussian noise with a known standard deviation, and that the noise in each axis is uncorrelated. (This is a strong assumption. Why might it fail for a real robot?)

Your goal is to fuse a stream of these noisy readings, together with the agent's own commanded motion, into an estimate good enough to navigate with. You will implement this estimator twice, once as a Kalman filter and once via elimination on a factor graph, before implementing a policy that is able to capture all the flags.

<br>

## Task 0: Noise model

In a filter, we maintain a belief about an unknown quantity, which is refined with new control inputs and corrected with new noisy measurements. Our game is set up as a linear-Gaussian system (see `formulas.md`), where the unknown quantity is the agent's position, the control input is the displacement from the commanded velocity, and each measurement is a noisy observation of the agent's position.

Before we can run a filter, we need to define how much the filter (dis)trusts its own predicted motions along with its received measurements. In [`state_estimation/model.py`](../src/maze/state_estimation/model.py), you will find some helper functions used by both the Kalman filter and the factor graph. Your job is to implement the `process_noise` $Q$ and `measurement_noise` $R$.

> [!NOTE]
> The observation model $H$ and the state-transition model $F$ are already defined as identity in each filter. Why is this the case? How does the state vector relate to the sensor reading? How does the state evolve over time?

<br>

## Task 1: Kalman filter

Now, you will implement a two-dimensional Kalman filter, which recursively tracks a belief about the agent's position by alternating between two steps: predicting forward through a motion model, and correcting with a measurement model. The belief is given by a Gaussian, stored via its mean `self.x` and covariance `self.P`. In [`state_estimation/kalman_filter.py`](../src/maze/state_estimation/kalman_filter.py) you will implement three methods.

- `initialize` sets the filter from its first reading.
- `predict` uses the agent's previous state and control input to predict the new mean position, propagates the covariance according to the motion model, and adds process noise to account for uncertainty in the motion dynamics.
- `update` takes a new noisy measurement, computes the Kalman gain to determine how much to trust the new measurement, and refines the estimated state and covariance.

> [!TIP]
> If you want to see your Kalman filter in action, we recommend getting a basic localization agent moving in Task 3 first. You can come back to the factor graph at any point.

<br>

## Task 2: Factor graph elimination

Your Kalman filter's recursive update is a special case of a much more general idea: representing a probabilistic estimation problem as a *factor graph* and running *variable elimination* on it. A factor graph represents a joint distribution as a graph on *variables*, which are quantities we don't know, connected via *factors*, which are *potentials* that constrain those variables (e.g. a prior belief, a motion model, or a measurement model). Rather than a mean and covariance, the belief is now carried as a Gaussian potential over the variables.

Your task is to build a two-node factor graph over the agent's previous position `x_prev` and current position `x_curr`, using the same $F$, $H$, $Q$, and $R$ your Kalman filter already uses. In [`state_estimation/factor_graph.py`](../src/maze/state_estimation/factor_graph.py), you will implement the following two functions.

- `motion_factor` builds the joint canonical factor over the previous and current positions.
- `eliminate` marginalizes a variable out of a joint canonical factor, returning the resulting factor over the remaining variables.

Once your factor graph works, eliminating `x_prev` should reproduce your Kalman filter's `predict` step exactly, and combining the result with a `measurement_factor` should reproduce your `update` step exactly. We've wired this up as a `FactorGraphFilter2D`, and you can run `tests/test_state_estimation.py` to check that it gives the same behavior as your `KalmanFilter2D`.

<br>

## Task 3: A localization agent

It's time to implement your first agent! In [`agents/localization_agent.py`](../src/maze/agents/localization_agent.py), you will be implementing a *localization* agent, which must determine its position in the world based on imperfect motion and sensor data. Each time `get_action` is called, you will need to drive your `KalmanFilter2D` (or `FactorGraphFilter2D`) through the following cycle.

1. On the first tick, `initialize` from `game_state.agent.position` and `game_state.agent.position_stddev`.
2. On every tick after that, `predict` with `dt` and the velocity you commanded on the *previous* tick, then `update` with the current reading and its standard deviation.

Your agent can then report the filter's mean as its `estimated_position`, which will render as a translucent ghost that should closely follow the agent's true path.

> [!NOTE]
> Your `predict` step assumes the agent really moved by the velocity it commanded. What happens to that assumption when a wall gets in the way?

Your goal is now to plan a route to capture every flag in the maze. In particular, you should use `configs/localization.yaml`, which gives your agent information about all walls, flags, and capture points by passing the true occupancy grid. (Note that flags are removed from the grid when held, and both flags and capture points are removed when captured.) We've written a test in `tests/test_localization.py` that benchmarks your agent based on how many flags it collects.

> [!TIP]
> There are many approaches you can take to plan this policy! Think back to the first assignment. (Are you really planning in continuous space?) You can also experiment with the filter's `process_noise_stddev`, which controls how sensitive your filter is to unexpected acceleration (e.g., due to walls). Since $Q$ is proportional to `dt ** 4`, you might find very large values more useful.

<br>

---

| [← `Getting Started`](3-getting-started.md#getting-started) | [`Back to top`](#individual-tasks) |
| :--- | :---: |
