"""Save and load trained neural brain models."""

import json
import os
from datetime import datetime

from neurotraffic.ai.neural_brain import NeuralBrain
from neurotraffic.ai.traffic_light_brain import TrafficLightBrain
from neurotraffic.core.config import Config
from neurotraffic.persistence.paths import MODELS_DIR


class ModelStore:
    @staticmethod
    def save_brain(brain, filename=None):
        os.makedirs(MODELS_DIR, exist_ok=True)
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"brain_{timestamp}.json"
        filepath = os.path.join(MODELS_DIR, filename)
        data = {
            "layer_sizes": brain.layer_sizes,
            "weights": brain.get_weights(),
            "saved_at": datetime.now().isoformat(),
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        return filepath

    @staticmethod
    def load_brain(filename="best_brain.json"):
        """Load a saved brain, or return None if the file doesn't exist.

        Raises ValueError if the file is not usable as a traffic light brain.
        """
        filepath = os.path.join(MODELS_DIR, filename)
        if not os.path.exists(filepath):
            return None
        with open(filepath) as f:
            data = json.load(f)
        brain = TrafficLightBrain()
        saved_sizes = data.get("layer_sizes")
        if saved_sizes and saved_sizes != brain.layer_sizes:
            # Saved with a different hidden architecture than the current
            # config; inputs/outputs must still match what lights provide.
            if saved_sizes[0] != Config.BRAIN_INPUTS or saved_sizes[-1] != Config.BRAIN_OUTPUTS:
                raise ValueError(
                    f"{filename} has layers {saved_sizes}; expected "
                    f"{Config.BRAIN_INPUTS} inputs and {Config.BRAIN_OUTPUTS} outputs")
            brain = NeuralBrain(saved_sizes)
        brain.set_weights(data["weights"])
        return brain

    @staticmethod
    def save_best(brain):
        return ModelStore.save_brain(brain, "best_brain.json")

    @staticmethod
    def load_best():
        return ModelStore.load_brain("best_brain.json")
