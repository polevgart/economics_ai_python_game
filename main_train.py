import attr
import copy

import genetic
import util as lib_util

from perceptron import NeuralStrategy
from rules import Board
from simulation import Simulator


def individual_factory():
    return NeuralStrategy(player_name="cock")


@attr.s(slots=True, kw_only=True)
class GeneticAlgorithm(genetic.GeneticAlgorithm):
    config: dict = attr.ib()

    def ranking_phase(self, population):
        prototype_board = Board(**self.config["Board"])
        assert self.population_size % len(prototype_board.player_names) == 0

        score__individual = []
        for sample in lib_util.group(population, len(prototype_board.player_names)):
            board = copy.deepcopy(prototype_board)
            for strategy, player_name in zip(sample, board.player_names):
                strategy.player_name = player_name

            simulator = Simulator(
                board=board,
                strategies=sample,
                **self.config["Simulator"],
            )
            while not simulator.is_endgame:
                simulator.step()

            for individual in sample:
                player = board.get_player(individual.player_name)
                score = player.score if player.is_alive else -1
                score__individual.append((score, individual))

        score__individual.sort(key=lambda k: k[0], reverse=True)
        print([score for score, _ in score__individual])
        return [individual for _, individual in score__individual]


def main():
    config = lib_util.get_config()

    genetic_algorithm = GeneticAlgorithm(
        individual_factory=individual_factory,
        config=config,
        **config["GeneticAlgorithm"],
    )
    individual = genetic_algorithm.run()
    lib_util.dump_pickle_if_need(config, individual)


if __name__ == "__main__":
    main()
