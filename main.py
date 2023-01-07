import argparse
import copy
import logging
import pickle
import yaml

from interface import CliInterface, PygameInterface
from perceptron import NeuralStrategy
from rules import Board
from simulation import Simulator, SimulationHistory
from strategy import *


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to yaml config")
    return parser.parse_args()


def load_pickle_or_init(config, cls: type):
    pickle_filename = config.get("load_pickle", {}).get(cls.__name__)
    if not pickle_filename:
        return cls(**config.get(cls.__name__, {}))

    with open(pickle_filename, "rb") as fin:
        return pickle.load(fin)


def dump_pickle_if_need(config, object):
    pickle_filename = config.get("dump_pickle", {}).get(object.__class__.__name__)
    if not pickle_filename:
        return

    with open(pickle_filename, "wb") as fout:
        pickle.dump(object, fout)


def main():
    args = parse_args()
    with open(args.config) as fin:
        config = yaml.safe_load(fin)

    simulation_hist = load_pickle_or_init(config, SimulationHistory)
    simulation_hist.initial_board = simulation_hist.initial_board or Board(**config["Board"])
    board = copy.deepcopy(simulation_hist.initial_board)

    simulator = Simulator(
        board=board,
        strategies=[
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
    renderer.start_loop()
    dump_pickle_if_need(config, simulator.simulation_hist)


if __name__ == "__main__":
    main()
