import attr

from strategy import BaseMove, DirectMove, BaseStrategy
from rules import State

from .preparation import ExtendedState, ReachabilityGraph
from .solver import BaseSolver, CollectHealBonusSolver, CollectScoreBonusSolver, ShootSolver, HideSolver, CenterSolver


@attr.s(slots=True, kw_only=True)
class AArturBaseStrategy(BaseStrategy):
    """My base strategy! Chicken!

    Stores some Solver objects and priority coefficients associated to them.

    Calculating the resulting move is quite simple:
    1. Call all our solvers -> moves and confidences
    2. Multiply our priority to the given confidence
    3. Pick a move with maximum value
    """

    solvers: dict[BaseSolver, float] = attr.ib(factory=dict, init=False)

    def get_next_move(self, state: State) -> BaseMove:
        state = ExtendedState(state, self.player_name)
        graph = ReachabilityGraph(state)

        best_move = DirectMove(dx=0, dy=0)
        best_score = 0.0

        # choosing a move with maximum priority * confidence
        for solver, priority in self.solvers.items():
            move, confidence = solver.solve(state, graph)
            score = priority * confidence
            if score > best_score:
                best_score = score
                best_move = move

        return best_move


@attr.s(slots=True, kw_only=True)
class AArturSmartStrategy(AArturBaseStrategy):
    """This is my strategy that should be imported and used."""

    def __attrs_post_init__(self):
        self.solvers = {
            CollectScoreBonusSolver(): 1.0,
            CollectHealBonusSolver(): 3.0,
            ShootSolver(): 2.0,
            HideSolver(): 0.0,
            CenterSolver(): 0.0,
        }
