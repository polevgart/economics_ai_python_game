import attr

from strategy import BaseMove, BaseStrategy
from rules import State

from .preparation import AdvancedState, Map
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
        moves: list[tuple[BaseMove, float]] = []  # if only the DirectMove and Shoot were hashable...
        state = AdvancedState(state, self.player_name)
        mapper = Map(state)

        for solver, priority in self.solvers.items():
            move, confidence = solver.solve(state, mapper)
            moves.append((move, priority * confidence))

        # choosing a move with maximum priority * confidence
        result_move, power = max(moves, key=lambda elem: elem[1])

        return result_move


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
