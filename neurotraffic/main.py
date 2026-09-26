"""NeuroTraffic — main entry point."""

import sys
import pygame

from neurotraffic.core.config import Config
from neurotraffic.core.clock import SimClock
from neurotraffic.core.simulation import World
from neurotraffic.rendering.renderer import Renderer
from neurotraffic.rendering.dashboard import Dashboard
from neurotraffic.rendering.debug_overlay import DebugOverlay
from neurotraffic.ai.genetic_trainer import GeneticTrainer
from neurotraffic.persistence.model_store import ModelStore
from neurotraffic.persistence.experiment_logger import ExperimentLogger


class App:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT))
        pygame.display.set_caption(Config.TITLE)

        self.clock = SimClock(Config.FPS)
        self.world = World()
        self.world.build()

        self.renderer = Renderer(self.screen)
        self.dashboard = Dashboard(self.screen)
        self.debug_overlay = DebugOverlay(self.screen)

        self.trainer = GeneticTrainer()
        self.logger = ExperimentLogger()

        self.training_mode = False
        self._training_eval_index = 0
        self._training_sim_time = 0.0
        self._sim_accumulator = 0.0

        self.running = True

    def run(self):
        while self.running:
            dt = self.clock.tick()
            self._handle_input()

            if dt > 0:
                if self.training_mode:
                    self._training_step()
                else:
                    self._free_run_step(dt)

            self.renderer.draw(self.world)
            self.debug_overlay.draw(self.world)
            self.dashboard.draw(
                self.world.metrics,
                self.clock,
                lights_mode=self._lights_mode(),
                training_info=self._get_training_info() if self.training_mode else None,
            )
            pygame.display.flip()

        pygame.quit()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event.key)

    def _handle_key(self, key):
        if key == pygame.K_ESCAPE:
            self.running = False
        elif key == pygame.K_SPACE:
            self.clock.toggle_pause()
        elif key == pygame.K_r:
            self._reset()
        elif key == pygame.K_t:
            self._toggle_training()
        elif key == pygame.K_d:
            self.debug_overlay.toggle()
        elif key == pygame.K_h:
            self.debug_overlay.toggle_heatmap()
        elif key == pygame.K_1:
            self.clock.set_speed(1.0)
        elif key == pygame.K_2:
            self.clock.set_speed(3.0)
        elif key == pygame.K_3:
            self.clock.set_speed(10.0)
        elif key == pygame.K_s:
            self._save_brain()
        elif key == pygame.K_l:
            self._load_brain()
        elif key == pygame.K_f:
            self._use_fixed_timers()
        elif key == pygame.K_n:
            if self.training_mode:
                self._force_next_generation()

    def _reset(self):
        if self.training_mode:
            # Restart the current evaluation from scratch
            self._start_training_eval(self._training_eval_index)
        else:
            # Keep whatever controls the lights (fixed timer or loaded brain)
            self._reset_world()

    def _reset_world(self):
        self.world.reset()
        self.clock.reset()
        self._sim_accumulator = 0.0

    def _toggle_training(self):
        self.training_mode = not self.training_mode
        if self.training_mode:
            self.trainer.reset_evaluations()
            self._start_training_eval(0)
        else:
            self.world.clear_brains()
            self._reset_world()

    def _start_training_eval(self, index):
        """Start evaluating brain at index in the population."""
        self._training_eval_index = index
        self._reset_world()
        brain = self.trainer.get_brain(index)
        self.world.set_brain_for_all_lights(brain)
        self._training_sim_time = 0.0

    def _free_run_step(self, dt):
        # Advance in fixed steps so higher speeds don't make cars jump
        # through each other; leftover time carries to the next frame.
        self._sim_accumulator += dt
        while self._sim_accumulator >= Config.SIM_TIMESTEP:
            self.world.update(Config.SIM_TIMESTEP)
            self._sim_accumulator -= Config.SIM_TIMESTEP

    def _training_step(self):
        # Run many sim ticks per rendered frame for fast training
        for _ in range(Config.TRAINING_STEPS_PER_FRAME):
            self.world.update(Config.SIM_TIMESTEP)
            self._training_sim_time += Config.SIM_TIMESTEP

            if self._training_sim_time >= Config.TRAINING_SIM_DURATION:
                self.world.finalize_metrics()
                self.trainer.evaluate(self._training_eval_index, self.world.metrics)

                next_index = self._training_eval_index + 1
                if next_index < self.trainer.population_size:
                    self._start_training_eval(next_index)
                else:
                    self._finish_generation()
                return

    def _finish_generation(self):
        """All brains evaluated — evolve."""
        self.trainer.evolve()

        if self.trainer.history:
            self.logger.log_generation(self.trainer.history[-1])
            self.logger.save()

        # Start next generation
        self._start_training_eval(0)

    def _force_next_generation(self):
        """Skip remaining evals and evolve with what we have."""
        if self.trainer.fitness_scores:
            self._finish_generation()

    def _save_brain(self):
        brain = self.trainer.get_best_brain()
        if brain:
            path = ModelStore.save_best(brain)
            print(f"Brain saved to {path}")
        else:
            print("No best brain to save yet.")

    def _load_brain(self):
        if self.training_mode:
            print("Leave training mode (T) before loading a brain.")
            return
        try:
            brain = ModelStore.load_best()
        except ValueError as e:
            print(f"Could not load brain: {e}")
            return
        if brain:
            self.world.set_brain_for_all_lights(brain)
            self._reset_world()
            print("Brain loaded.")
        else:
            print("No saved brain found.")

    def _use_fixed_timers(self):
        if self.training_mode:
            return
        self.world.clear_brains()
        self._reset_world()

    def _lights_mode(self):
        lights = self.world.city_map.get_traffic_lights()
        return "Neural" if lights and lights[0].brain is not None else "Fixed timer"

    def _get_training_info(self):
        return {
            "generation": self.trainer.generation,
            "best_fitness": self.trainer.best_fitness if self.trainer.best_fitness > float("-inf") else 0,
            "avg_fitness": (self.trainer.history[-1]["average_fitness"]
                           if self.trainer.history else 0),
            "eval_index": self._training_eval_index + 1,
            "pop_size": self.trainer.population_size,
            "sim_time": self._training_sim_time,
            "sim_duration": Config.TRAINING_SIM_DURATION,
        }


def main():
    app = App()
    app.run()


if __name__ == "__main__":
    main()
