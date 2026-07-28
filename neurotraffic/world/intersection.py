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

    def get_outgoing_by_direction(self, direction):
        """Get outgoing road toward given direction."""
        for road in self.outgoing_roads:
            if road.direction == direction:
                return road
        return None

    def get_queue_length(self, direction):
        """Count vehicles waiting near the end of the incoming road from this direction."""
        road = self.get_incoming_by_direction(direction)
        if road is None:
            return 0
        count = 0
        for v in road.vehicles:
            fraction = v.position_on_road / road.length if road.length > 0 else 0
            if fraction > 0.7 and v.speed < 5:
                count += 1
        return count

    def get_average_wait_time(self, direction):
        """Average wait time of vehicles near end of incoming road from this direction."""
        road = self.get_incoming_by_direction(direction)
        if road is None:
            return 0.0
        waiting = [v for v in road.vehicles
                    if (v.position_on_road / road.length if road.length > 0 else 0) > 0.7
                    and v.speed < 5]
        if not waiting:
            return 0.0
        return sum(v.wait_time for v in waiting) / len(waiting)
