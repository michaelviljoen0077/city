import json

import numpy as np
import pytest

from neurotraffic.ai.genetic_trainer import GeneticTrainer
from neurotraffic.ai.traffic_light_brain import TrafficLightBrain
from neurotraffic.core.config import Config
from neurotraffic.core.simulation import World
from neurotraffic.persistence import model_store
from neurotraffic.persistence.model_store import ModelStore
from neurotraffic.train import run_episode


def test_brain_output_shape():
    out = TrafficLightBrain().decide([0.5] * Config.BRAIN_INPUTS)
    assert len(out) == Config.BRAIN_OUTPUTS


def test_copy_is_independent_and_keeps_type():
    brain = TrafficLightBrain()
    clone = brain.copy()
    assert isinstance(clone, TrafficLightBrain)
    clone.mutate(1.0, 1.0)
    assert not np.allclose(brain.get_weights(), clone.get_weights())


def test_save_load_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(model_store, "MODELS_DIR", str(tmp_path))
    brain = TrafficLightBrain()
    ModelStore.save_brain(brain, "b.json")
    loaded = ModelStore.load_brain("b.json")
    assert np.allclose(loaded.get_weights(), brain.get_weights())
    assert ModelStore.load_brain("missing.json") is None


def test_load_rejects_incompatible_model(tmp_path, monkeypatch):
    monkeypatch.setattr(model_store, "MODELS_DIR", str(tmp_path))
    (tmp_path / "bad.json").write_text(json.dumps({"layer_sizes": [3, 2], "weights": [0.0] * 8}))
    with pytest.raises(ValueError):
        ModelStore.load_brain("bad.json")


def test_shipped_best_brain_loads():
    assert ModelStore.load_best() is not None


def test_one_generation_evolves(monkeypatch):
    monkeypatch.setattr(Config, "POPULATION_SIZE", 4)
    monkeypatch.setattr(Config, "ELITE_COUNT", 2)
    trainer = GeneticTrainer()
    world = World()
    world.build()
    for i in range(trainer.population_size):
        trainer.evaluate(i, run_episode(world, trainer.get_brain(i), duration=5.0))
    trainer.evolve()
    assert trainer.generation == 1
    assert len(trainer.population) == 4
    assert trainer.get_best_brain() is not None
    assert trainer.history[0]["best_fitness"] == trainer.best_fitness
