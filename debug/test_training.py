"""Quick training test script."""
from neurotraffic.core.simulation import World
from neurotraffic.core.config import Config
from neurotraffic.ai.genetic_trainer import GeneticTrainer
import time

trainer = GeneticTrainer()
world = World()
world.build()
print(f"Traffic lights: {len(world.city_map.get_traffic_lights())}")
dt = 1 / 60

# First test: fixed timer baseline (no brain)
world.reset()
for _ in range(int(Config.TRAINING_SIM_DURATION * 60)):
    world.update(dt)
world.finalize_metrics()
m = world.metrics
print(f"BASELINE (fixed timer): completed={m.cars_completed} wait={m.average_wait_time:.1f} "
      f"travel={m.average_travel_time:.1f} stuck={m.active_cars_at_end} active_wait={m.avg_active_wait:.1f}")

# Now train
for gen in range(10):
    t0 = time.time()
    for i in range(trainer.population_size):
        world.reset()
        brain = trainer.get_brain(i)
        world.set_brain_for_all_lights(brain)
        for _ in range(int(Config.TRAINING_SIM_DURATION * 60)):
            world.update(dt)
        world.finalize_metrics()
        trainer.evaluate(i, world.metrics)
    trainer.evolve()
    elapsed = time.time() - t0
    h = trainer.history[-1]
    print(
        f"Gen {h['generation']}: "
        f"best={h['best_fitness']:.1f} avg={h['average_fitness']:.1f} "
        f"completed={h['best_cars_completed']} "
        f"wait={h['best_avg_wait']:.1f} travel={h['best_avg_travel']:.1f} "
        f"({elapsed:.1f}s)"
    )
print("Done")
