from dataclasses import dataclass
from datetime import date
from typing import Optional

from gigamonkeys.montecarlo import CompositeSimulation
from gigamonkeys.montecarlo import Named
from gigamonkeys.montecarlo import NamedSummary
from gigamonkeys.montecarlo import Simulation
from gigamonkeys.montecarlo.calendar import CalendarEstimate


def estimate(name, low, high):
    return DeadlineEstimate(name=name, low=low, high=high)


def sequence(name, children):
    return DeadlineSequence(name=name, children=children)


def parallel(name, children):
    return DeadlineParallel(name=name, children=children)


class DeadlineSummarizer(Simulation):
    def summarize(self, accumulator):
        def noNone(xs):
            return [x for x in xs if x is not None]

        summary = {
            key: self.confidence_interval(
                noNone((getattr(a, key) for a in accumulator))
            )
            for key in ("days", "calendar_days", "start", "end")
        }
        summary.update(self.categorical(a.disposition for a in accumulator))
        return NamedSummary(self.name, summary)

    def not_started(self, end):
        """
        Result for when due date is already past. The end is the date we
        would have started this task if the due date hadn't been past.
        """
        return DeadlineStep("NOT_STARTED", 0, None, end)

    def incomplete(self, days, start, end):
        "Ran out of time. The end is when we stopped."
        return DeadlineStep("INCOMPLETE", days, start, end)

    def complete(self, days, start, end):
        "Finished before the due date."
        return DeadlineStep("COMPLETE", days, start, end)


@dataclass
class DeadlineStep:

    disposition: str
    days: int
    start: Optional[date]
    end: date

    def __post_init__(self):
        if self.start:
            self.calendar_days = (self.end - self.start).days
        else:
            self.calendar_days = None


class DeadlineEstimate(DeadlineSummarizer, CalendarEstimate):

    "An estimated value which observes a due date."

    def make_step(self, start=None, due_date=None, calendar=None, **kwds):
        if start >= due_date:
            return self.not_started(start)
        else:
            c = super().make_step(
                start=start, due_date=due_date, calendar=calendar, **kwds
            )
            if c.end > due_date:
                return self.incomplete(c.days, start, due_date)
            else:
                return self.complete(c.days, c.start, c.end)


class DeadlineComposite(Named, CompositeSimulation, DeadlineSummarizer):
    pass


class DeadlineSequence(DeadlineComposite):

    "Like CalendarSequence but also deadline aware."

    def step_children(
        self, accumulators, start=None, due_date=None, calendar=None, **kwds
    ):
        next_start = start

        def step(c, a):
            nonlocal next_start
            v = c.step(
                a, start=next_start, due_date=due_date, calendar=calendar, **kwds
            )
            # once we get a child that doesn't finish we will run
            # through the rest of the children with a start date
            # guaranteed to generate a not_started result.
            next_start = v.end if v.disposition == "COMPLETE" else due_date
            return v

        return [step(c, a) for c, a in zip(self.children, accumulators)]

    def combine_child_values(self, child_values):
        if child_values[0].disposition == "NOT_STARTED":
            return self.not_started(child_values[0].end)
        else:
            days = sum(c.days for c in child_values)
            start = child_values[0].start
            if all(c.disposition == "COMPLETE" for c in child_values):
                return self.complete(days, start, child_values[-1].end)
            else:
                incomplete = next(
                    (c for c in child_values if c.disposition != "COMPLETE"), None
                )
                return self.incomplete(days, start, incomplete.end)


class DeadlineParallel(DeadlineComposite):

    "Like CalendarParallel but also deadline aware."

    def step_children(
        self, accumulators, start=None, due_date=None, calendar=None, **kwds
    ):

        # Step the children once with our due date to see what happens
        # but don't really accumulate the results. FIXME: should
        # eventually make accumulator a class so we can have a null
        # object version.
        fake_acc = [c.accumulator() for c in self.children]
        first_pass = super().step_children(
            fake_acc, start=start, due_date=due_date, calendar=calendar, **kwds
        )

        incomplete = next((c for c in first_pass if c.disposition != "COMPLETE"), None)
        real_due_date = incomplete.end if incomplete else due_date
        return super().step_children(
            accumulators, start=start, due_date=real_due_date, calendar=calendar, **kwds
        )

    def combine_child_values(self, child_values):
        if all(c.disposition == "NOT_STARTED" for c in child_values):
            return self.not_started(child_values[0].end)
        else:
            days = max(c.days for c in child_values)
            start = child_values[0].start
            end = max(c.end for c in child_values)
            if all(c.disposition == "COMPLETE" for c in child_values):
                return self.complete(days, start, end)
            else:
                return self.incomplete(days, start, end)

        days = max(c.days for c in child_values)
        start = child_values[0].start
        end = max(c.end for c in child_values)
        return DeadlineStep(days, start, end)
