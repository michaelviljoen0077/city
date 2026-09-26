"""Traffic light controlling vehicle flow through an intersection."""

from neurotraffic.core.config import Config


class TrafficLight:
    PHASES = ["NS_GREEN", "ALL_RED_1", "EW_GREEN", "ALL_RED_2"]
    ALL_RED_DURATION = 1.0  # brief safety pause between phases
    # Which approaches were green in the phase before each all-red clearance.
    # Those approaches see "yellow" during the clearance; everyone else stays red.
    _CLEARING = {"ALL_RED_1": ("N", "S"), "ALL_RED_2": ("E", "W")}

    def __init__(self, intersection):
        self.intersection = intersection
        self.min_phase_time = Config.MIN_PHASE_TIME
        self.max_phase_time = Config.MAX_PHASE_TIME
        self.default_phase_time = Config.DEFAULT_PHASE_TIME
        self.brain = None
        self.reset()

    def reset(self):
        """Return to the initial phase and clear counters (brain is kept)."""
        self.phase_index = 0
        self.phase = self.PHASES[0]
        self.time_in_phase = 0.0
        self.switch_count = 0

    def update(self, world, dt):
        self.time_in_phase += dt

        if self.brain is not None:
            self._neural_update(world, dt)
        else:
            self._fixed_update(dt)

    @property
    def is_all_red(self):
        return self.phase in self._CLEARING

    def _fixed_update(self, dt):
        """Fixed-timer cycling."""
        duration = self.ALL_RED_DURATION if self.is_all_red else self.default_phase_time
        if self.time_in_phase >= duration:
            self._advance_phase()

    def _neural_update(self, world, dt):
        """Let the brain decide whether to switch."""
        if self.is_all_red:
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
        if not self.is_all_red:
            self.switch_count += 1

    def _gather_inputs(self):
        """Collect 10 normalized inputs for the neural brain."""
        inter = self.intersection
        directions = ("N", "S", "E", "W")
        max_q = 10.0
        max_w = 30.0

        queues = [min(inter.get_queue_length(d) / max_q, 1.0) for d in directions]
        waits = [min(inter.get_average_wait_time(d) / max_w, 1.0) for d in directions]
        phase_val = 0.0 if self.phase == "NS_GREEN" else 1.0
        time_norm = min(self.time_in_phase / self.max_phase_time, 1.0)
        return queues + waits + [phase_val, time_norm]

    def is_green_for(self, direction):
        """Check if traffic from the given direction has a green light."""
        return self.state_for(direction) == "green"

    def state_for(self, direction):
        """Signal shown to traffic approaching from `direction`:
        'green', 'yellow' (clearing after its green), or 'red'."""
        if self.phase == "NS_GREEN":
            return "green" if direction in ("N", "S") else "red"
        if self.phase == "EW_GREEN":
            return "green" if direction in ("E", "W") else "red"
        return "yellow" if direction in self._CLEARING[self.phase] else "red"
