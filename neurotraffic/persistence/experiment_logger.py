"""Log experiment results to JSON files."""

import json
import os
from datetime import datetime

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
EXPERIMENTS_DIR = os.path.join(DATA_DIR, "experiments")


class ExperimentLogger:
    def __init__(self):
        os.makedirs(EXPERIMENTS_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.filepath = os.path.join(EXPERIMENTS_DIR, f"experiment_{timestamp}.json")
        self.records = []

    def log_generation(self, generation_data):
        self.records.append(generation_data)

    def save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.records, f, indent=2)
        return self.filepath
