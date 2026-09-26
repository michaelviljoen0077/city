"""Intersection connecting multiple roads, optionally with a traffic light."""


class Intersection:
    def __init__(self, node):
        self.node = node
        self.id = node.id
        self.position = node.position
        self.incoming_roads = []
        self.outgoing_roads = []
        self.traffic_light = None

    def get_incoming_by_direction(self, direction):
        """Get incoming road from given direction (N/S/E/W)."""
        for road in self.incoming_roads:
            if road.direction == direction:
                return road
        return None

    def _waiting_vehicles(self, direction):
        """Slow vehicles in the last 30% of the incoming road from this direction."""
        road = self.get_incoming_by_direction(direction)
        if road is None or road.length <= 0:
            return []
        return [v for v in road.vehicles
                if v.position_on_road / road.length > 0.7 and v.speed < 5]

    def get_queue_length(self, direction):
        """Count vehicles queued at the intersection from this direction."""
        return len(self._waiting_vehicles(direction))

    def get_average_wait_time(self, direction):
        """Average wait time of vehicles queued from this direction."""
        waiting = self._waiting_vehicles(direction)
        if not waiting:
            return 0.0
        return sum(v.wait_time for v in waiting) / len(waiting)
