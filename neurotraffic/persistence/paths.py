"""Locations of on-disk data (saved models, experiment logs)."""

import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
MODELS_DIR = os.path.join(DATA_DIR, "saved_models")
EXPERIMENTS_DIR = os.path.join(DATA_DIR, "experiments")
