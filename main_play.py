import copy
import logging

import util as lib_util

from interface import CliInterface, PygameInterface  # noqa: F401
from rules import Board
from simulation import Simulator, SimulationHistory
from strategies.core import BaseStrategy
from strategies import strategies_registrant

logger = logging.getLogger(__name__)


def main():
    config = lib_util.get_config()

    simulation_hist = lib_util.load_pickle_or_init(config, SimulationHistory)
    simulation_hist.initial_board = simulation_hist.initial_board or Board(**config["Board"])
    board = copy.deepcopy(simulation_hist.initial_board)

    strategies = []
    if "fixed_strategies" in config:
        fixed_players = sum(config["fixed_strategies"].values())
        max_players = len(board.player_names)
        if max_players > fixed_players:
            logger.error("Config has different fixed_strategies and players on board: max players %s on board, you want players %s", max_players, fixed_players)
            exit(1)

        gen_player_names = iter(board.player_names)
        for strategy_name, cnt in config["fixed_strategies"].items():
            strategy_cls = strategies_registrant.get_participant(strategy_name)
            strategy: BaseStrategy = lib_util.load_pickle_or_init(config, strategy_cls)
            for _ in range(cnt):
                player_name = next(gen_player_names)
                named_strategy = copy.deepcopy(strategy)
                named_strategy.player_namse = player_name
                strategies.append(named_strategy)

    else:
        raise NotImplementedError("You must define fixed_strategies in config")

    simulator = Simulator(
        board=board,
        strategies=strategies,
        simulation_hist=simulation_hist,
        **config["Simulator"],
    )
    interface_class_name = config["main_interface"]
    interface_class = globals()[interface_class_name]
    interface = interface_class(
        board=board,
        simulator=simulator,
        **config.get(interface_class_name, {}),
    )
    interface.start_loop()
    lib_util.dump_pickle_if_need(config, simulator.simulation_hist)


if __name__ == "__main__":
    main()
