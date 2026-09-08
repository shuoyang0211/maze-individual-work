from maze.agents import LocalizationAgent
from tests.utils import flag_capture_counts

SEEDS = tuple(range(3))
MAX_SECONDS = 300.0


def test_localization_capture_counts():
    flag_counts = flag_capture_counts(
        "configs/localization.yaml",
        LocalizationAgent,
        max_seconds=MAX_SECONDS,
        seeds=SEEDS,
    )
    incomplete = [
        (seed, captured, total)
        for seed, captured, total in flag_counts
        if total == 0 or captured < total
    ]
    assert not incomplete, (
        f"Expected all flags to be captured within {MAX_SECONDS:g} simulated seconds "
        f"for every seed, but incomplete runs were: {incomplete}."
    )
