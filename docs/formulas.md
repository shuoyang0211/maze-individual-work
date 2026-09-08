<!--
========================================================================================================================

    This is a Markdown file. If you're using VS Code, right-click the filename and select "Open Preview" to render it!

========================================================================================================================
-->

# Formulas

| [`Preliminaries`](#preliminaries) | [`Kalman Filter`](#kalman-filter) | [`Factor Graphs`](#factor-graphs) |
| :---: | :---: | :---: |

<br>

This file contains definitions and formulas relevant to the state estimation tasks.

<br>

## Preliminaries

We wish to estimate an unobserved hidden state from a stream of noisy measurements of it. We assume the system is *linear-Gaussian*, which involves the following objects at each time step $k$.

| Object | Definition |
| --- | --- |
| $x_k$ | true (hidden) state |
| $\hat{x}_k$ | mean of our belief about $x_k$ |
| $P_k$ | covariance of our belief about $x_k$ |
| $u_k$ | known control input applied over the step |
| $z_k$ | observed measurement |
| $w_k$ | process noise, i.e., how wrong $F$ and $u_k$ turn out to be |
| $v_k$ | measurement noise, i.e., how wrong $z_k$ turns out to be |
| $F$ | state-transition model, mapping the previous state to the current one |
| $H$ | observation model, mapping a state to the measurement it would produce |
| $Q$ | covariance of the process noise $w_k$ |
| $R$ | covariance of the measurement noise $v_k$ |

The state evolves and is observed according to

$$
x_k = F x_{k-1} + u_k + w_k, \qquad w_k \sim \mathcal{N}(0, Q),
$$

$$
z_k = H x_k + v_k, \qquad v_k \sim \mathcal{N}(0, R),
$$

These assumptions are convenient because of the following. If our initial belief is Gaussian, then a Gaussian pushed through a linear map stays Gaussian, and a Gaussian conditioned on a linear-Gaussian observation stays Gaussian as well. So tracking the belief at every step requires only a mean and a covariance rather than an arbitrary distribution.

<br>

## Kalman Filter

The filter alternates between a *predict* step, which advances the belief through the transition model, and an *update* step, which corrects it with a measurement. In prediction, we advance the mean by the motion model and inflate the covariance by the process noise.

$$
\hat{x} \leftarrow F \hat{x} + u, \qquad P \leftarrow F P F^\top + Q.
$$

In the update, we compare the measurement to what the belief predicted, then move toward it in proportion to how much each side is trusted.

$$
y = z - H\hat{x}, \qquad S = H P H^\top + R, \qquad K = P H^\top S^{-1},
$$

$$
\hat{x} \leftarrow \hat{x} + K y, \qquad P \leftarrow (I - K H) P.
$$

Here, $y$ is the *innovation*, or how wrong the prediction turned out to be; $S$ is its covariance, or how surprising an error of that size should be; and $K$ is the *Kalman gain*, which decides how far toward the measurement to move. Note that $K$ depends only on the ratio between $P$ and $R$, so the balance between trusting the prediction and trusting the measurement is determined by $Q$ and $R$.

<br>

## Factor Graphs

A factor graph represents a joint distribution as a product of *factors*, each a potential over some subset of the *variables*. For Gaussian potentials, it is convenient to write each factor in *canonical form* (also called information form), parameterized by an information matrix $\Lambda$ and information vector $\eta$,

$$
\phi(x) \propto \exp\biggl(-\frac{1}{2}x^\top \Lambda x + \eta^\top x\biggr),
$$

which relates to the usual mean and covariance by $\Lambda = \Sigma^{-1}$ and $\eta = \Sigma^{-1}\mu$.

### Building factors

Each factor comes from one piece of the model. A Gaussian prior over a single variable, and a Gaussian likelihood treated as a factor over the state it observes, have canonical parameters

$$
\mathcal{N}(\mu, \Sigma): \quad \Lambda = \Sigma^{-1}, \qquad \eta = \Sigma^{-1}\mu,
$$

$$
\mathcal{N}(z; Hx, R): \quad \Lambda = H^\top R^{-1} H, \qquad \eta = H^\top R^{-1} z.
$$

A linear-Gaussian *conditional* $x_\text{curr} \mid x_\text{prev} \sim \mathcal{N}(F x_\text{prev} + u,\, Q)$ is instead a factor over both variables at once, with potential

$$
\phi(x_\text{prev}, x_\text{curr}) \propto \exp\biggl(-\frac{1}{2}\bigl(x_\text{curr} - F x_\text{prev} - u\bigr)^\top Q^{-1} \bigl(x_\text{curr} - F x_\text{prev} - u\bigr)\biggr),
$$

whose $\Lambda$ and $\eta$ are taken over the stacked vector $[x_\text{prev}, x_\text{curr}]^\top$.

### Combining factors

Multiplying factors adds their canonical parameters. In other words, the product of factors $\phi_1, \dots, \phi_n$ has

$$
\Lambda = \sum_{i=1}^{n} \Lambda_i, \qquad \eta = \sum_{i=1}^{n} \eta_i.
$$

### Eliminating a variable

Marginalizing a variable out of a factor is done via the *Schur complement*. Partition $\Lambda$ and $\eta$ into the block $a$ belonging to the variable being eliminated and the block $b$ belonging to all remaining variables.

$$
\Lambda = \begin{bmatrix} \Lambda_{aa} & \Lambda_{ab} \\ \Lambda_{ba} & \Lambda_{bb} \end{bmatrix},
\qquad
\eta = \begin{bmatrix} \eta_a \\ \eta_b \end{bmatrix}.
$$

Integrating $x_a$ out leaves a factor over the remaining variables with

$$
\Lambda' = \Lambda_{bb} - \Lambda_{ba}\Lambda_{aa}^{-1}\Lambda_{ab},
\qquad
\eta' = \eta_b - \Lambda_{ba}\Lambda_{aa}^{-1}\eta_a.
$$

<br>

---

| [`Back to top`](#formulas) |
| :---: |
