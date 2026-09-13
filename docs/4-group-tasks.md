<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Group Tasks

| [`README`](../README.md#cs-1820-group-programming-assignment-2-maze) | [`Installation`](1-installation.md#installation) | [`Game Overview`](2-game-overview.md#game-overview) | [`Getting Started`](3-getting-started.md#getting-started) | [`Group Tasks`] |
| :---: | :---: | :---: | :---: | :---: |

<br>

Congrats on completing the individual assignment! Now, we'll be shifting to the task of *mapping*. Like a real robot, our agent doesn't already know its environment. Instead, the environment is exposed through simulated *raycasts* that probe the area around the agent for nearby obstacles. Your goal is to use these readings to build a two-dimensional *occupancy grid* of the entire maze. Lastly, you will combine this map with your localization into a SLAM agent that can do both!

<br>

## Task 1: Occupancy mapping

From now on, none of your agents will be allowed to see the true occupancy grid. Your agent must now maintain *logits* for each cell (one for each of free space, wall, flag, and capture point), which are converted into probabilities using a softmax. In [`mapping/occupancy_mapping.py`](../src/maze/mapping/occupancy_mapping.py), you will implement two helpers, which your agents will use to update the occupancy grid.

- `update_cell` updates the logits and assignment of a single cell using one sensor observation.
- `update_grid` takes a list of raycasts and determines the cells along them to update.

> [!TIP]
> The logits are clamped to a fixed range around zero for numerical stability. Because a softmax is unchanged by adding a constant to every logit, we recommend centering the log-likelihoods before adding them, so that your logits don't drift towards the clamp. You'll also want to make use of `mapping/utils.py`.

<br>

## Task 2: A mapping agent

Time for another agent! In [`agents/mapping_agent.py`](../src/maze/agents/mapping_agent.py), you will be implementing a *mapping* agent, which must build a representation of the environment from range-based observations. On each tick, your agent will use your helpers in Task 1 to update its beliefs about the world. Then, your task is to simply build an agent which explores the entire world and builds a good map. Note that in `configs/mapping.yaml`, there is no position noise and there are no flags, so the only thing that limits you is where you choose to go. We've also written a test in `tests/test_mapping.py` that benchmarks your agent based on the proportions of free spaces and walls it correctly maps.

> [!TIP]
> You can press `C` to view your agent's occupancy grid, and `T` to see the true grid. We also recommend using `--teleop` to observe your mapping algorithm in action. Since your policy still runs, the occupancy grid will continue to update, but the policy's movements will be ignored in favor of your keyboard inputs.

<br>

## Task 3: A SLAM agent

You should now have two agents which are individually able to:

1. Localize itself and capture flags given a perfect map of the environment.
2. Map the environment given a perfect position estimate.

Our final goal is thus: we want a single agent that can simultaneously localize and map. In [`agents/slam_agent.py`](../src/maze/agents/slam_agent.py), your goal is to create a SLAM agent for `configs/slam.yaml`. You should have a lot of components from both portions of the assignment that you can glue together. However, there are many new challenges that come with knowing *neither* our own position nor the environment.

In `tests/test_slam.py`, your agent will be benchmarked by *both* how many flags it captures and how much of the map it gets right. (For this reason, we also ask that your SLAM agent continues mapping even if it has collected all flags.) As a group, you're also invited to further improve both the localization and mapping parts of the code, or to make new improvements for the simultaneous agent. These may improve your score on the Gradescope leaderboard, but no specific additions are required. We've included a list of potential starting points.

> <details><summary><b>Suggestions</b></summary>
>
> - **Detect poor estimates.** How do you know when your position estimate is wrong? How does that change your grid update, or your policy?
>
> - **Use the filter covariance.** How might you use your Kalman filter covariance matrix, in addition to its mean?
>
> - **Implement scan matching.** Can you use raycasts to also help you estimate your position?
>
> - **Try alternative filters.** How would alternative localization methods (e.g. particle filters) perform?
>
> - **Modify the logit update.** How might you change the logit update, so that cells you correctly detect as walls aren't being reassigned as free spaces?
>
> - **Utilize the maze structure.** Can you leverage the fact that walls in our maze tend to extend in a given direction for a long time?
>
> </details>

<br>

## Written task

In the group portions of these assignments, we hope you can engage with the course content more deeply while also learning from your peers. Therefore, we ask that you submit a short reflection (about 1–2 pages, in any format you like) detailing what you tried, what ideas worked well, and what didn't go as planned. We're more interested in the process than the result! For this assignment specifically, we ask that your write-up also answers the following questions:

1. How did your SLAM agent perform at first? Were there any new problems that didn't appear when you only had to do localization or mapping alone?

2. Briefly summarize the approach you took for mapping, for localization, and for combining them into SLAM. How did you apply the ideas from class? Were there any novel ideas that you found successful?

3. What ideas didn't work as you expected, and why do you think this was the case? Were there any catastrophic failures?

4. Can you describe your agent's final policy at a high level? What choices does it make to handle noisy measurements?

5. Did you use AI to aid in the development of your agent? If so, explain how you used it and summarize its contributions in your report. We also ask that you provide transcripts of all your conversations in a `prompts/` directory.

6. Provide a short summary of each team member's contributions.

Feel free to add any other information you would like us to know. Pictures, code snippets, and comments are highly appreciated. Before submitting, you can include your final report as a `writeup.pdf` file at the root of this repository.

<br>

---

| [← `Getting Started`](3-getting-started.md#getting-started) | [`Back to top`](#group-tasks) |
| :--- | :---: |
