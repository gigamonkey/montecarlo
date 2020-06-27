#!/usr/bin/env python

from montecarlo import Estimate, CompositeSimulation


class Sequence(CompositeSimulation):
    def combine_child_values(self, child_values):
        return sum(child_values)

    def summarize_own(self, own):
        return self.confidence_interval(own)


if __name__ == "__main__":

    s = Sequence(
        [
            Estimate(5, 10, 0),
            Estimate(5, 10, 0),
            Estimate(5, 10, 0),
            Estimate(5, 10, 0),
        ]
    )

    r = s.run(100_000)

    print(r.own)

    for c in r.children:
        print(f"  {c}")
