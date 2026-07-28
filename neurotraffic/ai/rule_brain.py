"""Rule-based traffic light brain (fixed timer baseline)."""

from neurotraffic.ai.brain import Brain


class RuleBrain(Brain):
    """Always returns 'keep current phase'. The fixed timer in TrafficLight handles switching."""

    def decide(self, inputs):
        return [1.0, 0.0]  # keep current phase
