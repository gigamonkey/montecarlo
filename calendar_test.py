#!/usr/bin/env python

import datetime
import json
import sys
from dataclasses import asdict

import pendulum

from gigamonkeys.montecarlo.calendar import Calendar
from gigamonkeys.montecarlo.calendar import estimate
from gigamonkeys.montecarlo.calendar import parallel
from gigamonkeys.montecarlo.calendar import sequence


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


def json_dump(x):
    json.dump(x, fp=sys.stdout, indent=2, default=default)


if __name__ == "__main__":

    s = sequence(
        "Test",
        [
            estimate("Sub 1", 10, 20),
            parallel("P1", [estimate("P-Sub 1", 10, 20), estimate("P-Sub 2", 15, 30)]),
        ],
    )

    c = Calendar({pendulum.parse("2020-07-03").date()})
    r = s.run(iters=10_000, start=c.today(), calendar=c)

    json_dump(asdict(r))
