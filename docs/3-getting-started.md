<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Getting Started

| [`README`](../README.md#cs-1820-individual-programming-assignment-3-goblets-and-ghouls) | [`Installation`](1-installation.md#installation) | [`Game Overview`](2-game-overview.md#game-overview) | [`Getting Started`] | [`Individual Tasks`](4-individual-tasks.md#individual-tasks) |
| :---: | :---: | :---: | :---: | :---: |

<br>

Now, you should be ready to start training your own policies and testing them out on different worlds! In this file, we will introduce the various programs which you will need as you complete the assignment. As usual, we've also included a quick primer on Git and some guidance on submitting to Gradescope.

<br>

## Running code

### Using `gg`

To run the starter code, you can use the following command.

```sh
gg [-h] [--config CONFIG] [--world-file WORLD_FILE]
   [--render-policy RENDER_POLICY | --train-algo TRAIN_ALGO]
   [--out OUT] [--episode-seed EPISODE_SEED]
```

See the following for example usage. Remember that policies are specific to the worlds they were trained for. To get you started, we have also provided a default policy that you can render with `uv run gg`.

```sh
# train a policy (for the default world) using src/gg/value_iteration.py
uv run gg --train-algo value_iteration --out policies/my_policy.npz

# render your value iteration policy (in the default world)
uv run gg --render-policy policies/my_policy.npz
```

### Using fixed world YAML files

Optionally, a config's random world generation can be overridden using a fixed world file, which can either be passed as an argument to `gg` or as a field in the config. To edit your own worlds, you can run the following.

```sh
uv run scripts/creator.py [--help] (--load LOAD | --size SIZE) [--out OUT]
```

If you find yourself frequently editing configs and world files by hand, you may also be interested in `schemas/`. There, we have provided JSON schemas to help you edit and validate YAMLs within VS Code.

<br>

## More about Git

### Managing versions with Git

[Git](https://git-scm.com/) is actually a *distributed version control system*, which is to grossly simplify, a piece of software used by developers to manage different versions of their code. You can learn more about what that means and how to start using it by reading this [wonderful introduction](https://cs61.seas.harvard.edu/site/2025/git/) from Harvard professor Eddie Kohler. Here's another [straight-to-the-point guide](https://rogerdudler.github.io/git-guide/) from Roger Dudler. (There are many more guides out there.)

In a nutshell, Git allows you to *commit* snapshots of your project, and the entire history of commits is saved in your repository. Not only does this save your current progress, it also lets you view past versions of your code and revert changes without losing any data. As you start the assignment, some commands we encourage you to get comfortable with are `status`, `add`, `commit`, `log`, `diff`, `push`, and `pull`. If you only remember one thing about Git, remember to ***commit early and often***!

### Common Git workflow

The following is the most common Git workflow.

```sh
# fetch changes from the remote repo and merge them into your local repo
git pull

# begin tracking new files and stage all changes to tracked files
git add .

# save a snapshot of your staged changes to your local repo history
git commit -m "<your-message>"

# upload your commits to the remote repo
git push
```

This logs all current changes to your project in a new commit, which you and others can view in the remote repo's webpage. Importantly, you should *always* make sure your code is up-to-date with the remote, by `pull`-ing before `push`-ing any new changes. The `pull` command won't matter for the individual portion of the assignment, but it will be necessary for the group portion.

### Group programming with Git

While Git is useful for coding alone (and fetching homework assignments), where Git really shines is when many, many developers need to work together on the same codebase. You will still independently write code in your local repo. However, you can then `pull` changes that other people have made, and `push` changes for others to see. The workflow above is still the gold standard. If you are interested, you can look into the `branch`, `switch`, and `merge` commands.

### Group programming with Live Share

Another way to code with a small group of people is with the [Live Share](vscode:extension/MS-vsliveshare.vsliveshare) extension from Microsoft. This extension lets you share a single development environment with your group members in real time, which can be a convenient alternative if your group plans to code synchronously. Follow the installation and quickstart guides on the extension page to get started.

<br>

## Submitting to Gradescope

To upload your work to Gradescope, you will need to do the following.

1. Commit and push your submission code to your unique GitHub repo. Don't forget to `add` any new files you created.
2. Open Gradescope in your browser and select your assignment.
3. In the popup, select your unique repo. This will likely be at the top of the list.
4. Select `main` as your branch. This is the default setting.
5. Click `Upload`! The autograder will now test your code on Gradescope's servers.

If you don’t see your repo in the list, check that your repo's webpage reflects your most recent commit. If not, you may have forgotten to `commit` or `push`. Once the autograder finishes, you will receive an email, and you should be able to see the results in the Gradescope assignment.

<br>

---

| [← `Game Overview`](2-game-overview.md#game-overview) | [`Back to top`](#getting-started) | [`Individual Tasks` →](4-individual-tasks.md#individual-tasks) |
| :--- | :---: | ---: |
