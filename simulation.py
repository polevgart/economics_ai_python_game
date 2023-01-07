import attr
import collections
import copy
import logging

from rules import Board, Player, PlayerName
from strategy import BaseStrategy, BaseMove, Shoot, DirectMove

logger = logging.getLogger(__name__)


@attr.s(slots=True, kw_only=True)
class TurnDescription:
    shoots: list[tuple[PlayerName, Shoot]] = attr.ib()
    direct_moves: list[tuple[PlayerName, DirectMove]] = attr.ib()


@attr.s(slots=True, kw_only=True)
class SimulationHistory:
    initial_board: Board = attr.ib(default=None)
    log: list[TurnDescription] = attr.ib(factory=list)

    def get_step(self, index):
        if index < len(self.log):
            return self.log[index]


@attr.s(slots=True, kw_only=True)
class Simulator:
    board: Board = attr.ib(default=None)
    players: list[Player] = attr.ib(init=False)
    strategies: list[BaseStrategy] = attr.ib()
    num_of_steps: int = attr.ib()
    cur_step: int = attr.ib(default=0, init=False)
    simulation_hist: SimulationHistory = attr.ib(factory=SimulationHistory)

    @players.default
    def _(self):
        return [self.board.get_player(pname) for pname in self.board.player_names]

    @property
    def is_endgame(self):
        return not (self.cur_step < self.num_of_steps and any(map(lambda p: p.is_alive, self.players)))

    def generate_moves(self) -> TurnDescription:
        assert not self.is_endgame

        turn_desc = self.simulation_hist.get_step(self.cur_step)
        self.cur_step += 1
        if turn_desc is not None:
            return turn_desc

        state = self.board.get_state_ref()
        move_kind2player__move = collections.defaultdict(list)
        for player, strategy in zip(self.players, self.strategies):
            if not player.is_alive:
                continue

            try:
                move = strategy.get_next_move(copy.deepcopy(state))
            except Exception:
                logger.exception("Error in get_next_move")
                raise
                continue

            if not isinstance(move, BaseMove):
                logger.warning("Incorrect move %s", type(move))
                continue

            move_kind2player__move[type(move)].append((player.name, move))

        turn_desc = TurnDescription(
            shoots=move_kind2player__move.pop(Shoot, []),
            direct_moves=move_kind2player__move.pop(DirectMove, []),
        )
        self.simulation_hist.log.append(turn_desc)

        if move_kind2player__move:
            logger.warning("Unexpected move kinds: %s", move_kind2player__move)

        return turn_desc

    def handle_shoots(self, shoots: list[tuple[PlayerName, Shoot]]):
        for player_name, move in shoots:
            self.board.handle_shoot(player_name, move.dx, move.dy)

    def handle_direct_moves(self, direct_moves: list[tuple[PlayerName, DirectMove]]):
        for player_name, move in direct_moves:
            self.board.handle_direct_move(player_name, move.dx, move.dy)

    def finish_step(self):
        self.board.recharge_items()

    def step(self):
        turn_desc = self.generate_moves()
        self.handle_shoots(turn_desc.shoots)
        self.handle_direct_moves(turn_desc.direct_moves)
        self.finish_step()
