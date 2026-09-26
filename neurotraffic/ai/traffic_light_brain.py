"""TrafficLightBrain — a NeuralBrain configured for traffic light control."""

from neurotraffic.ai.neural_brain import NeuralBrain
from neurotraffic.core.config import Config


class TrafficLightBrain(NeuralBrain):
    """10 inputs -> 16 -> 16 -> 2 outputs."""

    def __init__(self):
        super().__init__([
            Config.BRAIN_INPUTS,
            Config.BRAIN_HIDDEN_1,
            Config.BRAIN_HIDDEN_2,
            Config.BRAIN_OUTPUTS,
        ])
