"""Simulation clock with speed control."""

import pygame


class SimClock:
    def __init__(self, fps=60):
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.speed_multiplier = 1.0
        self.paused = False
        self.elapsed = 0.0  # total simulation time

    def tick(self):
        raw_dt = self.clock.tick(self.fps) / 1000.0
        if self.paused:
            return 0.0
        dt = raw_dt * self.speed_multiplier
        self.elapsed += dt
        return dt

    def set_speed(self, multiplier):
        self.speed_multiplier = multiplier

    def toggle_pause(self):
        self.paused = not self.paused

    def reset(self):
        self.elapsed = 0.0
        self.paused = False
