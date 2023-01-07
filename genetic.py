import attr
import random
from tqdm.auto import tqdm


class Individual:
    def mutate(self) -> "Individual":
        raise NotImplementedError()

    def crossover(self, other: "Individual") -> "Individual":
        raise NotImplementedError()


@attr.s(slots=True, kw_only=True)
class GeneticAlgorithm:
    individual_factory = attr.ib(default=Individual)

    max_generations: int = attr.ib()
    population_size: int = attr.ib()
    num_of_children: int = attr.ib()
    mutate_prob: float = attr.ib()

    crossover_weights: tuple[int] = attr.ib(init=False)
    selection_weights: tuple[int] = attr.ib(init=False)

    @crossover_weights.default
    def _(self):
        return tuple(range(self.population_size, 0, -1))

    @selection_weights.default
    def _(self):
        return tuple(range(self.population_size, 0, -1))

    def gen_start_population(self):
        return [
            self.individual_factory()
            for _ in range(self.population_size)
        ]

    def run(self) -> Individual:
        population = self.gen_start_population()
        ranked_population = self.ranking_phase(population)

        for epoch in tqdm(range(self.max_generations)):
            children = self.crossover_phase(ranked_population)
            survivors = self.selection_phase(ranked_population, count=self.population_size - len(children))
            self.mutation_phase(survivors)
            ranked_population = self.ranking_phase(children + survivors)

        return ranked_population[0]

    def crossover_phase(self, ranked_population: list[Individual]) -> list[Individual]:
        parents = random.choices(
            ranked_population, weights=self.crossover_weights, k=self.num_of_children * 2
        )
        paired_parents = zip(parents[:self.num_of_children], parents[self.num_of_children:])
        return [
            first.crossover(second) for first, second in paired_parents
        ]

    def selection_phase(self, ranked_population, count):
        return random.choices(
            ranked_population, weights=self.selection_weights, k=count
        )

    def mutation_phase(self, survivors: list[Individual]):
        for individual in survivors:
            if random.random() < self.mutate_prob:
                individual.mutate()

    def ranking_phase(self, population: list[Individual]) -> list[Individual]:
        raise NotImplementedError()
