import attr
import itertools

from rules import Board, Bonus, Player
from simulation import Simulator, TurnDescription


@attr.s(slots=True, kw_only=True)
class CliInterface:
    board: Board = attr.ib()
    simulator: Simulator = attr.ib()

    def start_loop(self):
        self.render()
        while not self.simulator.is_endgame:
            input()
            print(f"Step {self.simulator.cur_step}:")
            turn_desc = self.simulator.step()
            self.render_turn_desc(turn_desc)
            self.render()

    def render_turn_desc(self, turn_desc: TurnDescription):
        for player_name, move in itertools.chain(turn_desc.shoots, turn_desc.direct_moves):
            player = self.board.get_player(player_name)
            print(f"{player} make move {move}")

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
