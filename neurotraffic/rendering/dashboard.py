"""Dashboard — draws simulation metrics on screen."""

import pygame
from neurotraffic.core.config import Config


class Dashboard:
    def __init__(self, surface):
        self.surface = surface
        self.font = None
        self.small_font = None
        self._init_fonts()

    def _init_fonts(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 16)
        self.small_font = pygame.font.SysFont("consolas", 13)

    def draw(self, metrics, clock, lights_mode="Fixed timer", training_info=None):
        panel_w = Config.WINDOW_WIDTH // 4
        panel_x = Config.WINDOW_WIDTH - panel_w
        panel_rect = pygame.Rect(panel_x, 0, panel_w, Config.WINDOW_HEIGHT)
        pygame.draw.rect(self.surface, Config.COLOR_DASHBOARD_BG, panel_rect)
        pygame.draw.line(self.surface, (80, 80, 85),
                         (panel_x, 0), (panel_x, Config.WINDOW_HEIGHT), 2)

        x = panel_x + 12
        y = 12

        y = self._header(x, y, "NEUROTRAFFIC")
        y += 6

        snap = metrics.snapshot()
        y = self._label_value(x, y, "Time", f"{clock.elapsed:.1f}s")
        y = self._label_value(x, y, "Speed", f"{clock.speed_multiplier:.0f}x")
        y = self._label_value(x, y, "Paused", "Yes" if clock.paused else "No")
        y = self._label_value(x, y, "Lights", lights_mode)
        y += 10

        y = self._header(x, y, "TRAFFIC")
        y = self._label_value(x, y, "Spawned", str(snap["cars_spawned"]))
        y = self._label_value(x, y, "Completed", str(snap["cars_completed"]))
        y = self._label_value(x, y, "Active", str(snap["active_cars"]))
        y = self._label_value(x, y, "Avg Travel", f"{snap['average_travel_time']}s")
        y = self._label_value(x, y, "Avg Wait", f"{snap['average_wait_time']}s")
        y = self._label_value(x, y, "Congestion", f"{snap['congestion_score']}")
        y = self._label_value(x, y, "Light Sw.", str(snap["light_switch_count"]))
        y += 10

        if training_info:
            y = self._header(x, y, "TRAINING")
            y = self._label_value(x, y, "Generation", str(training_info.get("generation", "-")))
            y = self._label_value(x, y, "Best Fit.", f"{training_info.get('best_fitness', 0):.1f}")
            y = self._label_value(x, y, "Avg Fit.", f"{training_info.get('avg_fitness', 0):.1f}")
            y = self._label_value(x, y, "Eval", f"{training_info.get('eval_index', 0)}/{training_info.get('pop_size', 0)}")
            sim_t = training_info.get("sim_time", 0)
            sim_d = training_info.get("sim_duration", 1)
            y = self._label_value(x, y, "Sim", f"{sim_t:.0f}/{sim_d:.0f}s")
            y += 10

        y = self._header(x, y, "CONTROLS")
        controls = [
            ("Space", "Pause/Resume"),
            ("R", "Reset"),
            ("T", "Training mode"),
            ("D", "Debug overlay"),
            ("H", "Heatmap"),
            ("1/2/3", "Speed 1x/3x/10x"),
            ("S", "Save brain"),
            ("L", "Load brain"),
            ("F", "Fixed timers"),
            ("N", "Next generation"),
        ]
        for key, desc in controls:
            text = self.small_font.render(f"{key:>6}  {desc}", True, (160, 160, 165))
            self.surface.blit(text, (x, y))
            y += 17

    def _header(self, x, y, text):
        surf = self.font.render(text, True, Config.COLOR_YELLOW)
        self.surface.blit(surf, (x, y))
        return y + 22

    def _label_value(self, x, y, label, value):
        text = self.font.render(f"{label + ':':<14} {value}", True, Config.COLOR_TEXT)
        self.surface.blit(text, (x, y))
        return y + 20
