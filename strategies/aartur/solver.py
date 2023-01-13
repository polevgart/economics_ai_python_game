from strategy import BaseMove, DirectMove, Shoot
from rules import Wall, ScoreBonus, HealBonus, Player

from .preparation import ExtendedState, ReachabilityGraph


class BaseSolver:
    """BaseSolver is responsible for solving one particular task.

    This task can be, for example, collecting ScoreBonus or shooting at enemies.

    Its main method, 'solve', takes ExtendedState and a precalculated ReachabilityGraph,
    and returns BaseMove (which is the most suitable for this task) and 'confidence' in this move.
    'confidence' is just float, preferably from 0.0 to 1.0, where
    1.0 means max confidence and 0.0 means totally useless move.
    """

    def solve(self, state: ExtendedState, graph: ReachabilityGraph) -> tuple[BaseMove, float]:
        raise NotImplementedError()


class CollectBonusSolver(BaseSolver):
    """Solver for collecting one particular type of Bonus, which is defined in 'bonus_type'.
    """

    bonus_type: type = None

    @staticmethod
    def calculate_confidence(dist: int, player: Player) -> float:
        """Calculating confidence in move based on the distance to the bonus and
        some player state (for example, its health)
        """
        raise NotImplementedError()

    def solve(self, state: ExtendedState, graph: ReachabilityGraph) -> tuple[BaseMove, float]:
        bonuses: list[tuple[int, int]] = []   # list of coordinates of all bonuses on the map
        for y in range(state.size_y):
            for x in range(state.size_x):
                if isinstance(state.get_cell(x=x, y=y), self.bonus_type) and graph.get_cell(x=x, y=y).visited:
                    bonuses.append((x, y))

        if not bonuses:
            return DirectMove(dx=0, dy=0), 0.0

        # choosing the closest bonus as our goal (for now ignoring the bonus value)
        x, y = min(bonuses, key=lambda elem: graph.get_cell(x=elem[0], y=elem[1]).dist)
        dx, dy = graph.get_direction_to(x, y)

        dist = graph.get_cell(x=x, y=y).dist
        confidence = self.calculate_confidence(dist, state.player)

        return DirectMove(dx=dx, dy=dy), confidence


class CollectScoreBonusSolver(CollectBonusSolver):
    """Solver for collecting ScoreBonus."""

    bonus_type: type = ScoreBonus

    @staticmethod
    def calculate_confidence(dist: int, player: Player) -> float:
        return max(0.0, 1.0 - dist * 0.1)


class CollectHealBonusSolver(CollectBonusSolver):
    """Solver for collecting HealBonus."""

    bonus_type: type = HealBonus

    @staticmethod
    def calculate_confidence(dist: int, player: Player) -> float:
        # confidence is greater if we are low on health
        confidence = max(0.0, 1.0 - dist * 0.1)
        confidence *= (1.0 - player.health / player.max_health)
        return confidence


class ShootSolver(BaseSolver):
    """Solver for shooting at enemy.

    It can return either Shoot, shooting at enemy, or DirectMove, moving to enemy if it is out of range.
    Prioritizes more damaged and close enemies (close in meaning of moving to them).
    """

    confidence_moving: float = 0.1  # base confidence if we have to move to the targeted enemy
    confidence_direct_shooting: float = 0.5  # base confidence if we can shoot enemy directly (which is greater)
    # except this base confidence, there is other part which depends on how damaged the enemy is

    def solve(self, state: ExtendedState, graph: ReachabilityGraph) -> tuple[BaseMove, float]:
        # closest positions from which we can shoot at enemy
        closest_shoot_positions: list[tuple[Player, tuple[int, int]]] = []
        for enemy in state.other_players:
            if not enemy.is_alive:
                continue
            shoot_positions: list[tuple[int, int]] = []
            for dx, dy in (-1, 0), (1, 0), (0, -1), (0, 1):
                x = enemy.x + dx
                y = enemy.y + dy

                # finding all possible positions from which we can shoot at enemy
                while not isinstance(state.get_cell(x=x, y=y), (Wall,)):
                    if isinstance(state.get_cell(x=x, y=y), Player) and (x != state.player.x or y != state.player.y):
                        # all *other* players are blocking our shot, so breaking
                        # (we don't count *ourselves* as an obstacle for shooting!)
                        break
                    if graph.get_cell(x=x, y=y).visited:
                        shoot_positions.append((x, y))
                    x += dx
                    y += dy

            if shoot_positions:
                # finding the closest shooting position
                closest_shoot_position = min(shoot_positions,
                                             key=lambda elem: graph.get_cell(x=elem[0], y=elem[1]).dist)
                closest_shoot_positions.append((enemy, closest_shoot_position))

        if not closest_shoot_positions:
            return DirectMove(dx=0, dy=0), 0.0

        # constructing and assessing move for each enemy
        shoot_moves: list[tuple[BaseMove, float]] = []
        for enemy, (x, y) in closest_shoot_positions:
            if graph.get_cell(x=x, y=y).dist > 0:
                # if distance > 0 then we cannot shoot directly, we have to walk
                move = graph.get_direction_to(x, y)
                move = DirectMove(dx=move[0], dy=move[1])
                confidence = self.confidence_moving
            else:
                # we can shoot directly! perfect
                dx = enemy.x - x
                dy = enemy.y - y
                if dx == 0:
                    dy = 1 if dy > 0 else -1
                else:
                    dx = 1 if dx > 0 else -1
                move = Shoot(dx=dx, dy=dy)
                confidence = self.confidence_direct_shooting

            # increasing confidence based on how damaged the enemy is (the max value is 1.0)
            confidence += (1.0 - self.confidence_direct_shooting) * (1.0 - enemy.health / enemy.max_health)
            shoot_moves.append((move, confidence))

        # choosing the best move (and enemy)
        move, confidence = max(shoot_moves, key=lambda elem: elem[1])
        return move, confidence


class HideSolver(BaseSolver):
    """Solver for hiding from enemies. [not implemented!]

    If you are low on health then maybe you should hide and survive?
    """

    def solve(self, state: ExtendedState, graph: ReachabilityGraph) -> tuple[BaseMove, float]:
        return DirectMove(dx=1, dy=1), 0.0


class CenterSolver(BaseSolver):
    """Solver for going to the center of board. [not implemented!]

    If nothing to do then maybe you should go to the center? More opportunities (and more risk of dying!)
    """

    def solve(self, state: ExtendedState, graph: ReachabilityGraph) -> tuple[BaseMove, float]:
        return DirectMove(dx=1, dy=1), 0.0
