<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Individual Tasks

| [`README`](../README.md#cs-1820-individual-programming-assignment-3-goblets-and-ghouls) | [`Installation`](1-installation.md#installation) | [`Game Overview`](2-game-overview.md#game-overview) | [`Getting Started`](3-getting-started.md#getting-started) | [`Individual Tasks`] |
| :---: | :---: | :---: | :---: | :---: |

<br>

## Task 1: Value Iteration

First, you will implement *value iteration*, a model-based planning (or dynamic programming) algorithm. Given a known model of the environment, which includes the transition probabilities and rewards, we evaluate all possible outcomes in order to plan an optimal policy, without ever interacting with the game.

More specifically, we start with an (arbitrary) estimate of the optimal value function, which we improve recursively via the Bellman optimality update. Once our estimate converges, we then compute the greedy policy for our estimate, yielding the optimal policy with respect to the known model. In [`value_iteration.py`](../src/gg/value_iteration.py), you will implement three key functions.

1. `bellman_update()` - Updates a value estimate using the Bellman update.
2. `extract_policy()` - Extracts the optimal policy from a value estimate.
3. `train()` - Orchestrates the full training loop.

<br>

> <details><summary><b>Tips</b></summary>
>
> - Although value iteration is guaranteed to converge from any estimate, we recommend starting with an all-zero estimate.
>
> - To loop over the space of agent positions, you should use `GameState.all_states()`.
>
> - To traverse the game tree, you can use `GameState.next_state()`, which takes a *realized* action and deterministically produces the next state. You can then probe this state via `GameState.reward` and `GameState.done`. Since actions are stochastic, you will need to account for the probability of each realized action in your Bellman update.
>
> - Note that `array2 = array1` aliases the same array. To create a distinct array in memory, you can use `array.copy()`.
>
> - Make sure to declare the `dtype` of your arrays: value function entries must be `np.float32` values, and policy entries must be `Action` values.
>
> - You can use the `tdqm` package to track the progress of your training loops!
>
> </details>

<br>

## Task 2: $Q$-learning

Now, it's time to start learning! Your next task is to implement $Q$-learning, a model-free reinforcement learning algorithm. Unlike in planning, we are *not* given a model for the environment, nor do we try to estimate one. Instead, the agent *learns from experience* by choosing where to explore and observing transitions in the game.

More specifically, the agent maintains an estimate of the optimal action-value function, which it updates by sampling environment transitions and performing sample-based Bellman backups. Because $Q$-learning updates via noisy samples, we train for a fixed number of episodes rather than waiting for a convergence criterion. In [`q_learning.py`](../src/gg/q_learning.py), you will again implement three key functions.

1. `run_episode()` - Updates an action-value estimate using one episode rollout.
2. `extract_policy()` - Extracts the optimal policy from an action-value estimate.
3. `train()` - Orchestrates the full training loop.

Since we no longer assume a model of the environment, your implementation should *not* use `GGConfig` or `GameState.board`, except to fetch `GameState.board.width` and `GameState.board.height` for initializing value and policy arrays.

<br>

> <details><summary><b>Tips</b></summary>
>
> - At the beginning of each episode, use `GameState.reset()` to generate a fresh episode seed. Otherwise, your policy may overfit to a single episode's randomness.
>
> - To traverse the game tree, you can use `GameState.step()`, which takes an *intended* action and stochastically produces the next state. Unlike value iteration, you will only be able to observe a single state following your chosen action. Your $Q$ update will also need to handle terminal states specially.
>
> - If `np.argmax` encounters a tie, it always takes the first among the tied elements. To avoid directional bias when selecting actions, you might want to create a helper which computes an argmax with random tie breaks.
>
> - If you want to make training reproducible, you can specify a training seed hyperparameter and use one `np.random.Generator` to sample reset seeds and make random choices.
>
> </details>

<br>

---

| [← `Getting Started`](3-getting-started.md#getting-started) | [`Back to top`](#individual-tasks) |
| :--- | :---: |
