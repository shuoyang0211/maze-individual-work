<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Individual Tasks

| [`README`](../README.md#cs-1820-individual-programming-assignment-2-maze) | [`Installation`](1-installation.md#installation) | [`Game Overview`](2-game-overview.md#game-overview) | [`Getting Started`](3-getting-started.md#getting-started) | [`Individual Tasks`] |
| :---: | :---: | :---: | :---: | :---: |

<br>

Your agent gets a noisy reading of its own position on every policy tick. In `configs/localization.yaml` that reading has a standard deviation of `25.0` in a world `100` units across, so a single reading tells you very little. Your job is to fuse a stream of them, together with what the agent knows about its own commanded motion, into an estimate good enough to navigate with.

You will build that estimator twice. Tasks 1 and 2 build it as a **Kalman filter**, carrying a mean and covariance forward through time. Task 3 builds it as **elimination on a factor graph**. The two produce identical numbers, and `tests/test_state_estimation.py` holds you to that. The point of doing it twice is that the Kalman filter isn't a special-purpose algorithm — it's what inference on a chain reduces to when you keep only the most recent time step. Task 4 puts the estimate to work.

> [!NOTE]
> The GUI draws your reported estimate as a translucent ghost and the agent's true position as a red square. Press `C` to overlay the occupancy grid.

<br>

## Task 1: The noise model

> **Implement `process_noise` and `measurement_noise` in `src/maze/kalman_filter.py`.**

A filter is only as good as its answer to two questions: how much should it distrust its own prediction of where it moved, and how much should it distrust the latest reading? Those answers are the covariances `Q` and `R`, and everything else in this assignment consumes them. Both are 2x2, one row and column per axis.

**Process noise `Q`.** The agent commands a velocity but does not perfectly achieve it, and the discrepancy behaves like an unknown acceleration with standard deviation `process_noise_stddev`, independent in `x` and `y`. Over one step of length `dt`, an acceleration `a` displaces the agent by `a * dt^2 / 2`, so the position variance that step contributes scales with `dt^4 / 4`.

**Measurement noise `R`.** Readings are corrupted by noise of standard deviation `position_stddev`, the same in each axis and uncorrelated between them. That value arrives per-tick as `game_state.agent.position_stddev`, so `R` gets rebuilt from it every step rather than stored once.

`F` and `H` are provided as `self.F` and `self.H`. The `KalmanFilter2D` docstring explains why both are the identity, which is worth understanding before Task 2.

<br>

## Task 2: The Kalman filter

> **Implement `initialize`, `predict`, and `update` in `KalmanFilter2D`.**

The belief about the agent's position is a Gaussian, stored as a mean `self.x` (2x1) and covariance `self.P` (2x2). `initialize` sets it from the first reading. Every tick after that applies `predict`, which moves the belief forward using the velocity you commanded, then `update`, which pulls it toward a new reading.

```
u = control_vector(dt, control_input)             # provided for you
Q = process_noise(dt, self.process_noise_stddev)

x <- F x + u
P <- F P F^T + Q
```

Prediction always makes you less certain, which is exactly what adding `Q` does.

```
R = measurement_noise(position_stddev)

y = z - H x                 # innovation: how wrong the prediction was
S = H P H^T + R             # how surprised you should be by that much error
K = P H^T S^-1              # gain: how far to move toward the reading
x <- x + K y
P <- (I - K H) P
```

The gain `K` is the whole idea. When `P` is large relative to `R`, the filter barely trusts itself and moves most of the way to the reading; when `R` dominates, it coasts on its prediction. You never choose that tradeoff by hand — it falls out of the two covariances you wrote in Task 1.

> [!IMPORTANT]
> Use `self.F`, `self.H`, and your Task 1 functions rather than rebuilding these matrices inline. Task 3 depends on both filters using the exact same model.

<br>

## Task 3: Factor graph elimination

> **Implement `motion_factor` and `eliminate` in `src/maze/factor_graph.py`.**

Now build the same estimator from the other direction. Instead of a mean and covariance, represent the belief as an unnormalized Gaussian potential in **canonical form** (also called information form):

```
factor(x)  ∝  exp( -1/2 x^T Lambda x  +  eta^T x )
```

A `GaussianFactor` stores that `Lambda` and `eta` along with the `scope` of variables it covers. The change of coordinates is worth it because the two operations you need become almost trivial: **multiplying** factors together (`combine`, provided) is just summing their blocks, and **marginalizing out** a variable is a Schur complement.

**`motion_factor`** encodes the motion model as a potential over *two* variables at once, the position before the step and the position after:

```
x_curr | x_prev  ~  N(F x_prev + u,  Q)
```

Expand that Gaussian's exponent, `-1/2 (x_curr - F x_prev - u)^T Q^-1 (x_curr - F x_prev - u)`, and collect terms over the stacked vector `[x_prev; x_curr]`. The quadratic coefficients give a 4x4 `Lambda`, the linear coefficients a 4x1 `eta`. The off-diagonal blocks are what couple the two time steps — a factor with zero off-diagonals would claim the two positions are unrelated.

> [!WARNING]
> `dim` is the size of a *single* variable (2 here), not the width of `Lambda`. `combine` will raise a `ValueError` if you get this wrong.

**`eliminate`** removes a variable by integrating it out. Split `Lambda` and `eta` into the block for the variable you're eliminating (`a`) and the blocks that survive (`b`):

```
Lambda' = Lambda_bb - Lambda_ba Lambda_aa^-1 Lambda_ab
eta'    = eta_b     - Lambda_ba Lambda_aa^-1 eta_a
```

Use `joint.indices_for(...)` for those blocks rather than computing offsets yourself, and prefer `np.linalg.solve` over forming `Lambda_aa^-1`.

Once both work, `FactorGraphFilter2D` runs. Look closely at what it does: the Kalman `predict` from Task 2 *is* the marginalization of `x_prev` out of the joint over two consecutive positions. Same model, same answer, different bookkeeping. Run `uv run pytest tests/test_state_estimation.py` to check the two filters against each other step by step.

<br>

## Task 4: The localization agent

> **Implement `estimated_position` and `get_action` in `src/maze/agents/localization_agent.py`.**

`configs/localization.yaml` sets `use_true_map: true`, so the occupancy grid arrives already filled in — mapping is the group assignment's problem. What you have to deal with here is not reliably knowing where *you* are.

Each time `get_action` is called, drive your filter through one cycle:

1. On the very first tick, `initialize` from `game_state.agent.position` and `game_state.agent.position_stddev`.
2. On every tick after that, `predict` with `dt` and the velocity you commanded on the *previous* tick, then `update` with the current reading and its standard deviation.
3. Return the filter's mean from `estimated_position`.

The rest is navigation. Scan the grid for the nearest cell assigned `EntityType.Flag`, plan a route that avoids `Wall` cells, and return `Action.Move` commands along it, using `occupancy_grid.world_center` to turn a cell into a position to steer toward. Once close enough, return `Action.PickupFlag()`, then head for an `EntityType.CapturePoint` cell and `Action.DropFlag()`. The interaction radius is a config value the agent cannot read at runtime, so pick your own distance threshold and tune it. See [`comments.md`](comments.md#occupancygrid) for the grid, `Action`, and `GameState` interfaces.

A few things that tend to bite:

- **The estimate needs time to converge.** Right after `initialize`, `P` is roughly `position_stddev^2`, which is enormous. Holding still for a moment lets repeated `update` calls shrink it before you commit to a plan.
- **Plan from the estimate, not the reading.** Using `game_state.agent.position` directly defeats the assignment and will jitter your agent into walls.
- **`cell_at` can return `None`**, and the estimate is never exact, so handle the off-grid case and leave clearance around walls.

Run `uv run pytest tests/test_localization.py` to check that your agent captures every flag in the time budget, and `uv run maze --config configs/localization.yaml --agent localization` to watch it.

<br>

## Debugging your filter

When the agent doesn't capture the flags, the first question is never "what line is wrong" but **which half is wrong**, the estimator or the planner. This assignment is built so you can answer that without guessing, and the habit is worth learning here because larger robotics systems demand it constantly.

- **Start with the tests.** Tasks 1 through 3 never touch the game. If `tests/test_state_estimation.py` passes, your model is almost certainly fine and a misbehaving agent is a Task 4 problem.
- **Watch the ghost.** The gap between the ghost and the red square is a live readout of filter quality that owes nothing to your planner. A ghost that tracks well while the agent still drives into a wall means the planner is at fault.
- **Print `variance`.** It starts near `position_stddev^2` and should shrink and level off. If it isn't shrinking, `update` isn't working; if it collapses to nearly zero, your filter has gone overconfident and will ignore new readings.
- **Turn the noise down, not off.** Copy the config and lower `position_stddev` to check your planner under easy localization. Do not set it to `0` — that isn't an easier estimation problem but a degenerate one, since a belief with zero variance would need infinite information in canonical form. Something like `2.0` gives you the isolation without breaking the model.

> [!TIP]
> Change one thing at a time and pass `--seed` to keep the maze fixed between runs.

<br>

---

| [← `Getting Started`](3-getting-started.md#getting-started) | [`Back to top`](#individual-tasks) |
| :--- | :---: |
