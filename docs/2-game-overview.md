<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Game Overview

| [`README`](../README.md#cs-1820-individual-programming-assignment-3-goblets-and-ghouls) | [`Installation`](1-installation.md#installation) | [`Game Overview`] | [`Getting Started`](3-getting-started.md#getting-started) | [`Individual Tasks`](4-individual-tasks.md#individual-tasks) |
| :---: | :---: | :---: | :---: | :---: |

<br>

In this game, the world is represented by a discrete grid of tiles, which are zero-indexed with the origin in the top-left corner. For example, in the following grid, the agent is located at `(7, 16)`. Each world is generated according to a YAML in `configs/`, which specifies the world's dimensions and uses a random seed to place agents and populate the world with walls and goblets. You can check out `configs/default.yaml` to get a sense for how worlds are generated.

<figure style="text-align: center;">
    <img src="./assets/world_structure.png" alt="The agent is shown in the default config." width="600">
    <figcaption style="font-style: italic;">
        The agent is represented by a red square. Walls are gray squares, and goblets are yellow and orange circles.
    </figcaption>
</figure>

<br>

## Agent Movement

To control the agent, you will provide a *policy* which specifies, for each position on the grid, the action that your agent will select. These actions are `Action.Up`, `Action.Right`, `Action.Down`, and `Action.Left`, which attempt to move the agent in the corresponding direction. In game, you'll be able to visualize your policy as an arrow field by pressing `P`,

But there's a catch! Unlike in previous assignments, your agent's intended action will not always be the action it actually takes. Instead, the transition function itself is stochastic in the following way. Each world's config file specifies a vector `[p_intended, p_right, p_back, p_left]` of transition probabilities, which are non-negative real numbers that sum to $1$. On each turn, your agent will:

- take the intended action with probability `p_intended`,
- slip one step clockwise with probability `p_right`,
- slip two steps clockwise, or backwards, with probability `p_back`,
- and slip three steps clockwise with probability `p_left`.

For example, if the transition is `[0.9, 0.0, 0.0, 0.1]`, then an agent that always chooses right will still randomly move up!

<figure style="text-align: center;">
    <img src="./assets/agent_movement.webp" alt="The policy field shows a rightward policy everywhere, but the agent moves up, missing two goblets." width="600">
    <figcaption style="font-style: italic;">
        The adventurer will encounter far, out-of-distribution lands.
    </figcaption>
</figure>

<br>

## Collecting Rewards

Finally, the world is populated with a set of goblets, each of which has an associated reward. Some goblets are made of fool's gold (orange) and give the adventurer zero or negative reward, while real goblets are made of real gold (yellow) and give the adventurer positive rewards. More precisely, each goblet has a reward `r`, which is an integer drawn uniformly between `-r_max` and `r_max`.  

Once the adventurer transitions into a cell containing a goblet, it immediately receives the associated reward and leaves to go cash in its prize, ending the game. We can thus formulate each world as a Markov decision process, where the state space is given by the position of the agent, and the action space, transition function, and rewards are defined as above.

<figure style="text-align: center;">
    <img src="./assets/collecting_rewards.webp" alt="The agent collects a piece of true gold, ending the game." width="600">
    <figcaption style="font-style: italic;">
        “You should enjoy the little detours to the fullest. Because that's where you'll find the things more important than what you want.” —Ging Freecss
    </figcaption>
</figure>

<br>

---

| [← `Installation`](1-installation.md#installation) | [`Back to top`](#game-overview) | [`Getting Started` →](3-getting-started.md#getting-started) |
| :--- | :---: | ---: |
