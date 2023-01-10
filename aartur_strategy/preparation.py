from rules import State, Wall, Player


class AdvancedState:
    """More convenient State, containing current player and other players."""

    def __init__(self, state: State, player_name: str):
        self.cells = state.cells
        self.size_y = len(self.cells)
        self.size_x = len(self.cells[0])

        self.player: Player
        self.other_players: list[Player] = []
        for y in range(self.size_y):
            for x in range(self.size_x):
                cell = self.cells[y][x]
                if isinstance(cell, Player):
                    if cell.name == player_name:
                        self.player = cell
                    else:
                        self.other_players.append(cell)

    def __getitem__(self, item):
        return self.cells.__getitem__(item)


class MapCell:
    """Element of a 'Map'.

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


class Map:
    """Calculates distance and path from state.player to all other cells.

    Map is being constructed once per each turn and then is being used in algorithms
    that require some kind of movement on the board.
    """

    def __init__(self, state: AdvancedState):
        """Constructing a Map from State"""
        self.size_x = state.size_x
        self.size_y = state.size_y
        self.map: list[list[MapCell]] = [[MapCell() for _ in range(state.size_x)] for _ in range(state.size_y)]

        def fill_map(mapper: list[list[MapCell]], cells: list[tuple[int, int]], dist: int):
            # Recursive function for filling map cells step-by-step
            next_cells = []
            for x, y in cells:
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        new_x, new_y = x + dx, y + dy
                        if not isinstance(state[new_y][new_x], (Player, Wall)) and not mapper[new_y][new_x].visited:
                            next_cells.append((new_x, new_y))
                            mapper[new_y][new_x] = MapCell(dist=dist, dx=dx, dy=dy, visited=True)

            if next_cells:
                fill_map(mapper, next_cells, dist + 1)

        # Initializing original cell with dist=0 and starting recursion process
        self.map[state.player.y][state.player.x] = MapCell(dist=0, visited=True)
        fill_map(self.map, [(state.player.x, state.player.y)], 1)

    def show(self) -> str:
        str_size: int = 12
        s = ''
        for y in range(self.size_y):
            for x in range(self.size_x):
                cell = self.map[y][x]
                cell_str = f'{cell.dist} ({cell.dx}, {cell.dy})' if cell.visited else ''
                s += cell_str.ljust(str_size) + ' | '
            s += '\n'
        return s

    def goto(self, x: int, y: int) -> tuple[int, int]:
        """Calculates direction from the original cell to a given cell."""
        cell = self[y][x]
        while self[y][x].dist > 1:
            x -= cell.dx
            y -= cell.dy
            cell = self[y][x]

        return cell.dx, cell.dy

    def __getitem__(self, item):
        return self.map.__getitem__(item)
