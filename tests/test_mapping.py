from maze.agents import MappingAgent
from tests.utils import mapping_recalls

SEEDS = tuple(range(4))
MAX_SECONDS = 300.0
MIN_FREE_RECALL = 0.85
MIN_WALL_RECALL = 0.45


def test_mapping_recall():
    free_recall, wall_recall = mapping_recalls(
        "configs/mapping.yaml",
        MappingAgent,
        max_seconds=MAX_SECONDS,
        seeds=SEEDS,
    )
    assert free_recall >= MIN_FREE_RECALL, (
        f"Expected free space recall of at least {MIN_FREE_RECALL:.0%} over "
        f"{len(SEEDS)} seeds, but got {free_recall:.2%}."
    )
    assert wall_recall >= MIN_WALL_RECALL, (
        f"Expected wall recall of at least {MIN_WALL_RECALL:.0%} over "
        f"{len(SEEDS)} seeds, but got {wall_recall:.2%}."
    )
