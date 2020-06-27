from montecarlo import Estimate, CompositeSimulation, NamedSimulation


class NamedEstimate(NamedSimulation, Estimate):

    def __init__(self, **kwds):
        super().__init__(**kwds)


class CompositeSchedule(NamedSimulation, CompositeSimulation):

    "Schedule whose total time is a function of it's children."

    def __init__(self, **kwds):
        super().__init__(**kwds)

    def summarize_own(self, own):
        return self.confidence_interval(own)


class Sequence(CompositeSchedule):

    "Children done in sequence."

    def combine_child_values(self, child_values):
        return sum(child_values)


class Parallel(CompositeSchedule):

    "Children done in parallel and all must complete."

    def combine_child_values(self, child_values):
        return max(child_values)


class OneOf(CompositeSchedule):

    "Children done in parallel but we stop when one completes."

    def combine_child_values(self, child_values):
        return min(child_values)
