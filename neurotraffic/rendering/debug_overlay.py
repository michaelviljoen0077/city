"""Debug overlay — optional visual information for debugging."""

import pygame
from neurotraffic.core.config import Config


class DebugOverlay:
    def __init__(self, surface):
        self.surface = surface
        self.font = None
        self.enabled = False
        self.heatmap_enabled = False
        self._init_fonts()

    def _init_fonts(self):
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 11)

    def toggle(self):
        self.enabled = not self.enabled

    def toggle_heatmap(self):
        self.heatmap_enabled = not self.heatmap_enabled

    def draw(self, world):
        if self.heatmap_enabled:
            self._draw_heatmap(world)
        if not self.enabled:
            return
        self._draw_node_ids(world)
        self._draw_vehicle_ids(world)
        self._draw_queue_lengths(world)

    def _draw_node_ids(self, world):
        for node in world.city_map.nodes.values():
            text = self.font.render(str(node.id), True, (180, 180, 80))
            self.surface.blit(text, (node.x - 6, node.y - 20))

    def _draw_vehicle_ids(self, world):
        for v in world.vehicles:
            if v.completed:
                continue
            label = f"#{v.id}"
            text = self.font.render(label, True, (180, 220, 255))
            self.surface.blit(text, (int(v.x) + 8, int(v.y) - 10))

    def _draw_queue_lengths(self, world):
        for inter in world.city_map.intersections.values():
            if inter.traffic_light is None:
                continue
            x, y = inter.position
            for i, d in enumerate(["N", "S", "E", "W"]):
                q = inter.get_queue_length(d)
                if q > 0:
                    offsets = {"N": (0, -30), "S": (0, 30), "E": (30, 0), "W": (-30, 0)}
                    ox, oy = offsets[d]
                    text = self.font.render(f"{d}:{q}", True, (255, 150, 150))
                    self.surface.blit(text, (x + ox - 8, y + oy - 6))

    def _draw_heatmap(self, world):
        for inter in world.city_map.intersections.values():
            total_q = sum(inter.get_queue_length(d) for d in ["N", "S", "E", "W"])
            if total_q == 0:
                continue
            intensity = min(total_q / 15.0, 1.0)
            r = int(255 * intensity)
            g = int(60 * (1 - intensity))
            color = (r, g, 0, int(80 + 100 * intensity))

            x, y = inter.position
            size = Config.BLOCK_SIZE // 3
            heat_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
            pygame.draw.circle(heat_surf, color, (size, size), size)
            self.surface.blit(heat_surf, (x - size, y - size))
