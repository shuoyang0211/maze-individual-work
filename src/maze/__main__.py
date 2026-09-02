from argparse import ArgumentParser
from enum import StrEnum
from importlib.metadata import version

from maze_core import parse_config, run

from maze.agents import LocalizationAgent, MappingAgent


class AgentId(StrEnum):
    LOCALIZATION = "localization"
    MAPPING = "mapping"

ID_TO_AGENT = {
    AgentId.LOCALIZATION: LocalizationAgent,
    AgentId.MAPPING: MappingAgent,
}

def main():
    parser = ArgumentParser()
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Path to the config file.",
    )
    parser.add_argument(
        "--agent",
        type=AgentId,
        choices=list(AgentId),
        default=AgentId.LOCALIZATION,
        help="Which agent to use.",
    )

    args = parser.parse_args()

    config = parse_config(args.config)
    print(f"Using maze_core version: {version("maze_core")}")
    print(f"Running {args.agent.value.upper()} agent with config: {args.config}")
    run(config=config, policy=ID_TO_AGENT[args.agent]())

if __name__ == "__main__":
    main()