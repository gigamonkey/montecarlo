#!/usr/bin/env python

from dataclasses import asdict

import pendulum

from cal import Calendar
from schedule import CalendarEstimate, CalendarParallel, CalendarSequence
from util import json_dump

s = CalendarSequence(
    "Test",
    [
        CalendarEstimate("Sub 1", 10, 20),
        CalendarParallel(
            "P1",
            [CalendarEstimate("P-Sub 1", 10, 20), CalendarEstimate("P-Sub 2", 15, 30)],
        ),
    ],
)

c = Calendar({pendulum.parse("2020-07-03").date()})
r = s.run(iters=10_000, start=c.today(), calendar=c)


json_dump(asdict(r))
