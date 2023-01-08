import attr
import pygame

from rules import *  # noqa
from rules import BaseObject
from simulation import Simulator


MAX_FPS = 30


@attr.s(slots=True, kw_only=True)
class PygameInterface:
    board: Board = attr.ib()
    simulator: Simulator = attr.ib()
    screen = attr.ib(init=False, default=None)

    screen_width = attr.ib()
    screen_height = attr.ib()

    border_x = attr.ib()
    border_y = attr.ib()
    border_between_cells = attr.ib()

    cell_size = attr.ib(init=False)

    player_surf: pygame.Surface = attr.ib(default=None, init=False)
    dead_surf: pygame.Surface = attr.ib(default=None, init=False)
    empty_surf: pygame.Surface = attr.ib(default=None, init=False)
    wall_surf: pygame.Surface = attr.ib(default=None, init=False)
    kind_bonus2surf: dict[type, dict[int: pygame.Surface]] = attr.ib(default=None, init=False)

    @cell_size.default
    def _(self):
        return min(
            (self.screen_width - 2 * self.border_x - self.border_between_cells * (self.board.size_x - 1)) // self.board.size_x,
            (self.screen_height - 2 * self.border_y - self.border_between_cells * (self.board.size_y - 1)) // self.board.size_y
        )

    def load_cell_image(self, path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (self.cell_size, self.cell_size))

    def __attrs_post_init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.player_surf = self.load_cell_image("images/player.png")
        self.dead_surf = self.load_cell_image("images/dead.png")
        self.empty_surf = self.load_cell_image("images/empty.png")
        self.wall_surf = self.load_cell_image("images/wall.png")
        self.kind_bonus2surf = {
            HealBonus: {
                value: self.load_cell_image(f"images/heal_x{value}.png")
                for value in range(1, 4)
            },
            PoisonBonus: {
                value: self.load_cell_image(f"images/poison_x{value}.png")
                for value in range(1, 4)
            },
            ScoreBonus: {
                value: self.load_cell_image(f"images/exp_x{value}.png")
                for value in range(1, 4)
            },
        }

    def start_loop(self, autorun=True, fps=3):
        clock = pygame.time.Clock()
        running = True
        while running:
            next_step = False
            for event in pygame.event.get():
                match event.type:  # noqa
                    case pygame.QUIT:
                        running = False
                    case pygame.KEYDOWN:
                        match event.key:  # noqa
                            case pygame.K_ESCAPE:
                                running = False
                            case pygame.K_RETURN | pygame.K_n:
                                next_step = True
                                autorun = False
                            case pygame.K_SPACE:
                                autorun = not autorun
                            case pygame.K_a:
                                fps = max(1, fps - 1)
                            case pygame.K_s:
                                fps = min(MAX_FPS, fps + 1)

            if autorun:
                clock.tick(fps)
                next_step = True

            if next_step and not self.simulator.is_endgame:
                self.simulator.step()

            self.render()
            pygame.display.flip()

        pygame.quit()

    def _render_cell(self, cell: BaseObject) -> pygame.Surface:
        surf = self.empty_surf.copy()
        match cell:  # noqa
            case Bonus():
                surf.blit(self.kind_bonus2surf[type(cell)][cell.value], (0, 0))
            case Player():
                if not cell.is_alive:
                    surf.blit(self.dead_surf, (0, 0))
                    return surf

                surf.blit(self.player_surf, (0, 0))

                hp_frac = cell.health / cell.max_health
                hp_color = (
                    int(min(255, 255 * 2 * (1 - hp_frac))),
                    int(min(255, 255 * 2 * hp_frac)),
                    0,
                )
                pygame.draw.rect(
                    surf, hp_color,
                    (5, self.cell_size - 15, int(hp_frac * (self.cell_size - 10)), 10),
                )
                pygame.draw.rect(
                    surf, "black",
                    (5, self.cell_size - 15, self.cell_size - 10, 10),
                    width=1,
                )

            case Wall():
                surf.blit(self.wall_surf, (0, 0))
            case None:
                pass
            case _:
                logger.error("Unknown cell type %s", cell)

        return surf

    def render(self):
        self.screen.fill("black")
        for board_y in range(self.board.size_y):
            for board_x in range(self.board.size_x):
                cell = self.board.get_cell(board_x, board_y)
                surf = self._render_cell(cell)

                x = self.border_x + self.cell_size * board_x + self.border_between_cells * board_x
                y = self.border_y + self.cell_size * board_y + self.border_between_cells * board_y
                self.screen.blit(surf, (x, y))
