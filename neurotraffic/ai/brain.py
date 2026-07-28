"""Abstract brain interface for all AI controllers."""

import copy


class Brain:
    def decide(self, inputs):
        raise NotImplementedError

    def mutate(self, mutation_rate, mutation_strength):
        pass

    def copy(self):
        return copy.deepcopy(self)

    def get_weights(self):
        return []

    def set_weights(self, weights):
        pass
