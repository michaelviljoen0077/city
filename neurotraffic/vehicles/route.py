"""Route: a sequence of road segments a vehicle follows."""


class Route:
    def __init__(self, node_ids, city_map):
        self.node_ids = node_ids
        self.road_segments = []
        for i in range(len(node_ids) - 1):
            road = city_map.get_road(node_ids[i], node_ids[i + 1])
            if road is not None:
                self.road_segments.append(road)
        self.current_index = 0

    @property
    def current_road(self):
        if self.current_index < len(self.road_segments):
            return self.road_segments[self.current_index]
        return None

    @property
    def next_road(self):
        if self.current_index + 1 < len(self.road_segments):
            return self.road_segments[self.current_index + 1]
        return None

    def advance(self):
        self.current_index += 1

    @property
    def finished(self):
        return self.current_index >= len(self.road_segments)

    @property
    def remaining(self):
        return len(self.road_segments) - self.current_index
