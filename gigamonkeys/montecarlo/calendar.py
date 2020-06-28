import pendulum


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
