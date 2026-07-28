"""Simulation — manages the world state, car spawning, updates, and metrics."""

import random
from neurotraffic.core.config import Config
from neurotraffic.world.city_map import CityMap
from neurotraffic.vehicles.car import Car
from neurotraffic.vehicles.pathfinder import Pathfinder
from neurotraffic.vehicles.route import Route
from neurotraffic.metrics.metrics_collector import MetricsCollector


class World:
    """Holds all simulation state."""

    def __init__(self):
        self.city_map = CityMap()
        self.vehicles = []
        self.completed_vehicles = []
        self.metrics = MetricsCollector()
        self.pathfinder = Pathfinder()
        self._next_vehicle_id = 0
        self._spawn_timer = 0.0

    def build(self):
        self.city_map.build_grid()

    def reset(self):
        # Remove vehicles from roads
        for road in self.city_map.roads:
            road.vehicles.clear()
        # Reset traffic lights
        for tl in self.city_map.get_traffic_lights():
            tl.phase = "NS_GREEN"
            tl.phase_index = 0
            tl.time_in_phase = 0.0
            tl.switch_count = 0
        self.vehicles.clear()
        self.completed_vehicles.clear()
        self.metrics.reset()
        self._next_vehicle_id = 0
        self._spawn_timer = 0.0

    def update(self, dt):
        self._try_spawn(dt)
        self._update_vehicles(dt)
        self._update_traffic_lights(dt)
        self._collect_completed()
        self._sample_metrics()

    def _try_spawn(self, dt):
        self._spawn_timer += dt
        if self._spawn_timer >= Config.SPAWN_INTERVAL:
            self._spawn_timer -= Config.SPAWN_INTERVAL
            if len(self.vehicles) < Config.MAX_ACTIVE_CARS:
                self._spawn_car()

    def _spawn_car(self):
        edges = self.city_map.edge_nodes
        if len(edges) < 2:
            return
        start_node = random.choice(edges)
        dest_node = random.choice(edges)
        while dest_node.id == start_node.id:
            dest_node = random.choice(edges)

        path = self.pathfinder.find_route(self.city_map, start_node.id, dest_node.id)
        if len(path) < 2:
            return

        # Don't spawn on top of a car still near the road entry
        first_road = self.city_map.get_road(path[0], path[1])
        if first_road is not None:
            for v in first_road.vehicles:
                if v.position_on_road < Config.SPAWN_CLEARANCE:
                    return

        car = Car(self._next_vehicle_id, start_node, dest_node)
        self._next_vehicle_id += 1
        route = Route(path, self.city_map)
        car.set_route(route)
        self.vehicles.append(car)
        self.metrics.record_spawn()

    def _update_vehicles(self, dt):
        for v in self.vehicles:
            v.update(self, dt)

    def _update_traffic_lights(self, dt):
        for tl in self.city_map.get_traffic_lights():
            tl.update(self, dt)

    def _collect_completed(self):
        # self.vehicles holds only active cars; completed ones move out
        still_active = []
        for v in self.vehicles:
            if v.completed:
                self.completed_vehicles.append(v)
                self.metrics.record_completed(v)
            else:
                still_active.append(v)
        self.vehicles = still_active

    def _sample_metrics(self):
        active = self.vehicles
        for v in active:
            self.metrics.record_speed_sample(v.speed)
        if active:
            self.metrics.avg_active_wait = sum(v.wait_time for v in active) / len(active)
        else:
            self.metrics.avg_active_wait = 0.0
        self.metrics.update_light_switches(self.city_map.get_traffic_lights())

    def finalize_metrics(self):
        """Record end-of-simulation stats (call before fitness eval)."""
        self.metrics.active_cars_at_end = len(self.vehicles)

    def set_brain_for_all_lights(self, brain):
        """Set the same brain for every traffic light (shared brain mode)."""
        for tl in self.city_map.get_traffic_lights():
            tl.brain = brain

    def clear_brains(self):
        """Remove neural brains; traffic lights revert to fixed timers."""
        for tl in self.city_map.get_traffic_lights():
            tl.brain = None
