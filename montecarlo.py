#!/usr/bin/env python

from math import floor
from random import normalvariate

# From https://en.wikipedia.org/wiki/Normal_distribution#Quantile_function
z_90 = 1.644853626951


class Simulation:

    "Base class for simulations."

    def accumulator(self):
        "Produce an accumulator to hold results of each step."
        pass

    def add(self, accumulator, step):
        "Add the results of a step to our accumulator."
        pass

    def step(self):
        "Produce one step of the simulation."
        pass

    def summarize(self, accumulator):
        "Summarize the accumulated values."
        pass

    def run(self, iters):
        "Simulate by producing and accumulating iters steps."
        acc = self.accumulator()
        for _ in range(iters):
            self.add(acc, self.step())
        return self.summarize(acc)

    def confidence_interval(self, values, p=0.9):
        "Compute a confidence interval from a set of sortable values."
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
        self.values = normal_values(low, high, lowest, highest)

    def accumulator(self):
        return []

    def add(self, accumulator, step):
        accumulator.append(step)

    def step(self):
        return next(self.values)

    def summarize(self, accumulator):
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

    def summarize_own(self, self_acc):
        "Summarize our own accumulated top-level simulated values."
        pass

    #
    # Concrete methods.
    #

    def accumulator(self):
        return Composite([], [c.accumulator() for c in self.children])

    def add(self, accumulator, step):
        accumulator.own.append(step.own)
        child_accs_and_steps = zip(accumulator.children, step.children)
        for child, (a, s) in zip(self.children, child_accs_and_steps):
            child.add(a, s)

    def step(self):
        child_values = [c.step() for c in self.children]
        return Composite(self.combine_child_values(child_values), child_values)

    def summarize(self, accumulator):
        return Composite(
            self.summarize_own(accumulator.own),
            [c.summarize(a) for a, c in zip(accumulator.children, self.children)],
        )


class Composite:

    "Represent anything that has its own value and children values."

    def __init__(self, own, children):
        self.own = own
        self.children = children


#
# Utility functions
#


def normal_values(low, high, lowest=float("-inf"), highest=float("inf")):
    "Generator of random normal values given a 90% confidence interval."

    half_width = (high - low) / 2
    mid = low + half_width

    # 90% of normal values will fall within +/- 1.64 standard
    # deviations of the mean. We want 90% of values to fall between
    # low and high, so we want to back out the desired standard
    # deviation such that 1.64 standard deviations is the distance
    # from mid to high (or to low).
    stddev = half_width / z_90

    while True:
        yield min(max(normalvariate(mid, stddev), lowest), highest)
