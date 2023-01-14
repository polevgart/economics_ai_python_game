import copy
import logging

import util as lib_util

from interface import CliInterface, PygameInterface  # noqa: F401
from strategies.neural_network import NeuralStrategy
from rules import Board
from simulation import Simulator, SimulationHistory
from strategies.core import *  # noqa

logger = logging.getLogger(__name__)


def main():
    config = lib_util.get_config()

    simulation_hist = lib_util.load_pickle_or_init(config, SimulationHistory)
    simulation_hist.initial_board = simulation_hist.initial_board or Board(**config["Board"])
    board = copy.deepcopy(simulation_hist.initial_board)

    strategy = lib_util.load_pickle(config, NeuralStrategy)
    if strategy is None:
        logger.warning("Strategy didn't loaded. A RandomStrategy will be created")
        strategy = RandomStrategy()

    strategies = []
    for i in range(4):
        named_strategy = copy.deepcopy(strategy)
        named_strategy.player_name = board.player_names[i]
        strategies.append(named_strategy)

    simulator = Simulator(
        board=board,
        strategies=strategies or [
            NeuralStrategy(player_name=board.player_names[0]),
            NeuralStrategy(player_name=board.player_names[1]),
            NeuralStrategy(player_name=board.player_names[2]),
            NeuralStrategy(player_name=board.player_names[3]),
        ],
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
