from collections import deque
from typing import Deque

from rules import State, Wall, Player


class ExtendedState:
    """More convenient State, containing current player and other players."""

    def __init__(self, state: State, player_name: str):
        self.cells = state.cells
        self.size_y = len(self.cells)
        self.size_x = len(self.cells[0])

        self.player: Player
        self.other_players: list[Player] = []
        for y in range(self.size_y):
            for x in range(self.size_x):
                cell = self.get_cell(x=x, y=y)
                if isinstance(cell, Player):
                    if cell.name == player_name:
                        self.player = cell
                    else:
                        self.other_players.append(cell)

    def get_cell(self, *, x: int, y: int):
        return self.cells[y][x]

    def set_cell(self, cell, *, x: int, y: int):
        self.cells[y][x] = cell


class ReachabilityGraphCell:
    """Element of a 'ReachabilityGraph'.

    Contains distance to the corresponding cell and direction *from* the previous cell
    (which also contains direction from its previous cell,
    so one can construct full path from the original cell).

    'visited' flag indicated whether this cell is reachable (False means unreachable)
    """

    def __init__(self, dist: int = 0, dx: int = 0, dy: int = 0, visited: bool = False):
        self.dist: int = dist
        self.dx: int = dx
        self.dy: int = dy
        self.visited: bool = visited


class ReachabilityGraph:
    """Calculates distance and path from state.player to all other cells.

    ReachabilityGraph is being constructed once per each turn and then is being used in algorithms
    that require some kind of movement on the board.
    """

    def __init__(self, state: ExtendedState):
        """Constructing a ReachabilityGraph from State"""
        self.size_x = state.size_x
        self.size_y = state.size_y
        self.graph: list[list[ReachabilityGraphCell]] = [
            [ReachabilityGraphCell() for _ in range(state.size_x)]
            for _ in range(state.size_y)
        ]

        self._fill_graph(state, state.player.x, state.player.y)

    def _fill_graph(self, state: ExtendedState, start_x: int, start_y: int):
        # Iterative function for filling graph cells (BFS)
        self.set_cell(ReachabilityGraphCell(dist=0, visited=True), x=start_x, y=start_y)

        cells: Deque[tuple[int, int, int]] = deque()
        cells.append((start_x, start_y, 1))
        while cells:
            x, y, dist = cells.popleft()

            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    new_x, new_y = x + dx, y + dy
                    if (not isinstance(state.get_cell(x=new_x, y=new_y), (Player, Wall)) and
                            not self.get_cell(x=new_x, y=new_y).visited):
                        cells.append((new_x, new_y, dist + 1))
                        self.set_cell(ReachabilityGraphCell(dist=dist, dx=dx, dy=dy, visited=True), x=new_x, y=new_y)

    def show(self) -> str:
        str_size: int = 12
        s = ''
        for y in range(self.size_y):
            for x in range(self.size_x):
                cell = self.get_cell(x=x, y=y)
                cell_str = f'{cell.dist} ({cell.dx}, {cell.dy})' if cell.visited else ''
                s += cell_str.ljust(str_size) + ' | '
            s += '\n'
        return s

    def get_direction_to(self, x: int, y: int) -> tuple[int, int]:
        """Calculates direction from the original cell to a given cell."""
        cell = self.get_cell(x=x, y=y)
        while cell.dist > 1:
            x -= cell.dx
            y -= cell.dy
            cell = self.get_cell(x=x, y=y)

        return cell.dx, cell.dy

    def get_cell(self, *, x: int, y: int) -> ReachabilityGraphCell:
        return self.graph[y][x]

    def set_cell(self, cell: ReachabilityGraphCell, *, x: int, y: int):
        self.graph[y][x] = cell
