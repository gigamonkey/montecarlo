# Simple estimate: values are just ideal days.

from gigamonkeys.montecarlo import CompositeSimulation
from gigamonkeys.montecarlo import Named


class Sequence(Named, CompositeSimulation):

    "Children done in sequence."

    def combine_child_values(self, child_values):
        return sum(child_values)


class Parallel(Named, CompositeSimulation):

    "Children done in parallel and all must complete."

    def combine_child_values(self, child_values):
        return max(child_values)


class OneOf(Named, CompositeSimulation):

    "Children done in parallel but we stop when one completes."

    def combine_child_values(self, child_values):
        return min(child_values)
