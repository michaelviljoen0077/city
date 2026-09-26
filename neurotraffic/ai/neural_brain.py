"""Simple feedforward neural network implemented with NumPy."""

import copy

import numpy as np
from neurotraffic.ai.brain import Brain
from neurotraffic.core.config import Config


class NeuralBrain(Brain):
    def __init__(self, layer_sizes=None):
        if layer_sizes is None:
            layer_sizes = [
                Config.BRAIN_INPUTS,
                Config.BRAIN_HIDDEN_1,
                Config.BRAIN_HIDDEN_2,
                Config.BRAIN_OUTPUTS,
            ]
        self.layer_sizes = layer_sizes
        self.weights = []
        self.biases = []
        for i in range(len(layer_sizes) - 1):
            w = np.random.randn(layer_sizes[i], layer_sizes[i + 1]) * 0.5
            b = np.zeros(layer_sizes[i + 1])
            self.weights.append(w)
            self.biases.append(b)

    def decide(self, inputs):
        x = np.array(inputs, dtype=np.float64)
        for i, (w, b) in enumerate(zip(self.weights, self.biases)):
            x = x @ w + b
            if i < len(self.weights) - 1:
                x = np.tanh(x)  # hidden activation
        return x.tolist()

    def mutate(self, mutation_rate=None, mutation_strength=None):
        if mutation_rate is None:
            mutation_rate = Config.MUTATION_RATE
        if mutation_strength is None:
            mutation_strength = Config.MUTATION_STRENGTH
        for i in range(len(self.weights)):
            mask = np.random.random(self.weights[i].shape) < mutation_rate
            noise = np.random.randn(*self.weights[i].shape) * mutation_strength
            self.weights[i] += mask * noise

            mask_b = np.random.random(self.biases[i].shape) < mutation_rate
            noise_b = np.random.randn(*self.biases[i].shape) * mutation_strength
            self.biases[i] += mask_b * noise_b

    def copy(self):
        # Shallow-copy keeps the subclass; then give the clone its own arrays
        new = copy.copy(self)
        new.layer_sizes = list(self.layer_sizes)
        new.weights = [w.copy() for w in self.weights]
        new.biases = [b.copy() for b in self.biases]
        return new

    def get_weights(self):
        """Flatten all weights and biases into a single list."""
        flat = []
        for w, b in zip(self.weights, self.biases):
            flat.extend(w.flatten().tolist())
            flat.extend(b.flatten().tolist())
        return flat

    def weight_count(self):
        return sum(w.size + b.size for w, b in zip(self.weights, self.biases))

    def set_weights(self, flat_weights):
        """Restore weights and biases from a flat list."""
        if len(flat_weights) != self.weight_count():
            raise ValueError(
                f"expected {self.weight_count()} weights for layers "
                f"{self.layer_sizes}, got {len(flat_weights)}")
        idx = 0
        for i in range(len(self.weights)):
            w_size = self.weights[i].size
            self.weights[i] = np.array(flat_weights[idx:idx + w_size]).reshape(self.weights[i].shape)
            idx += w_size
            b_size = self.biases[i].size
            self.biases[i] = np.array(flat_weights[idx:idx + b_size])
            idx += b_size
