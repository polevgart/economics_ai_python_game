import attr
import collections
import copy
import logging

from rules import Board, Player
from strategy import BaseStrategy, BaseMove, Shoot, DirectMove

logger = logging.getLogger(__name__)


@attr.s(slots=True, kw_only=True)
class Simulator:
    board: Board = attr.ib()
    players: list[Player] = attr.ib(init=False)
    strategies: list[BaseStrategy] = attr.ib()
    num_of_steps: int = attr.ib()
    cur_step: int = attr.ib(default=0, init=False)

    @players.default
    def _(self):
        return self.board.players

    @property
    def is_endgame(self):
        return not (self.cur_step < self.num_of_steps and any(map(lambda p: p.is_alive, self.players)))

    def step(self):
        assert not self.is_endgame
        self.cur_step += 1
        state = self.board.get_state()
        move_kind2player__move = collections.defaultdict(list)
        for player, strategy in zip(self.players, self.strategies):
            try:
                move = strategy.get_next_move(copy.deepcopy(state))
            except Exception:
                logger.exception("Error in get_next_move")
                continue

            if not isinstance(move, BaseMove):
                logger.warning("Incorrect move %s", type(move))
                continue

            move_kind2player__move[type(move)].append((player, move))

        for player, move in move_kind2player__move.pop(Shoot, []):
            self.board.handle_shoot(player, move.dx, move.dy)

        for player, move in move_kind2player__move.pop(DirectMove, []):
            self.board.handle_direct_move(player, move.dx, move.dy)

        if move_kind2player__move:
            logger.warning("Unexpected move kinds: %s", move_kind2player__move)
