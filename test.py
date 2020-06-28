#!/usr/bin/env python


from montecarlo import *
from schedule import *
from schedule_dsl import *


def show_results(r, indent):
    if r.name:
        if hasattr(r.summary, "own"):
            print(f"{' ' * indent * 2}{r.name}: {r.summary.own}")
        else:
            print(f"{' ' * indent * 2}{r.name}: {r.summary}")
    if hasattr(r.summary, "children"):
        for c in r.summary.children:
            show_results(c, indent + 1)


if __name__ == "__main__":

    e = Sequence(
        name="bar",
        children=[
            NamedEstimate(name="sub1", low=5, high=10),
            NamedEstimate(name="sub2", low=5, high=20),
        ],
    )

    r = e.run(100_000)

    show_results(r, 0)

    with open("foo.txt") as f:
        ast = parse(f)

    def to_schedule(node, children):
        if not children:
            return NamedEstimate(node.name, node.low, node.high)
        else:
            t = Sequence if isinstance(node, Plus) else Parallel
            return t(node.name, children)

    s = ast.map(to_schedule)
    s.name = "Roadmap"
    r = s.run(10_000)
    print()
    show_results(r, 0)
