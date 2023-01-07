import copy
import logging

import util as lib_util

from interface import CliInterface, PygameInterface  # noqa: F401
from perceptron import NeuralStrategy
from rules import Board
from simulation import Simulator, SimulationHistory
from strategy import *  # noqa

logger = logging.getLogger(__name__)


def main():
    config = lib_util.get_config()

    simulation_hist = lib_util.load_pickle_or_init(config, SimulationHistory)
    simulation_hist.initial_board = simulation_hist.initial_board or Board(**config["Board"])
    board = copy.deepcopy(simulation_hist.initial_board)

    strategy = lib_util.load_pickle(config, NeuralStrategy)
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
        num_of_steps=2000,
        simulation_hist=simulation_hist,
    )
    # renderer = CliInterface(
    #     board=board,
    #     simulator=simulator,
    # )
    renderer = PygameInterface(
        board=board,
        simulator=simulator,
        **config["PygameInterface"]
    )
    renderer.start_loop(autorun=False)
    lib_util.dump_pickle_if_need(config, simulator.simulation_hist)


if __name__ == "__main__":
    main()
