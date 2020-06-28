from dataclasses import asdict, dataclass, field
from datetime import date

from cal import Calendar
from montecarlo import CompositeSimulation, Estimate, NamedSimulation, Simulation

# Simple estimate: values are just ideal days.

# Calendar estimate: values are ideal days, start and end and thus
# calendar days.

# Deadline estimate: values are calendar estimate plus a status of
# COMPLETE, INCOMPLETE, or NOT_STARTED. (When NOT_STARTED, all the
# other values are None). Probably want to count calendar days for
# COMPLETE and INCOMPLETE runs separately to get the 90% CI on how
# long we spend working on a task when we finish it and the CI on how
# long we waste working on it when we're not going to finish.

# To step a simple estimate we just gather all the simulated ideal
# days and combine.

# To step a calendar estimate we need to do a calendar-aware step of
# all our children (each node is given a start date and a calendar and
# returns {ideal_days, start, end, calendar_days} as the step so the
# parent can use the end date of one child as the start date for the
# next child.

# To step a deadline estimate we need to do a deadline-aware step of
# all our children (each node is given a start date, drop-dead date,
# and a calendar and returns {status, ideal_days, start, end,
# calendar_days} as the step so the parent can use the end date of one
# child as the start date for the next child.


class NamedEstimate(NamedSimulation, Estimate):
    def __init__(self, name, low, high):
        NamedSimulation.__init__(self, name)
        Estimate.__init__(self, low, high)


class CompositeSchedule(NamedSimulation, CompositeSimulation):

    "Schedule whose total time is a function of it's children."

    def __init__(self, name, children):
        NamedSimulation.__init__(self, name)
        CompositeSimulation.__init__(self, children)

    def summarize_own(self, own):
        return self.confidence_interval(own)


class Sequence(CompositeSchedule):

    "Children done in sequence."

    def combine_child_values(self, child_values):
        return sum(child_values)


class Parallel(CompositeSchedule):

    "Children done in parallel and all must complete."

    def combine_child_values(self, child_values):
        return max(child_values)


class OneOf(CompositeSchedule):

    "Children done in parallel but we stop when one completes."

    def combine_child_values(self, child_values):
        return min(child_values)


class CalendarSimulation(Simulation):
    def summarize(self, accumulator):
        return {
            key: self.confidence_interval([getattr(a, key) for a in accumulator])
            for key in ("days", "calendar_days", "start", "end")
        }


class CalendarEstimate(NamedSimulation, CalendarSimulation, Estimate):
    def __init__(self, name, low, high):
        NamedSimulation.__init__(self, name)
        Estimate.__init__(self, low, high)

    def step(self, accumulator, start=None, calendar=None, **kwds):
        days = super().step([], **kwds)
        end = calendar.n_workdays_after(start, days)
        s = CalendarStep(days, start, end)
        accumulator.append(s)
        return s


class CalendarSequence(CompositeSchedule, CalendarSimulation):
    def step(self, accumulator, start=None, calendar=None, **kwds):
        child_values = []
        next_start = start
        for c, a in zip(self.children, accumulator.children):
            v = c.step(a, start=next_start, calendar=calendar, **kwds)
            next_start = v.end
            child_values.append(v)
        s = self.combine_child_values(child_values)
        accumulator.own.append(s)
        return s

    def combine_child_values(self, child_values):
        return CalendarStep(
            sum(c.days for c in child_values),
            child_values[0].start,
            child_values[-1].end,
        )

    def summarize_own(self, own):
        return {
            key: self.confidence_interval([getattr(a, key) for a in own])
            for key in ("days", "calendar_days", "start", "end")
        }


@dataclass
class CalendarStep:

    days: int
    start: date
    end: date
    calendar_days: int = field(init=False)

    def __post_init__(self):
        self.calendar_days = (self.end - self.start).days


if __name__ == "__main__":

    import pendulum

    s = CalendarSequence(
        "Test", [CalendarEstimate("Sub 1", 10, 20), CalendarEstimate("Sub 2", 10, 20)]
    )
    c = Calendar({pendulum.parse("2020-07-03").date()})
    r = s.run(iters=10_000, start=c.today(), calendar=c)

    from util import json_dump

    json_dump(asdict(r))
