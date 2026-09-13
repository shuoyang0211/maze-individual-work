import pytest

from maze.agents import SlamAgent
from tests.utils import slam_results

SEEDS = tuple(range(4))
MAX_SECONDS = 300.0
MIN_FLAGS_PER_SEED = 1
MIN_FREE_RECALL = 0.80
MIN_WALL_RECALL = 0.30


@pytest.fixture(scope="module")
def results() -> list[tuple[int, int, int, float, float]]:
    return slam_results(
        "configs/slam.yaml",
        SlamAgent,
        max_seconds=MAX_SECONDS,
        seeds=SEEDS,
    )


def test_slam_capture_counts(results):
    starved = [
        (seed, captured, total)
        for seed, captured, total, _, _ in results
        if total == 0 or captured < MIN_FLAGS_PER_SEED
    ]
    assert not starved, (
        f"Expected at least {MIN_FLAGS_PER_SEED} flag(s) captured within "
        f"{MAX_SECONDS:g} simulated seconds for every seed, but these runs fell "
        f"short: {starved}."
    )


def test_slam_mapping_recall(results):
    free_recalls = [free_recall for _, _, _, free_recall, _ in results]
    wall_recalls = [wall_recall for _, _, _, _, wall_recall in results]
    mean_free_recall = sum(free_recalls) / len(free_recalls)
    mean_wall_recall = sum(wall_recalls) / len(wall_recalls)

    assert mean_free_recall >= MIN_FREE_RECALL, (
        f"Expected a mean free space recall of at least {MIN_FREE_RECALL:.0%} "
        f"over {len(SEEDS)} seeds, but got {mean_free_recall:.2%} "
        f"(per seed: {[f'{recall:.2%}' for recall in free_recalls]})."
    )
    assert mean_wall_recall >= MIN_WALL_RECALL, (
        f"Expected a mean wall recall of at least {MIN_WALL_RECALL:.0%} "
        f"over {len(SEEDS)} seeds, but got {mean_wall_recall:.2%} "
        f"(per seed: {[f'{recall:.2%}' for recall in wall_recalls]})."
    )
