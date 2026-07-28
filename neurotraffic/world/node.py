"""A node in the road network graph (intersection or endpoint)."""


class Node:
    def __init__(self, node_id, x, y, is_edge=False):
        self.id = node_id
        self.x = x
        self.y = y
        self.position = (x, y)
        self.is_edge = is_edge  # edge nodes are entry/exit points
        self.incoming_roads = []
        self.outgoing_roads = []
