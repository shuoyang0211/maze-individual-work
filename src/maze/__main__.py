from argparse import ArgumentParser

from maze.agents import TeleopAgent
from maze_core import run, parse_config

def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        default="configs/teleop.yaml",
        help="Path to the config file.",
    )

    args = parser.parse_args()

    config = parse_config(args.config)
    run(config=config, policy=TeleopAgent())

if __name__ == "__main__":
    main()