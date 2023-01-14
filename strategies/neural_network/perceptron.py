import attr
import copy
import numpy as np
import numpy.typing as npt
import typing

from genetic import Individual
from rules import *  # noqa
from rules import BaseObject
from strategies.core import BaseMove, BaseStrategy
import util as lib_util


Activation = typing.Callable[[npt.ArrayLike], npt.ArrayLike]


def act_relu(x: npt.ArrayLike) -> npt.ArrayLike:
    x[x < 0] = 0
    return x


def act_sigmoid(x: npt.ArrayLike, eps: float = 1e-9) -> npt.ArrayLike:
    neg_mask = (x < 0)
    z = np.empty_like(x)
    z[neg_mask] = np.exp(x[neg_mask])
    z[~neg_mask] = np.exp(-x[~neg_mask])
    numerator = np.ones_like(x)
    numerator[neg_mask] = z[neg_mask]
    return (numerator / (1 + z)).clip(eps, 1 - eps)


def act_tanh(x: npt.ArrayLike) -> npt.ArrayLike:
    return 2 * act_sigmoid(2 * x) - 1


@attr.s(slots=True, kw_only=True)
class Perceptron:
    input_size: int = attr.ib()
    output_size: int = attr.ib()
    hidden_layer_sizes: tuple[int] = attr.ib(default=(64, 64))
    activation: Activation = attr.ib(default=act_relu)
    weights: list[npt.ArrayLike] = attr.ib()

    @weights.default
    def init_weights(self):
        layer_sizes = self.input_size, *self.hidden_layer_sizes, self.output_size
        return [
            self._xavier_init(shape)
            for shape in zip(layer_sizes, layer_sizes[1:])
        ]

    def _xavier_init(self, shape: tuple[int, int]):
        fan_in, fan_out = shape
        bound = np.sqrt(6 / (fan_in + fan_out))
        return np.random.uniform(-bound, bound, size=shape)

    def forward(self, x: npt.ArrayLike) -> npt.ArrayLike:
        for weight in self.weights:
            x = self.activation(x @ weight)
        return x

    def __call__(self, x):
        return self.forward(x)


@attr.s(slots=True, kw_only=True)
class NeuralStrategy(BaseStrategy, Individual):
    perceptron: Perceptron = attr.ib(factory=lambda: Perceptron(input_size=800, output_size=13))

    def encode_cell(self, cell: BaseObject | None) -> list[float]:
        match cell:  # noqa
            case Wall():
                return [1, 0, 0, 0, 0] + [0, 0, 0]
            case HealBonus():
                return [0, 1, 0, 0, 0] + [cell.value, 0, 0]
            case PoisonBonus():
                return [0, 0, 1, 0, 0] + [cell.value, 0, 0]
            case ScoreBonus():
                return [0, 0, 0, 1, 0] + [cell.value, 0, 0]
            case Player():
                return [0, 0, 0, 0, 1] + [cell.health, cell.score, cell.name == self.player_name]
            case None:
                return [0, 0, 0, 0, 0] + [0, 0, 0]
            case _:
                raise TypeError("Unknown cell type")

    def encode_state(self, state: State) -> npt.ArrayLike:
        embeddings = []
        for row in state.cells:
            for cell in row:
                embeddings.extend(self.encode_cell(cell))
        return np.array(embeddings, dtype=np.float16)

    def decode_move(self, out: npt.ArrayLike) -> BaseMove:
        idx = np.argmax(out)
        return self._possible_moves[idx]

    def get_next_move(self, state: State) -> BaseMove:
        x = self.encode_state(state)
        out = self.perceptron(x)
        move = self.decode_move(out)
        return move

    def mutate(self):
        """Gaussian mutation with standard parameter values mu=0 and sigma=1
        """
        prob = 0.1
        for layer in self.perceptron.weights:
            mask = np.random.random(layer.shape) < prob
            noise = np.random.normal(size=layer.shape, scale=1e-3)
            layer[mask] += noise[mask]

    def crossover(self, other: 'NeuralStrategy') -> 'NeuralStrategy':
        eta = 10
        child = copy.deepcopy(self)
        for i, (layer, other_layer) in enumerate(zip(self.perceptron.weights, other.perceptron.weights)):
            rand = np.random.random(layer.shape)
            beta = np.where(rand < 0.5, 2 * rand, 1. / (2 * (1 - rand)))
            beta **= 1. / (eta + 1)
            if lib_util.roll_dice(0.5):
                layer, other_layer = other_layer, layer
            child.perceptron.weights[i] = ((1 + beta) * layer + (1 - beta) * other_layer) / 2

        return child
