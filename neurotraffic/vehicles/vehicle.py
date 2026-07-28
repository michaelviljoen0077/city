"""Base vehicle class."""

from neurotraffic.core.config import Config


class Vehicle:
    def __init__(self, vehicle_id, start_node, destination_node):
        self.id = vehicle_id
        self.start_node = start_node
        self.destination_node = destination_node
        self.route = None
        self.current_road = None
        self.position_on_road = 0.0
        self.speed = 0.0
        self.max_speed = Config.CAR_MAX_SPEED
        self.wait_time = 0.0
        self.travel_time = 0.0
        self.completed = False
        self.x = 0.0
        self.y = 0.0
        self.angle = 0.0

    def set_route(self, route):
        self.route = route
        if route.current_road is not None:
            self.current_road = route.current_road
            self.current_road.add_vehicle(self)
            self.position_on_road = 0.0
            self.x = self.current_road.start_node.x
            self.y = self.current_road.start_node.y
            self.angle = self.current_road.angle

    def update(self, world, dt):
        raise NotImplementedError

    def _update_position_xy(self):
        """Sync x, y from position on current road."""
        if self.current_road is not None and self.current_road.length > 0:
            t = self.position_on_road / self.current_road.length
            t = max(0.0, min(1.0, t))
            self.x, self.y = self.current_road.position_at(t)
            self.angle = self.current_road.angle
