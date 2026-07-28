"""Metrics collection for simulation runs."""


class MetricsCollector:
    def __init__(self):
        self.reset()

    def reset(self):
        self.cars_spawned = 0
        self.cars_completed = 0
        self._travel_times = []
        self._wait_times = []
        self._speed_sum = 0.0
        self._speed_count = 0
        self.light_switch_count = 0
        # End-of-simulation stats (set by World.finalize_metrics)
        self.active_cars_at_end = 0
        self.avg_active_wait = 0.0

    def record_spawn(self):
        self.cars_spawned += 1

    def record_completed(self, vehicle):
        self.cars_completed += 1
        self._travel_times.append(vehicle.travel_time)
        self._wait_times.append(vehicle.wait_time)

    def record_speed_sample(self, speed):
        self._speed_sum += speed
        self._speed_count += 1

    @property
    def active_cars(self):
        return self.cars_spawned - self.cars_completed

    @property
    def average_travel_time(self):
        return sum(self._travel_times) / len(self._travel_times) if self._travel_times else 0.0

    @property
    def average_wait_time(self):
        return sum(self._wait_times) / len(self._wait_times) if self._wait_times else 0.0

    @property
    def total_wait_time(self):
        return sum(self._wait_times)

    @property
    def average_speed(self):
        return self._speed_sum / self._speed_count if self._speed_count > 0 else 0.0

    @property
    def congestion_score(self):
        """Higher means more congestion. Uses active cars' wait time."""
        if self.cars_spawned == 0:
            return 0.0
        active = self.active_cars
        if active == 0:
            return 0.0
        return self.avg_active_wait * active / 100.0

    def update_light_switches(self, traffic_lights):
        self.light_switch_count = sum(tl.switch_count for tl in traffic_lights)

    def snapshot(self):
        """Return dict of current metrics."""
        return {
            "cars_spawned": self.cars_spawned,
            "cars_completed": self.cars_completed,
            "active_cars": self.active_cars,
            "average_travel_time": round(self.average_travel_time, 1),
            "average_wait_time": round(self.average_wait_time, 1),
            "total_wait_time": round(self.total_wait_time, 1),
            "average_speed": round(self.average_speed, 1),
            "congestion_score": round(self.congestion_score, 2),
            "light_switch_count": self.light_switch_count,
        }
