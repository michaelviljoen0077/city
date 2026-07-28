"""Builds the road network graph: nodes, road segments, intersections, traffic lights."""

from neurotraffic.core.config import Config
from neurotraffic.world.node import Node
from neurotraffic.world.road_segment import RoadSegment
from neurotraffic.world.intersection import Intersection
from neurotraffic.world.traffic_light import TrafficLight


class CityMap:
    def __init__(self):
        self.nodes = {}
        self.roads = []
        self.intersections = {}
        self.edge_nodes = []
        self._next_road_id = 0

    def build_grid(self, cols=None, rows=None):
        cols = cols or Config.GRID_COLS
        rows = rows or Config.GRID_ROWS
        block = Config.BLOCK_SIZE

        # Offset so grid is centered
        offset_x = (Config.WINDOW_WIDTH - Config.WINDOW_WIDTH // 4 - (cols - 1) * block) // 2
        offset_y = (Config.WINDOW_HEIGHT - (rows - 1) * block) // 2

        # Create nodes
        for r in range(rows):
            for c in range(cols):
                node_id = r * cols + c
                x = offset_x + c * block
                y = offset_y + r * block
                is_edge = r == 0 or r == rows - 1 or c == 0 or c == cols - 1
                node = Node(node_id, x, y, is_edge=is_edge)
                self.nodes[node_id] = node
                if is_edge:
                    self.edge_nodes.append(node)

        # Create bidirectional roads (two directed segments per connection)
        for r in range(rows):
            for c in range(cols):
                nid = r * cols + c
                # Horizontal: connect to right neighbor
                if c < cols - 1:
                    right_id = r * cols + (c + 1)
                    self._add_road_pair(nid, right_id)
                # Vertical: connect to bottom neighbor
                if r < rows - 1:
                    below_id = (r + 1) * cols + c
                    self._add_road_pair(nid, below_id)

        # Create intersections for all non-edge (interior) nodes, and edge nodes that
        # connect to more than one road also get intersections but no traffic lights.
        for node in self.nodes.values():
            if len(node.incoming_roads) >= 2:
                inter = Intersection(node)
                inter.incoming_roads = list(node.incoming_roads)
                inter.outgoing_roads = list(node.outgoing_roads)
                self.intersections[node.id] = inter

                # Traffic lights on all 3+ way intersections (excludes corners)
                if len(node.incoming_roads) >= 3:
                    tl = TrafficLight(inter)
                    inter.traffic_light = tl

    def _add_road_pair(self, id_a, id_b):
        na = self.nodes[id_a]
        nb = self.nodes[id_b]
        # Forward
        r1 = RoadSegment(self._next_road_id, na, nb)
        self._next_road_id += 1
        self.roads.append(r1)
        na.outgoing_roads.append(r1)
        nb.incoming_roads.append(r1)
        # Backward
        r2 = RoadSegment(self._next_road_id, nb, na)
        self._next_road_id += 1
        self.roads.append(r2)
        nb.outgoing_roads.append(r2)
        na.incoming_roads.append(r2)

    def get_road(self, from_node_id, to_node_id):
        """Find the directed road segment from one node to another."""
        from_node = self.nodes[from_node_id]
        for road in from_node.outgoing_roads:
            if road.end_node.id == to_node_id:
                return road
        return None

    def get_traffic_lights(self):
        """Return all traffic lights."""
        return [inter.traffic_light for inter in self.intersections.values()
                if inter.traffic_light is not None]
