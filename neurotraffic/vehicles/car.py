"""Car — a rule-based vehicle that follows traffic laws."""

from neurotraffic.core.config import Config
from neurotraffic.vehicles.vehicle import Vehicle

STOP_LINE_BUFFER = 2.0  # pixels before intersection to stop at
MIN_GAP = 4.0  # clear space kept behind the car ahead
BRAKE_MARGIN = 6.0  # start braking this early to absorb discrete timesteps


class Car(Vehicle):
    def update(self, world, dt):
        if self.completed or self.route is None:
            return

        self.travel_time += dt
        self._follow_route(world, dt)
        self._update_position_xy()

    def _follow_route(self, world, dt):
        road = self.current_road
        if road is None:
            return

        obstacle_dist = self._nearest_obstacle_distance(world, road)
        self._drive(obstacle_dist, road, dt)

        # Track wait time
        if self.speed < 1.0:
            self.wait_time += dt

        # Move
        self.position_on_road += self.speed * dt

        if self.position_on_road >= road.length:
            # Safety nets: never cross on a hard red, and never cross into
            # a road whose entry is blocked (would land on another car).
            if self._light_state_ahead(world, road) == "red" or self._next_road_entry_blocked():
                self.position_on_road = road.length - STOP_LINE_BUFFER
                self.speed = 0.0
                return
            self.position_on_road = road.length
            self._arrive_at_node(world)

    def _drive(self, obstacle_dist, road, dt):
        """Accelerate when clear; brake when stopping distance demands it."""
        target = min(self.max_speed, road.speed_limit)

        if obstacle_dist is None:
            self.speed = min(self.speed + Config.CAR_ACCELERATION * dt, target)
            return

        if obstacle_dist <= 1.0:
            self.speed = 0.0
            return

        if self._stopping_distance() + BRAKE_MARGIN >= obstacle_dist:
            self.speed = max(0.0, self.speed - Config.CAR_DECELERATION * dt)
        else:
            self.speed = min(self.speed + Config.CAR_ACCELERATION * dt, target)

    def _stopping_distance(self):
        """Distance needed to stop from current speed at max deceleration."""
        return (self.speed ** 2) / (2.0 * Config.CAR_DECELERATION)

    def _nearest_obstacle_distance(self, world, road):
        """Distance to the nearest thing we must stop for, or None if clear."""
        dists = []

        dist_to_line = road.length - STOP_LINE_BUFFER - self.position_on_road
        light = self._light_state_ahead(world, road)
        if light == "red":
            dists.append(dist_to_line)
        elif light == "yellow":
            # Stop only if we can physically stop before the line;
            # otherwise we are committed and clear the intersection.
            if self._stopping_distance() <= dist_to_line:
                dists.append(dist_to_line)

        gap = self._distance_to_car_ahead()
        if gap is not None:
            dists.append(gap - Config.CAR_LENGTH - MIN_GAP)

        merge_gap = self._merge_conflict_distance(road)
        if merge_gap is not None:
            dists.append(merge_gap - Config.CAR_LENGTH - MIN_GAP)

        return min(dists) if dists else None

    def _light_state_ahead(self, world, road):
        """State of the light at the end of this road for our approach:
        'green' (or no light), 'yellow' (clearing after our green), or 'red'."""
        inter = world.city_map.intersections.get(road.end_node.id)
        if inter is None or inter.traffic_light is None:
            return "green"
        return inter.traffic_light.state_for(road.direction)

    def _distance_to_car_ahead(self):
        """Center-to-center distance to the nearest car ahead, looking through
        to the next road on the route so queues that spill back are respected."""
        road = self.current_road
        if road is None:
            return None

        closest = None
        for v in road.vehicles:
            if v is self:
                continue
            if v.position_on_road > self.position_on_road:
                d = v.position_on_road - self.position_on_road
                if closest is None or d < closest:
                    closest = d

        if self.route is not None:
            next_road = self.route.next_road
            if next_road is not None:
                remaining = road.length - self.position_on_road
                for v in next_road.vehicles:
                    d = remaining + v.position_on_road
                    if closest is None or d < closest:
                        closest = d

        return closest

    def _merge_conflict_distance(self, road):
        """Yield to cars on other approaches that will enter our next road
        before us. Returns projected center-to-center distance, or None."""
        if self.route is None or self.route.next_road is None:
            return None
        target = self.route.next_road
        my_remaining = road.length - self.position_on_road

        closest = None
        for other_road in road.end_node.incoming_roads:
            if other_road is road:
                continue
            for v in other_road.vehicles:
                if v.route is None or v.route.next_road is not target:
                    continue
                if v.speed < 5.0:  # parked or held at a red light — not merging
                    continue
                their_remaining = other_road.length - v.position_on_road
                # Only yield to whoever reaches the intersection first
                if their_remaining < my_remaining or (
                        their_remaining == my_remaining and v.id < self.id):
                    d = my_remaining - their_remaining
                    if closest is None or d < closest:
                        closest = d
        return closest

    def _next_road_entry_blocked(self):
        """True if a car sits close enough to the next road's entry that
        crossing the intersection now would put us on top of it."""
        if self.route is None or self.route.next_road is None:
            return False
        for v in self.route.next_road.vehicles:
            if v.position_on_road < Config.CAR_LENGTH + MIN_GAP:
                return True
        return False

    def _arrive_at_node(self, world):
        """Car reached end of current road segment."""
        old_road = self.current_road
        if old_road:
            old_road.remove_vehicle(self)

        self.route.advance()

        if self.route.finished:
            self.completed = True
            self.current_road = None
            return

        self.current_road = self.route.current_road
        self.position_on_road = 0.0
        if self.current_road:
            self.current_road.add_vehicle(self)
