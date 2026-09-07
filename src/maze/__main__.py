from __future__ import annotations

from argparse import ArgumentParser
from importlib.metadata import version

from maze_core import parse_config, run, run_headless

from maze import agents

_AGENT_CLASS_NAMES = {
    "mapping": "MappingAgent",
    "localization": "LocalizationAgent",
    "slam": "SlamAgent",
}
AGENT_REGISTRY = {
    agent_id: getattr(agents, class_name)
    for agent_id, class_name in _AGENT_CLASS_NAMES.items()
    if hasattr(agents, class_name)
}


def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Path to a config file.",
    )
    parser.add_argument(
        "--agent",
        choices=AGENT_REGISTRY,
        default=next(iter(AGENT_REGISTRY)),
        help="Which agent to run.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Maze generation seed, overriding the config.",
    )
    parser.add_argument(
        "--headless",
        nargs="?",
        const=300.0,
        default=None,
        type=float,
        metavar="SECONDS",
        help="Run for SECONDS of simulated time (default: 300).",
    )
    parser.add_argument(
        "--teleop",
        action="store_true",
        help="Enable keyboard control to override actions.",
    )

    args = parser.parse_args()
    if args.headless is not None and args.headless <= 0:
        parser.error("--headless SECONDS must be positive")

    config = parse_config(args.config)

    if args.seed is not None:
        if not 0 <= args.seed <= 0xFFFFFFFF:
            parser.error("--seed must fit in an unsigned 32-bit integer")
        maze_generation = config.maze_generation
        maze_generation.seed = args.seed
        config.maze_generation = maze_generation
    if args.teleop:
        config.teleop = True

    headless_seconds = args.headless
    if config.headless and headless_seconds is None:
        headless_seconds = 300.0
    if headless_seconds is not None and config.teleop:
        parser.error("Teleop cannot be used with a headless run")

    print(f"Using maze_core version: {version('maze_core')}")
    agent_type = AGENT_REGISTRY[args.agent]
    print(f"Running {agent_type.__name__}")
    print(f"Using config: {args.config}")
    policy = agent_type()

    if headless_seconds is None:
        run(config=config, policy=policy)
    else:
        print(f"Headless evaluation for up to {headless_seconds:g} simulated seconds")
        print(run_headless(config=config, policy=policy, max_seconds=headless_seconds))

if __name__ == "__main__":
    main()
