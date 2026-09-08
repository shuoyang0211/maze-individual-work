<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Group Tasks

| [`README`](../README.md#cs-1820-group-programming-assignment-2-maze) | [`Installation`](1-installation.md#installation) | [`Game Overview`](2-game-overview.md#game-overview) | [`Getting Started`](3-getting-started.md#getting-started) | [`Group Tasks`] |
| :---: | :---: | :---: | :---: | :---: |

<br>

Congrats on completing the individual assignment! Now, we'll be shifting to the task of *mapping*. Like a real robot, our agent doesn't already know its environment! Instead, the environment is exposed through simulated *raycasts* that report the distance to the nearest obstacle in several directions around the agent. Your goal is to use these readings to update a two-dimensional *occupancy grid*, in order to fully map out the maze.

<br>

## Task 1: Occupancy mapping

First, we'll write some helper functions that you will need for your mapping and SLAM agents. Now, your agents will no longer have access to the true occupancy grid. In [`mapping/occupancy_mapping.py`](../src/maze/mapping/occupancy_mapping.py), you

<br>

## Task 2: A mapping agent


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

## Task 3: SLAM

One more agent to go!

<br>

## Written task

In the group assignment, we want to put these two parts together to produce an agent that is able to simultaneously localize and map! Given the `LocalizationAgent` and `MappingAgent` from the previous assignment this should be near immediate. Glue together your `LocalizationAgent` and `MappingAgent` implementations to produce an agent who is able to SLAM and capture all of the flags in the map.

Our SLAM implementation is far from perfect, however! As a group, you're invited to make improvements in both the localization and mapping parts of the code to improve the performance of your agent. These improvements are not required for this portion of the assignment, but can improve your score on the Gradescope leaderboard. Possible starting places include:

-   In the localization code, we neglect using the raycasts to localize our agent. Once we have an accurate map, using the raycasts can improve our localization estimate! Alternatively, we explored using Kalman filters for localization, but how would alternative localization methods (i.e. particle filters) perform?
-   In the mapping code, you may have noticed that cells that were previously assigned walls become free as the agent moves. This is to be expected since we are approximating our rays on a discrete grid, and therefore, sometimes the ray may go through a cell that has a wall but not hit the wall at that point. To combat this, you might want to change how logits are updated when a class becomes very likely. Furthermore, is it possible to leverage the fact that often times in our maze the walls tend to extend in a given direction for a long time?

In a short writeup, describe what you did and tried on this assignment. This is a chance to reflect on your approach and design choices, not a formal report — bullet points are fine.

Please address the following for each task:

-   **What you implemented.** Briefly summarize the approach you took for mapping, localization, and the factor graph.
-   **What you tried that didn't work.** Design choices you explored and abandoned, bugs that took a while to track down, or parameter values that gave bad results and why you think they did.

You are also welcome to include plots, screenshots, or short snippets of code that illustrate what you're describing. Submit the writeup as a markdown file 

Feel free to post on Ed or stop by office hours if you have any questions/want to brainstorm ideas!

<br>

---

| [← `Getting Started`](3-getting-started.md#getting-started) | [`Back to top`](#group-tasks) |
| :--- | :---: |
