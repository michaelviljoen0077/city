"""Renderer — draws the road network, cars, and traffic lights."""

import math
import pygame
from neurotraffic.core.config import Config


class Renderer:
    def __init__(self, surface):
        self.surface = surface

    def draw(self, world):
        self.surface.fill(Config.COLOR_BG)
        self._draw_roads(world)
        self._draw_intersections(world)
        self._draw_traffic_lights(world)
        self._draw_vehicles(world)

    def _draw_roads(self, world):
        drawn = set()
        for road in world.city_map.roads:
            key = tuple(sorted([road.start_node.id, road.end_node.id]))
            if key in drawn:
                continue
            drawn.add(key)
            sx, sy = road.start_node.x, road.start_node.y
            ex, ey = road.end_node.x, road.end_node.y
            pygame.draw.line(self.surface, Config.COLOR_ROAD,
                             (sx, sy), (ex, ey), Config.ROAD_WIDTH)
            # Lane divider (dashed)
            self._draw_dashed_line(sx, sy, ex, ey)

    def _draw_dashed_line(self, sx, sy, ex, ey):
        dx = ex - sx
        dy = ey - sy
        length = math.hypot(dx, dy)
        if length == 0:
            return
        nx, ny = dx / length, dy / length
        dash_len = 10
        gap_len = 8
        pos = 0
        while pos < length:
            end_pos = min(pos + dash_len, length)
            x1 = sx + nx * pos
            y1 = sy + ny * pos
            x2 = sx + nx * end_pos
            y2 = sy + ny * end_pos
            pygame.draw.line(self.surface, Config.COLOR_LANE_MARK,
                             (int(x1), int(y1)), (int(x2), int(y2)), 1)
            pos += dash_len + gap_len

    def _draw_intersections(self, world):
        for inter in world.city_map.intersections.values():
            x, y = inter.position
            size = Config.ROAD_WIDTH // 2 + 4
            rect = pygame.Rect(x - size, y - size, size * 2, size * 2)
            pygame.draw.rect(self.surface, Config.COLOR_INTERSECTION, rect)

    def _draw_traffic_lights(self, world):
        for inter in world.city_map.intersections.values():
            tl = inter.traffic_light
            if tl is None:
                continue
            x, y = inter.position
            offset = Config.ROAD_WIDTH // 2 + 6
            r = 5

            # North/South indicators
            ns_color = Config.COLOR_GREEN if tl.is_green_for("N") else Config.COLOR_RED
            pygame.draw.circle(self.surface, ns_color, (x, y - offset), r)
            pygame.draw.circle(self.surface, ns_color, (x, y + offset), r)

            # East/West indicators
            ew_color = Config.COLOR_GREEN if tl.is_green_for("E") else Config.COLOR_RED
            pygame.draw.circle(self.surface, ew_color, (x - offset, y), r)
            pygame.draw.circle(self.surface, ew_color, (x + offset, y), r)

    def _draw_vehicles(self, world):
        for vehicle in world.vehicles:
            if vehicle.completed:
                continue
            x, y = int(vehicle.x), int(vehicle.y)
            # Offset car to right side of road (simulate lane)
            if vehicle.current_road:
                perp = vehicle.current_road.angle + math.pi / 2
                x += int(math.cos(perp) * Config.LANE_WIDTH * 0.35)
                y += int(math.sin(perp) * Config.LANE_WIDTH * 0.35)

            half_l = Config.CAR_LENGTH // 2
            half_w = Config.CAR_WIDTH // 2
            angle = vehicle.angle
            cos_a = math.cos(angle)
            sin_a = math.sin(angle)
            corners = []
            for dx, dy in [(-half_l, -half_w), (half_l, -half_w),
                           (half_l, half_w), (-half_l, half_w)]:
                rx = x + dx * cos_a - dy * sin_a
                ry = y + dx * sin_a + dy * cos_a
                corners.append((rx, ry))

            # Car body
            pygame.draw.polygon(self.surface, Config.COLOR_CAR, corners)

            # Headlight (front)
            front_x = x + half_l * cos_a
            front_y = y + half_l * sin_a
            pygame.draw.circle(self.surface, Config.COLOR_YELLOW,
                               (int(front_x), int(front_y)), 2)
