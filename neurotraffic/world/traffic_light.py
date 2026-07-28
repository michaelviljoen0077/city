"""Traffic light controlling vehicle flow through an intersection."""

from neurotraffic.core.config import Config


class TrafficLight:
    PHASES = ["NS_GREEN", "ALL_RED_1", "EW_GREEN", "ALL_RED_2"]
    ALL_RED_DURATION = 1.0  # brief safety pause between phases

    def __init__(self, intersection):
        self.intersection = intersection
        self.phase = "NS_GREEN"
        self.phase_index = 0
        self.time_in_phase = 0.0
        self.min_phase_time = Config.MIN_PHASE_TIME
        self.max_phase_time = Config.MAX_PHASE_TIME
        self.default_phase_time = Config.DEFAULT_PHASE_TIME
        self.brain = None
        self.switch_count = 0

    def update(self, world, dt):
        self.time_in_phase += dt

        if self.brain is not None:
            self._neural_update(world, dt)
        else:
            self._fixed_update(dt)

    def _fixed_update(self, dt):
        """Fixed-timer cycling."""
        duration = self.ALL_RED_DURATION if "ALL_RED" in self.phase else self.default_phase_time
        if self.time_in_phase >= duration:
            self._advance_phase()

    def _neural_update(self, world, dt):
        """Let the brain decide whether to switch."""
        if "ALL_RED" in self.phase:
            if self.time_in_phase >= self.ALL_RED_DURATION:
                self._advance_phase()
            return

        if self.time_in_phase < self.min_phase_time:
            return

        if self.time_in_phase >= self.max_phase_time:
            self._advance_phase()
            return

        inputs = self._gather_inputs()
        output = self.brain.decide(inputs)

        if output[1] > output[0]:
            self._advance_phase()

    def _advance_phase(self):
        self.phase_index = (self.phase_index + 1) % len(self.PHASES)
        self.phase = self.PHASES[self.phase_index]
        self.time_in_phase = 0.0
        if self.phase in ("NS_GREEN", "EW_GREEN"):
            self.switch_count += 1

    def _gather_inputs(self):
        """Collect 10 normalized inputs for the neural brain."""
        inter = self.intersection
        n_q = inter.get_queue_length("N")
        s_q = inter.get_queue_length("S")
        e_q = inter.get_queue_length("E")
        w_q = inter.get_queue_length("W")

        n_w = inter.get_average_wait_time("N")
        s_w = inter.get_average_wait_time("S")
        e_w = inter.get_average_wait_time("E")
        w_w = inter.get_average_wait_time("W")

        phase_val = 0.0 if self.phase == "NS_GREEN" else 1.0
        time_norm = min(self.time_in_phase / self.max_phase_time, 1.0)

        max_q = 10.0
        max_w = 30.0
        return [
            min(n_q / max_q, 1.0),
            min(s_q / max_q, 1.0),
            min(e_q / max_q, 1.0),
            min(w_q / max_q, 1.0),
            min(n_w / max_w, 1.0),
            min(s_w / max_w, 1.0),
            min(e_w / max_w, 1.0),
            min(w_w / max_w, 1.0),
            phase_val,
            time_norm,
        ]

    def is_green_for(self, direction):
        """Check if traffic from the given direction has a green light."""
        if self.phase == "NS_GREEN":
            return direction in ("N", "S")
        elif self.phase == "EW_GREEN":
            return direction in ("E", "W")
        return False
