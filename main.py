import logging

from rules import Board
from strategy import *
from simulation import Simulator
from cli import CliInterface
from pygame_interface import PygameInterface



def main():
    board = Board(
        size_x=10,
        size_y=10,
        num_of_items=20,
        num_of_players=4,
        max_health=2,
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
        screen_width=500,
        screen_height=500,
        border_x=5,
        border_y=5,
        border_between_cells=5,
    )
    renderer.start_loop()


if __name__ == "__main__":
    main()
