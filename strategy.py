import attr
import random
import typing

from rules import State


__all__ = (
    "BaseMove",
    "DirectMove",
    "Shoot",
    "BaseStrategy",
    "RandomStrategy",
    "ExceptionStrategy",
)


class BaseMove:
    pass


@attr.s(slots=True, kw_only=True)
class DirectMove(BaseMove):
    """Направления движения. Можно стоять на месте
    """
    dx: int = attr.ib()
    dy: int = attr.ib()

    def __attrs_post_init__(self):
        assert self.dx in (1, 0, -1) and self.dy in (1, 0, -1)


@attr.s(slots=True, kw_only=True)
class Shoot(BaseMove):
    """4 стороны - направления выстрела.
    При попадании +1 очко выстрелившему и -1 хп противнику
    """
    dx: int = attr.ib()
    dy: int = attr.ib()

    def __attrs_post_init__(self):
        assert self.dx == 0 and self.dy in (1, -1) or self.dy == 0 and self.dx in (1, -1)


class BaseStrategy:
    def get_next_move(self, state: State) -> BaseMove:
        raise NotImplementedError()


class RandomStrategy(BaseStrategy):
    _possible_moves = [
        DirectMove(dx=dx, dy=dy) for dx in (-1, 0, 1) for dy in (-1, 0, 1)
    ] + [
        Shoot(dx=1, dy=0),
        Shoot(dx=-1, dy=0),
        Shoot(dx=0, dy=-1),
        Shoot(dx=0, dy=1),
    ]

    def get_next_move(self, state: State) -> BaseMove:
        return random.choice(self._possible_moves)


class GreedyStrategy(BaseStrategy):
    def get_next_move(self, state: State) -> BaseMove:
        return random.choice(self._possible_moves)


class ExceptionStrategy(BaseStrategy):
    pass
