"""Graph-based pathfinder using Dijkstra's algorithm."""

import heapq


class Pathfinder:
    def find_route(self, city_map, start_node_id, dest_node_id):
        """Find shortest route as a list of node IDs from start to destination.

        Returns list of node IDs (including start and dest), or empty list if no path.
        """
        if start_node_id == dest_node_id:
            return [start_node_id]

        # Dijkstra
        dist = {start_node_id: 0.0}
        prev = {}
        visited = set()
        heap = [(0.0, start_node_id)]

        while heap:
            d, nid = heapq.heappop(heap)
            if nid in visited:
                continue
            visited.add(nid)

            if nid == dest_node_id:
                break

            node = city_map.nodes[nid]
            for road in node.outgoing_roads:
                neighbor_id = road.end_node.id
                if neighbor_id in visited:
                    continue
                new_dist = d + road.length
                if new_dist < dist.get(neighbor_id, float("inf")):
                    dist[neighbor_id] = new_dist
                    prev[neighbor_id] = nid
                    heapq.heappush(heap, (new_dist, neighbor_id))

        # Reconstruct path
        if dest_node_id not in prev:
            return []

        path = []
        current = dest_node_id
        while current is not None:
            path.append(current)
            current = prev.get(current)
        path.reverse()
        return path
