import logging

from interface import CliInterface, PygameInterface
from rules import Board
from simulation import Simulator
from strategy import *


def main():
    board = Board(
        size_x=10,
        size_y=10,
        num_of_items=20,
        num_of_players=4,
        max_health=2,
        level_map_path='maps/level.txt',
    )
    simulator = Simulator(
        board=board,
        strategies=[
            RandomStrategy(),
            RandomStrategy(),
            RandomStrategy(),
            RandomStrategy(),
        ],
        num_of_steps=2000,
    )
    # renderer = CliInterface(
    #     board=board,
    #     simulator=simulator,
    # )
    renderer = PygameInterface(
        board=board,
        simulator=simulator,
        screen_width=1000,
        screen_height=800,
        border_x=5,
        border_y=5,
        border_between_cells=5,
    )
    renderer.start_loop()


if __name__ == "__main__":
    main()
