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


from gigamonkeys.montecarlo import NamedComposite


class Sequence(NamedComposite):

    "Children done in sequence."

    def combine_child_values(self, child_values):
        return sum(child_values)


class Parallel(NamedComposite):

    "Children done in parallel and all must complete."

    def combine_child_values(self, child_values):
        return max(child_values)


class OneOf(NamedComposite):

    "Children done in parallel but we stop when one completes."

    def combine_child_values(self, child_values):
        return min(child_values)
