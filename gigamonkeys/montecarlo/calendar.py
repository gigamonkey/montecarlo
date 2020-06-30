from dataclasses import dataclass
from dataclasses import field
from datetime import date

import pendulum

from gigamonkeys.montecarlo import CompositeSimulation
from gigamonkeys.montecarlo import Estimate
from gigamonkeys.montecarlo import Named
from gigamonkeys.montecarlo import Simulation


class Calendar:

    "Keep track of weekdays and days off."

    def __init__(self, days_off):
        self.days_off = days_off

    def today(self):
        return pendulum.today().date()

    def n_workdays_after(self, start, days):
        "The end date days workdays after start."
        new_start = start
        days_left = days
        while days_left > 0:
            end = self.n_weekdays_after(new_start, days_left)
            days_left = self.days_off_between(new_start, end)
            new_start = end
        return end

    def n_weekdays_after(self, start, days):
        "The date `days` weekdays after start (non-inclusive)."
        whole_weeks, extra_days = divmod(days, 5)
        into_weekend = start.weekday() + extra_days > 4

        if not into_weekend:
            weekend_days = 0
        elif start.weekday() < 5:
            weekend_days = 2
        else:
            weekend_days = 7 - start.weekday()

        return start.add(weeks=whole_weeks, days=extra_days + weekend_days)

    def days_off_between(self, start, end):
        return sum(start <= d <= end for d in self.days_off)


def estimate(name, low, high):
    return CalendarEstimate(name=name, low=low, high=high)


def sequence(name, children):
    return CalendarSequence(name=name, children=children)


def parallel(name, children):
    return CalendarParallel(name=name, children=children)


class CalendarSummarizer(Simulation):
    def summarize(self, accumulator):
        return {
            key: self.confidence_interval([getattr(a, key) for a in accumulator])
            for key in ("days", "calendar_days", "start", "end")
        }


class CalendarEstimate(Named, CalendarSummarizer, Estimate):
    def make_step(self, start=None, calendar=None, **kwds):
        days = super().make_step(**kwds)
        end = calendar.n_workdays_after(start, days)
        return CalendarStep(days, start, end)


class CalendarComposite(Named, CompositeSimulation, CalendarSummarizer):
    pass


class CalendarSequence(CalendarComposite):

    "Like Sequence except date aware."

    def step_children(self, accumulators, start=None, calendar=None, **kwds):

        next_start = start

        def step(c, a):
            nonlocal next_start
            v = c.step(a, start=next_start, calendar=calendar, **kwds)
            next_start = v.end
            return v

        return [step(c, a) for c, a in zip(self.children, accumulators)]

    def combine_child_values(self, child_values):
        days = sum(c.days for c in child_values)
        start = child_values[0].start
        end = child_values[-1].end
        return CalendarStep(days, start, end)


class CalendarParallel(CalendarComposite):

    "Like Parallel except date aware."

    def combine_child_values(self, child_values):
        days = max(c.days for c in child_values)
        start = child_values[0].start
        end = max(c.end for c in child_values)
        return CalendarStep(days, start, end)


@dataclass
class CalendarStep:

    days: int
    start: date
    end: date
    calendar_days: int = field(init=False)

    def __post_init__(self):
        self.calendar_days = (self.end - self.start).days


if __name__ == "__main__":

    c = Calendar(set())

    start = pendulum.parse("2020-06-29").date()

    starts = "".join(f"{start.add(days=d).format('dddd'):12}" for d in range(7))
    padding = " " * len(f"{9:2d} days after: ")
    print(f"{padding}{starts}")
    for i in range(16):
        ends = "".join(
            f"{c.n_weekdays_after(start.add(days=d), i).format('dddd'):12}"
            for d in range(7)
        )
        print(f"{i:2d} days after: {ends}")
