import attr

from rules import Board, Bonus, Player
from simulation import Simulator


@attr.s(slots=True, kw_only=True)
class CliInterface:
    board: Board = attr.ib()
    simulator: Simulator = attr.ib()

    def start_loop(self):
        self.render()
        while not self.simulator.is_endgame:
            input()
            print(f"Step {self.simulator.cur_step}:")
            self.simulator.step()
            self.render()

    def render(self):
        for y in range(self.board.size_y):
            for x in range(self.board.size_x):
                cell = self.board.get_cell(x, y)
                name = cell.__class__.__name__ if cell is not None else "."
                if isinstance(cell, Bonus):
                    name = cell.repr()

                if isinstance(cell, Player):
                    name = f"{cell.health}|{cell.score}"
                    name = "🎅" + name
                print(name, end="\t")
            print()
