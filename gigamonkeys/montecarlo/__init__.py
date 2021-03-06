from collections import defaultdict
from dataclasses import dataclass
from math import floor
from random import normalvariate
from typing import List

# From https://en.wikipedia.org/wiki/Normal_distribution#Quantile_function
z_90 = 1.644853626951


class Mixin:

    "Because object.__init__ doesn't accept arbitrary keyword args."

    def __init__(self, **kwds):
        pass


class Simulation(Mixin):

    "Base class for simulations."

    def accumulator(self):
        "Produce an accumulator to hold results of each step."
        return []

    def make_step(self, **kwds):
        "Generate one simulated step"
        # Called by the default step method but if step is overridden
        # to directly create the step, this needn't be implemented.

    def step(self, accumulator, **kwds):
        "Produce one step of the simulation and add it to the accumulator."
        s = self.make_step(**kwds)
        accumulator.append(s)
        return s

    def summarize(self, accumulator):
        "Summarize the accumulated values."
        return self.confidence_interval(accumulator)

    def run(self, iters, **kwds):
        "Simulate by producing and accumulating iters steps."
        acc = self.accumulator()
        for _ in range(iters):
            self.step(acc, **kwds)
        return self.summarize(acc)

    def confidence_interval(self, values, p=0.9):
        "Compute a confidence interval from a set of sortable values."
        if not values:
            return None

        ordered = sorted(values)
        size = len(ordered)
        outside = (1 - p) / 2
        return (ordered[floor(size * outside)], ordered[floor(size * 1 - outside)])

    def categorical(self, values):
        "Return proportion of each of the values in a list."
        counts = defaultdict(float)
        total = 0
        for x in values:
            counts[x] += 1
            total += 1
        return {k: v / total for k, v in counts.items()}


class Estimate(Simulation):

    """
    A direct estimate. Simulated by generating random normal values
    such that 90% of the values will fall within the bounds of the
    estimate.
    """

    def __init__(self, low, high, lowest=float("-inf"), highest=float("inf"), **kwds):
        super().__init__(low=low, high=high, lowest=lowest, highest=highest, **kwds)

        # 90% of normal values will fall within +/- ~1.64 standard
        # deviations of the mean. We want 90% of values to fall
        # between low and high, so we want to back out the desired
        # standard deviation such that 1.64 standard deviations is the
        # distance from mid to high (or to low).

        half_width = (high - low) / 2
        mid = low + half_width
        stddev = half_width / z_90

        def value():
            return min(max(normalvariate(mid, stddev), lowest), highest)

        self.values = iter(value, None)

    def make_step(self, **kwds):
        return next(self.values)


class CompositeSimulation(Simulation):

    "Simulate the composition of child simulations in some way."

    def __init__(self, children, **kwds):
        super().__init__(children=children, **kwds)
        self.children = children

    def combine_child_values(self, child_values):
        "Combine children's step values into our step value."

    def step_children(self, accumulators, **kwds):
        "Step our children and return the result."
        return [c.step(a, **kwds) for c, a in zip(self.children, accumulators)]

    def accumulator(self):
        return Composite([], [c.accumulator() for c in self.children])

    def step(self, accumulator, **kwds):
        child_values = self.step_children(accumulator.children, **kwds)
        s = self.combine_child_values(child_values)
        accumulator.own.append(s)
        return s

    def summarize(self, accumulator):
        return Composite(
            super().summarize(accumulator.own),
            [c.summarize(a) for c, a in zip(self.children, accumulator.children)],
        )


class Named(Mixin):
    def __init__(self, name, **kwds):
        super().__init__(name=name, **kwds)
        self.name = name

    # FIXME: not clear this actually ever gets invoked.
    def summarize(self, accumulator):
        return NamedSummary(self.name, super().summarize(accumulator))


@dataclass
class Composite:
    "Represent anything that has its own value and child values."
    own: object
    children: List[object]


@dataclass
class NamedSummary:
    name: str
    summary: object
