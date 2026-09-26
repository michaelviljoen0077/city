"""Headless training — evolve traffic light brains without opening a window.

Usage:
    python -m neurotraffic.train --generations 10 --save
"""

import argparse
import random
import time

import numpy as np

from neurotraffic.core.config import Config
from neurotraffic.core.simulation import World
from neurotraffic.ai.fitness import calculate_fitness
from neurotraffic.ai.genetic_trainer import GeneticTrainer
from neurotraffic.persistence.model_store import ModelStore
from neurotraffic.persistence.experiment_logger import ExperimentLogger


def run_episode(world, brain, duration=None):
    """Run one simulation from scratch with `brain` on every light
    (None = fixed timers) and return its metrics."""
    duration = Config.TRAINING_SIM_DURATION if duration is None else duration
    world.reset()
    if brain is None:
        world.clear_brains()
    else:
        world.set_brain_for_all_lights(brain)
    for _ in range(int(round(duration / Config.SIM_TIMESTEP))):
        world.update(Config.SIM_TIMESTEP)
    world.finalize_metrics()
    return world.metrics


def _describe(m):
    return (f"completed={m.cars_completed} wait={m.average_wait_time:.1f}s "
            f"travel={m.average_travel_time:.1f}s stuck={m.active_cars_at_end}")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--generations", type=int, default=10)
    parser.add_argument("--duration", type=float, default=Config.TRAINING_SIM_DURATION,
                        help="simulated seconds per evaluation")
    parser.add_argument("--seed", type=int, default=None, help="random seed for reproducible runs")
    parser.add_argument("--save", action="store_true",
                        help="save the best brain as best_brain.json when done")
    args = parser.parse_args(argv)

    if args.seed is not None:
        random.seed(args.seed)
        np.random.seed(args.seed)

    world = World()
    world.build()
    trainer = GeneticTrainer()
    logger = ExperimentLogger()
    print(f"Traffic lights: {len(world.city_map.get_traffic_lights())}")

    baseline = run_episode(world, None, args.duration)
    print(f"Baseline (fixed timer): fitness={calculate_fitness(baseline):.1f} {_describe(baseline)}")

    for _ in range(args.generations):
        t0 = time.time()
        for i in range(trainer.population_size):
            metrics = run_episode(world, trainer.get_brain(i), args.duration)
            trainer.evaluate(i, metrics)
        trainer.evolve()
        h = trainer.history[-1]
        logger.log_generation(h)
        print(f"Gen {h['generation']}: best={h['best_fitness']:.1f} avg={h['average_fitness']:.1f} "
              f"completed={h['best_cars_completed']} wait={h['best_avg_wait']:.1f}s "
              f"travel={h['best_avg_travel']:.1f}s ({time.time() - t0:.1f}s)")

    if trainer.history:
        print(f"Experiment log: {logger.save()}")
    if args.save and trainer.get_best_brain() is not None:
        print(f"Best brain saved to {ModelStore.save_best(trainer.get_best_brain())}")


if __name__ == "__main__":
    main()
