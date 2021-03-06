#!/usr/bin/env python
import datetime
import json
import sys
from dataclasses import asdict

from gigamonkeys.montecarlo import Estimate
from gigamonkeys.montecarlo import Named
from gigamonkeys.montecarlo.schedule import Parallel
from gigamonkeys.montecarlo.schedule import Sequence
from gigamonkeys.montecarlo.schedule_dsl import Plus
from gigamonkeys.montecarlo.schedule_dsl import parse


def show_results(r, indent):
    if r.name:
        s = r.summary.own if hasattr(r.summary, "own") else r.summary
        print(f"{' ' * indent * 2}{r.name}: {round(s[0])}-{round(s[1])}")
    if hasattr(r.summary, "children"):
        for c in r.summary.children:
            show_results(c, indent + 1)


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


def json_dump(x):
    json.dump(x, fp=sys.stdout, indent=2, default=default)


class NamedEstimate(Named, Estimate):
    pass


if __name__ == "__main__":

    e = Sequence(
        name="bar",
        children=[
            NamedEstimate(name="sub1", low=5, high=10),
            NamedEstimate(name="sub2", low=5, high=20),
        ],
    )

    # r = e.run(100_000)
    # show_results(r, 0)

    with open("foo.txt") as f:
        ast = parse(f)

    def to_schedule(node, children):
        if not children:
            return NamedEstimate(name=node.name, low=node.low, high=node.high)
        else:
            t = Sequence if isinstance(node, Plus) else Parallel
            return t(name=node.name, children=children)

    s = ast.map(to_schedule)
    s.name = "TOTAL"
    r = s.run(10_000)
    print()
    show_results(r, 0)
    print()
    json_dump(asdict(r))
