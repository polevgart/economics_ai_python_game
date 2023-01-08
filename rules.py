import attr
import functools
import logging
from pathlib import Path
import random
import typing


__all__ = (
    "PlayerName",
    "Player",
    "Wall",
    "Bonus",
    "HealBonus",
    "PoisonBonus",
    "ScoreBonus",
    "Board",
    "State",
)


logger = logging.getLogger(__name__)


class BaseObject:
    pass


def only_if_alive(func):
    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        if self.is_alive:
            func(self, *args, **kwargs)

    return wrapped


class PlayerName(str):
    pass


@attr.s(slots=True, kw_only=True)
class Player(BaseObject):
    name: PlayerName = attr.ib()
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
    cells: list[list[typing.Optional[BaseObject]]] = attr.ib()


class PlayerNotFoundError(Exception):
    pass


@attr.s(slots=True, kw_only=True)
class Board:
    size_x: int = attr.ib()
    size_y: int = attr.ib()
    num_of_items: int = attr.ib()
    available_items: int = attr.ib(default=0)
    max_health: int = attr.ib()
    level_map_path: typing.Optional[str | Path] = attr.ib(default=None)

    cells: list[list[typing.Optional[BaseObject]]] = attr.ib(default=None, init=False)
    _name2player: dict[PlayerName, Player] = attr.ib(factory=dict, init=False)
    player_names: list[PlayerName] = attr.ib()

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

    def get_player(self, player_name: PlayerName, strict=True) -> Player | None:
        player = self._name2player.get(player_name)
        if player is None and strict:
            raise PlayerNotFoundError(f"Player {player_name} undefined")

        return player

    def _load_level_map(self):
        self.cells = []
        with open(self.level_map_path, "r") as file:
            for line in file:
                line = line.rstrip()
                if line:
                    row = [
                        None if char == "." else Wall()
                        for char in line
                    ]
                    self.cells.append(row)

        self.size_x = max(map(len, self.cells))
        for row in self.cells:
            row.extend([Wall()] * (self.size_x - len(row)))
        self.size_y = len(self.cells)

    def _generate_walls(self):
        if self.level_map_path is not None:
            try:
                self._load_level_map()
                return
            except OSError:
                logger.exception("Couldn't parse level map :(")

        self.cells = [[None] * self.size_x for _ in range(self.size_y)]
        self.cells[0] = [Wall()] * self.size_x
        self.cells[-1] = [Wall()] * self.size_x
        for i in range(self.size_y):
            self.cells[i][0] = Wall()
            self.cells[i][-1] = Wall()

    def _generate_players(self):
        for name in self.player_names:
            x, y = self.get_rand_coord_empty_cell()
            player = self.get_player(name, strict=False) or Player(name=name, x=x, y=y, max_health=self.max_health)
            self.set_cell(x, y, player)
            self._name2player[name] = player

    def _generate_items(self, count):
        for i in range(count):
            x, y = self.get_rand_coord_empty_cell()
            self.set_cell(x, y, Spawner.spawn())

        self.available_items += count

    def recharge_items(self):
        self._generate_items(self.num_of_items - self.available_items)

    def restart(self):
        self._generate_walls()
        self._generate_players()
        self._generate_items(self.num_of_items)

    def get_cell(self, x, y):
        return self.cells[y][x]

    def set_cell(self, x, y, cell):
        self.cells[y][x] = cell

    def is_empty(self, x, y):
        return self.get_cell(x, y) is None

    def can_move_to(self, x, y):
        return not isinstance(self.get_cell(x, y), (Player, Wall))

    def handle_shoot(self, player_name: PlayerName, dx: int, dy: int):
        player = self.get_player(player_name)
        x = player.x + dx
        y = player.y + dy
        while self.can_move_to(x, y):
            x += dx
            y += dy

        cell = self.get_cell(x, y)
        if isinstance(cell, Player):
            cell.damage(1)
            player.change_score(1)

    def handle_direct_move(self, player_name: PlayerName, dx: int, dy: int):
        player = self.get_player(player_name)
        x = player.x + dx
        y = player.y + dy
        if self.can_move_to(x, y):
            self.set_cell(player.x, player.y, None)
            player.move(dx, dy)
            cell = self.get_cell(player.x, player.y)
            if cell is not None:
                cell.pick(player)
                self.available_items -= 1
            self.set_cell(player.x, player.y, player)

    def get_state_ref(self) -> State:
        # cut out a square of const radius centered at the player which requested the state
        return State(cells=self.cells)


class Spawner:
    items__probs = tuple(zip(*{
        PoisonBonus: 1,
        HealBonus: 2,
        ScoreBonus: 5,
    }.items()))

    @classmethod
    def spawn(cls) -> Item:
        return random.choices(*cls.items__probs)[0]()
