#!/usr/bin/env python

import datetime
import json
import sys
from dataclasses import asdict

import pendulum

from gigamonkeys.montecarlo.calendar import Calendar
from gigamonkeys.montecarlo.schedule import CalendarEstimate, CalendarParallel, CalendarSequence


def default(o):
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()


def json_dump(x):
    json.dump(x, fp=sys.stdout, indent=2, default=default)


if __name__ == "__main__":

    s = CalendarSequence(
        "Test",
        [
            CalendarEstimate("Sub 1", 10, 20),
            CalendarParallel(
                "P1",
                [
                    CalendarEstimate("P-Sub 1", 10, 20),
                    CalendarEstimate("P-Sub 2", 15, 30),
                ],
            ),
        ],
    )

    c = Calendar({pendulum.parse("2020-07-03").date()})
    r = s.run(iters=10_000, start=c.today(), calendar=c)

    json_dump(asdict(r))
