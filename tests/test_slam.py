import pytest

from maze.agents import SlamAgent
from tests.utils import slam_results

SEEDS = tuple(range(3))
MAX_SECONDS = 300.0
MIN_FLAGS_PER_SEED = 1
MIN_MEAN_ACCURACY = 0.50


@pytest.fixture(scope="module")
def results() -> list[tuple[int, int, int, float]]:
    return slam_results(
        "configs/slam.yaml",
        SlamAgent,
        max_seconds=MAX_SECONDS,
        seeds=SEEDS,
    )


def test_slam_capture_counts(results):
    starved = [
        (seed, captured, total)
        for seed, captured, total, _ in results
        if total == 0 or captured < MIN_FLAGS_PER_SEED
    ]
    assert not starved, (
        f"Expected at least {MIN_FLAGS_PER_SEED} flag(s) captured within "
        f"{MAX_SECONDS:g} simulated seconds for every seed, but these runs fell "
        f"short: {starved}."
    )


def test_slam_mapping_recall(results):
    accuracies = [accuracy for _, _, _, accuracy in results]
    mean_accuracy = sum(accuracies) / len(accuracies)
    assert mean_accuracy >= MIN_MEAN_ACCURACY, (
        f"Expected a mean mapping accuracy of at least {MIN_MEAN_ACCURACY:.0%} "
        f"over {len(SEEDS)} seeds, but got {mean_accuracy:.2%} "
        f"(per seed: {[f'{a:.2%}' for a in accuracies]})."
    )
