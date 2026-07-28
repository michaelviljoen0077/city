"""Save and load trained neural brain models."""

import json
import os
from datetime import datetime

from neurotraffic.ai.neural_brain import NeuralBrain
from neurotraffic.ai.traffic_light_brain import TrafficLightBrain


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
MODELS_DIR = os.path.join(DATA_DIR, "saved_models")


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
        filepath = os.path.join(MODELS_DIR, filename)
        if not os.path.exists(filepath):
            return None
        with open(filepath) as f:
            data = json.load(f)
        brain = TrafficLightBrain()
        saved_sizes = data.get("layer_sizes")
        if saved_sizes and saved_sizes != brain.layer_sizes:
            # Saved with a different architecture than the current config
            brain = NeuralBrain(saved_sizes)
        brain.set_weights(data["weights"])
        return brain

    @staticmethod
    def save_best(brain):
        return ModelStore.save_brain(brain, "best_brain.json")

    @staticmethod
    def load_best():
        return ModelStore.load_brain("best_brain.json")
