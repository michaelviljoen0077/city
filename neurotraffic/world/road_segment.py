"""A directed road segment connecting two nodes."""

import math


class RoadSegment:
    def __init__(self, road_id, start_node, end_node, lanes=1, speed_limit=120.0):
        self.id = road_id
        self.start_node = start_node
        self.end_node = end_node
        self.lanes = lanes
        self.speed_limit = speed_limit
        self.vehicles = []
        self.allowed_modes = ["car"]

        dx = end_node.x - start_node.x
        dy = end_node.y - start_node.y
        self.length = math.hypot(dx, dy)
        self.angle = math.atan2(dy, dx)

    @property
    def direction(self):
        """Return cardinal direction: 'N', 'S', 'E', 'W'."""
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        if abs(dx) > abs(dy):
            return "E" if dx > 0 else "W"
        else:
            return "S" if dy > 0 else "N"

    def position_at(self, t):
        """Get (x, y) at fraction t along the road (0=start, 1=end)."""
        x = self.start_node.x + (self.end_node.x - self.start_node.x) * t
        y = self.start_node.y + (self.end_node.y - self.start_node.y) * t
        return (x, y)

    def add_vehicle(self, vehicle):
        self.vehicles.append(vehicle)

    def remove_vehicle(self, vehicle):
        if vehicle in self.vehicles:
            self.vehicles.remove(vehicle)

    def vehicles_sorted(self):
        """Return vehicles sorted by position on road (nearest to end first)."""
        return sorted(self.vehicles, key=lambda v: v.position_on_road, reverse=True)
