import attr
import pygame

from rules import *
from simulation import Simulator


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
    wall_surf: pygame.Surface = attr.ib(default=None, init=False)
    kind_bonus2surf: dict[type, dict[int: pygame.Surface]] = attr.ib(default=None, init=False)

    @cell_size.default
    def _(self):
        return min(
            (self.screen_width - 2 * self.border_x - self.border_between_cells * (self.board.size_x - 1)) // self.board.size_x,
            (self.screen_height - 2 * self.border_y - self.border_between_cells * (self.board.size_y - 1)) // self.board.size_y
        )

    def load_cell_image(self, path):
        img = pygame.image.load(path)
        return pygame.transform.scale(img, (self.cell_size, self.cell_size))

    def __attrs_post_init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))

        self.player_surf = self.load_cell_image(f"images/player.png")
        self.wall_surf = self.load_cell_image(f"images/wall.png")
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


    def start_loop(self):
        running = True
        while running:
            next_step = False
            for event in pygame.event.get():
                match event.type:
                    case pygame.QUIT:
                        running = False
                    case pygame.KEYDOWN:
                        match event.key:
                            case pygame.K_ESCAPE:
                                running = False
                            case pygame.K_RETURN | pygame.K_n:
                                next_step = True

            self.screen.fill("black")

            if next_step and not self.simulator.is_endgame:
                self.simulator.step()

            self.render()
            # Flip the display
            pygame.display.flip()

        pygame.quit()

    def render(self):
        for board_y in range(self.board.size_y):
            for board_x in range(self.board.size_x):
                cell = self.board.get_cell(board_x, board_y)
                x = self.border_x + self.cell_size * board_x + self.border_between_cells * board_x
                y = self.border_y + self.cell_size * board_y + self.border_between_cells * board_y
                if isinstance(cell, Bonus):
                    surf = self.kind_bonus2surf[type(cell)][cell.value]
                elif isinstance(cell, Player):
                    surf = self.player_surf
                elif isinstance(cell, Wall):
                    surf = self.wall_surf
                else:
                    surf = pygame.Surface((self.cell_size, self.cell_size))
                    surf.fill("white")

                self.screen.blit(surf, (x, y))
