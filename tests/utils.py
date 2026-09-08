from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Any

from maze_core import GameResult, parse_config, run_headless


def game_loop(
    filename: str | Path,
    agent_class: type[Any],
    max_seconds: float,
    maze_seed: int | None = None,
) -> GameResult:
    """Run an agent headlessly and return its evaluation metrics.

    Parameters:
        `filename`: Path to the YAML maze configuration.
        `agent_class`: Agent class to evaluate.
        `max_seconds`: Simulated-time budget for the run.
        `maze_seed`: Optional fixed seed to use instead of the config's seed.

    Returns:
        The result of the game.
    """
    config = parse_config(str(filename))
    if maze_seed is not None:
        config.seed = maze_seed
    agent = agent_class()
    result = run_headless(config=config, policy=agent, max_seconds=max_seconds)
    if result.policy_error is not None:
        raise RuntimeError(result.policy_error)
    return result


def _run_mapping_trial(
    args: tuple[str | Path, type[Any], float, int],
) -> tuple[int, int, int, int]:
    """Return correct and total counts for free and wall cells in one trial."""
    result = game_loop(*args)
    return (*result.free_recall_cells, *result.wall_recall_cells)


def mapping_recalls(
    filename: str | Path,
    agent_class: type[Any],
    max_seconds: float,
    seeds: Sequence[int],
    max_workers: int = 8,
) -> tuple[float, float]:
    """Return Free Space and Wall recall over a set of fixed maze seeds."""
    if not seeds:
        raise ValueError("seeds must not be empty")

    trials = [(filename, agent_class, max_seconds, seed) for seed in seeds]
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        counts = list(executor.map(_run_mapping_trial, trials, chunksize=1))

    free_correct = sum(count[0] for count in counts)
    free_total = sum(count[1] for count in counts)
    wall_correct = sum(count[2] for count in counts)
    wall_total = sum(count[3] for count in counts)
    if free_total == 0 or wall_total == 0:
        raise ValueError("each maze must contain Free Space and Wall cells")
    return free_correct / free_total, wall_correct / wall_total


def _run_localization_trial(
    args: tuple[str | Path, type[Any], float, int],
) -> tuple[int, int, int]:
    result = game_loop(*args)
    return args[-1], result.captured_flags, result.total_flags


def flag_capture_counts(
    filename: str | Path,
    agent_class: type[Any],
    max_seconds: float,
    seeds: Sequence[int],
    max_workers: int = 8,
) -> list[tuple[int, int, int]]:
    """Return ``(seed, captured, total)`` flag counts for each fixed seed."""
    if not seeds:
        raise ValueError("seeds must not be empty")

    trials = [(filename, agent_class, max_seconds, seed) for seed in seeds]
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(_run_localization_trial, trials, chunksize=1))


def _run_slam_trial(
    args: tuple[str | Path, type[Any], float, int],
) -> tuple[int, int, int, float]:
    result = game_loop(*args)
    return args[-1], result.captured_flags, result.total_flags, result.mapping_accuracy


def slam_results(
    filename: str | Path,
    agent_class: type[Any],
    max_seconds: float,
    seeds: Sequence[int],
    max_workers: int = 8,
) -> list[tuple[int, int, int, float]]:
    """Return ``(seed, captured, total, mapping_accuracy)`` for each fixed seed."""
    if not seeds:
        raise ValueError("seeds must not be empty")

    trials = [(filename, agent_class, max_seconds, seed) for seed in seeds]
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        return list(executor.map(_run_slam_trial, trials, chunksize=1))
