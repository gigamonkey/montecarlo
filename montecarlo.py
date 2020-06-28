from dataclasses import dataclass
from math import floor
from random import normalvariate
from typing import List

# From https://en.wikipedia.org/wiki/Normal_distribution#Quantile_function
z_90 = 1.644853626951


class Simulation:

    "Base class for simulations."

    def accumulator(self):
        "Produce an accumulator to hold results of each step."
        pass

    def step(self, accumulator, **kwds):
        "Produce one step of the simulation and add it to the accumulator."
        print("In Simulation step")
        pass

    def summarize(self, accumulator):
        "Summarize the accumulated values."
        pass

    def run(self, iters, **kwds):
        "Simulate by producing and accumulating iters steps."
        acc = self.accumulator()
        print(f"Got acc {acc} from {self}")
        for _ in range(iters):
            self.step(acc, **kwds)
        return self.summarize(acc)

    def confidence_interval(self, values, p=0.9):
        "Compute a confidence interval from a set of sortable values."
        if not values:
            raise Exception("Can't compute CI from empty array")

        ordered = sorted(values)
        size = len(ordered)
        outside = (1 - p) / 2
        return (
            ordered[floor(size * outside)],
            ordered[floor(size * 1 - outside)],
        )


class Estimate(Simulation):

    """
    A direct estimate. Simulated by generating random normal values
    such that 90% of the values will fall within the bounds of the
    estimate.
    """

    def __init__(self, low, high, lowest=float("-inf"), highest=float("inf")):

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

    def accumulator(self):
        return []

    def step(self, accumulator, **kwds):
        print("In Estimate step")
        s = next(self.values)
        accumulator.append(s)
        print(f"In Estimate step returning {s}")
        return s

    def summarize(self, accumulator):
        print("In Estimate summarize")
        return self.confidence_interval(accumulator)


class CompositeSimulation(Simulation):

    """
    A simulation that works by composing simulated children in some
    way.
    """

    def __init__(self, children):
        self.children = children

    #
    # Abstract
    #

    def combine_child_values(self, child_values):
        "Combine a set of simulated values for our children into our simulated value."
        pass

    def summarize_own(self, own):
        "Summarize our own accumulated top-level simulated values."
        pass

    #
    # Concrete methods.
    #

    def accumulator(self):
        return Composite([], [c.accumulator() for c in self.children])

    def step(self, accumulator, **kwds):
        cv = [c.step(a, **kwds) for c, a in zip(self.children, accumulator.children)]
        s = self.combine_child_values(cv)
        accumulator.own.append(s)
        return s

    def summarize(self, accumulator):
        return Composite(
            self.summarize_own(accumulator.own),
            [c.summarize(a) for a, c in zip(accumulator.children, self.children)],
        )


@dataclass
class Composite:
    "Represent anything that has its own value and child values."
    own: object
    children: List[object]


class NamedSimulation(Simulation):
    def __init__(self, name):
        self.name = name

    def summarize(self, accumulator):
        print("In NamedSimulation summarize")
        return NamedSummary(self.name, super().summarize(accumulator))

    def step(self, acc, **kwds):
        print("In NamedSimulation step")
        return super().step(acc, **kwds)


@dataclass
class NamedSummary:
    name: str
    summary: object
