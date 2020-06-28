#!/usr/bin/env python

from montecarlo import *
from schedule import *


if __name__ == "__main__":

    e = Sequence(
        name="bar",
        children=[
            NamedEstimate(name="sub1", low=5, high=10),
            NamedEstimate(name="sub2", low=5, high=20),
        ],
    )
    r = e.run(100_000)
    print(f"{r.name}: {r.summary.own}")
    for c in r.summary.children:
        print(f"  {c.name}: {c.summary}")
