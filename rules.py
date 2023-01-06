import attr
import random
import typing
import functools


__all__ = (
    "Player",
    "Bonus",
    "Wall",
    "HealBonus",
    "PoisonBonus",
    "ScoreBonus",
    "Board",
    "State",
)


class BaseObject:
    pass


def only_if_alive(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        if self.is_alive:
            func(self, *args, **kwargs)

    return wrapped


@attr.s(slots=True, kw_only=True)
class Player(BaseObject):
    x: int = attr.ib()
    y: int = attr.ib()

    max_health: int = attr.ib()
    health: int = attr.ib(default=None, init=False)
    score: int = attr.ib(default=0, init=False)

    def __attrs_post_init__(self):
        self.reset()

    def reset(self):
        self.health = self.max_health
        self.score = 0

    @property
    def is_alive(self):
        return self.health > 0

    @only_if_alive
    def heal(self, amount: int):
        self.health = min(self.health + amount, self.max_health)

    @only_if_alive
    def damage(self, amount: int):
        self.health = max(0, self.health - amount)

    @only_if_alive
    def change_score(self, diff: int):
        self.score += diff

    @only_if_alive
    def move(self, dx, dy):
        self.x += dx
        self.y += dy


@attr.s(slots=True, kw_only=True)
class Wall(BaseObject):
    _singleton = None

    def __new__(cls):
        if cls._singleton is None:
            cls._singleton = super(Wall, cls).__new__(cls)

        return cls._singleton


@attr.s(slots=True, kw_only=True)
class Item(BaseObject):
    pass


@attr.s(slots=True, kw_only=True)
class Bonus(Item):
    value: int = attr.ib()
    repr_symbol = "?"

    @value.default
    def _generate_value(self):
        return random.choices(*self._values__probs)[0]

    def pick(self, player: Player):
        raise NotImplementedError()

    def repr(self):
        return self.repr_symbol * self.value


@attr.s(slots=True, kw_only=True)
class ScoreBonus(Bonus):
    # -3: 1, -2: 2, -1: 3
    _values__probs = tuple(zip(*{1: 3, 2: 2, 3: 1}.items()))
    repr_symbol = "💰"

    def pick(self, player: Player):
        player.change_score(self.value)


@attr.s(slots=True, kw_only=True)
class HealBonus(Bonus):
    _values__probs = tuple(zip(*{1: 3, 2: 2, 3: 1}.items()))
    repr_symbol = "🍏"

    def pick(self, player: Player):
        player.heal(self.value)


@attr.s(slots=True, kw_only=True)
class PoisonBonus(Bonus):
    _values__probs = tuple(zip(*{1: 3, 2: 2, 3: 1}.items()))
    repr_symbol = "💀"

    def pick(self, player: Player):
        player.damage(self.value)


@attr.s(slots=True, kw_only=True)
class State:
    cells: list[list[BaseObject]] = attr.ib()


@attr.s(slots=True, kw_only=True)
class Board:
    size_x: int = attr.ib()
    size_y: int = attr.ib()
    num_of_items: int = attr.ib()
    cells: list[list[typing.Optional[BaseObject]]] = attr.ib(default=None, init=False)
    num_of_players: int = attr.ib()
    players: list[Player] = attr.ib(default=None, init=False)
    max_health: int = attr.ib()

    def __attrs_post_init__(self):
        self.restart()

    def get_rand_coord(self):
        x = random.randint(1, self.size_x - 2)
        y = random.randint(1, self.size_y - 2)
        return x, y

    def get_rand_coord_empty_cell(self):
        x, y = self.get_rand_coord()
        while not self.is_empty(x, y):
            x, y = self.get_rand_coord()

        return x, y

    def restart(self):
        self.cells = [[None] * self.size_x for _ in range(self.size_y)]
        self.cells[0] = [Wall()] * self.size_x
        self.cells[-1] = [Wall()] * self.size_x
        for i in range(self.size_y):
            self.cells[i][0] = Wall()
            self.cells[i][-1] = Wall()

        self.players = []
        for _ in range(self.num_of_players):
            x, y = self.get_rand_coord_empty_cell()
            player = Player(x=x, y=y, max_health=self.max_health)
            self.set_cell(x, y, player)
            self.players.append(player)

        for i in range(self.num_of_items):
            x, y = self.get_rand_coord_empty_cell()
            self.set_cell(x, y, Spawner.spawn())

    def get_cell(self, x, y):
        return self.cells[y][x]

    def set_cell(self, x, y, cell):
        self.cells[y][x] = cell

    def is_empty(self, x, y):
        return self.get_cell(x, y) is None

    def can_move_to(self, x, y):
        return not isinstance(self.get_cell(x, y), (Player, Wall))

    def handle_shoot(self, player, dx, dy):
        x = player.x + dx
        y = player.y + dy
        while self.can_move_to(x, y):
            x += dx
            y += dy

        cell = self.get_cell(x, y)
        if isinstance(cell, Player):
            cell.damage(1)
            player.change_score(1)

    def handle_direct_move(self, player, dx, dy):
        x = player.x + dx
        y = player.y + dy
        if self.can_move_to(x, y):
            self.set_cell(player.x, player.y, None)
            player.move(dx, dy)
            self.set_cell(player.x, player.y, player)

    def get_state(self) -> State:
        return State(cells=self.cells)


class Spawner:
    items__probs = tuple(
        zip(
            *(
                (PoisonBonus, 1),
                (HealBonus, 1),
                (ScoreBonus, 1),
            )
        )
    )

    @classmethod
    def spawn(cls) -> Item:
        return random.choices(*cls.items__probs)[0]()
