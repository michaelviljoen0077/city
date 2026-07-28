"""Genetic algorithm trainer for traffic light brains."""

import random
from neurotraffic.core.config import Config
from neurotraffic.ai.traffic_light_brain import TrafficLightBrain
from neurotraffic.ai.fitness import calculate_fitness


class GeneticTrainer:
    def __init__(self):
        self.population_size = Config.POPULATION_SIZE
        self.elite_count = Config.ELITE_COUNT
        self.mutation_rate = Config.MUTATION_RATE
        self.mutation_strength = Config.MUTATION_STRENGTH
        self.generation = 0
        self.population = [TrafficLightBrain() for _ in range(self.population_size)]
        self.fitness_scores = []
        self.best_brain = None
        self.best_fitness = float("-inf")
        self.history = []  # list of dicts per generation

    def get_brain(self, index):
        """Get brain at index for a simulation run."""
        return self.population[index]

    def evaluate(self, index, metrics):
        """Record fitness for brain at index.

        Snapshot the metrics: the live collector is reset before the next run.
        """
        fitness = calculate_fitness(metrics)
        self.fitness_scores.append((index, fitness, metrics.snapshot()))
        return fitness

    def reset_evaluations(self):
        """Discard partial evaluation results (e.g. when training restarts)."""
        self.fitness_scores = []

    def evolve(self):
        """Create next generation from evaluated fitness scores."""
        self.fitness_scores.sort(key=lambda x: x[1], reverse=True)

        best_idx, best_fit, best_metrics = self.fitness_scores[0]
        if best_fit > self.best_fitness:
            self.best_fitness = best_fit
            self.best_brain = self.population[best_idx].copy()

        avg_fit = sum(f for _, f, _ in self.fitness_scores) / len(self.fitness_scores)

        self.history.append({
            "generation": self.generation,
            "best_fitness": best_fit,
            "average_fitness": avg_fit,
            "best_cars_completed": best_metrics["cars_completed"],
            "best_avg_wait": best_metrics["average_wait_time"],
            "best_avg_travel": best_metrics["average_travel_time"],
        })

        # Select elites
        elites = []
        for i in range(min(self.elite_count, len(self.fitness_scores))):
            idx = self.fitness_scores[i][0]
            elites.append(self.population[idx].copy())

        # Build next generation
        new_pop = list(elites)
        while len(new_pop) < self.population_size:
            parent = random.choice(elites)
            child = parent.copy()
            child.mutate(self.mutation_rate, self.mutation_strength)
            new_pop.append(child)

        self.population = new_pop
        self.fitness_scores = []
        self.generation += 1

    def get_best_brain(self):
        return self.best_brain
