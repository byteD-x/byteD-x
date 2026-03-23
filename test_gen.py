import datetime as dt
from scripts import generate_snake_svg as snake

def make_weeks():
    start = dt.date(2025, 1, 5)
    weeks = []
    for week_index in range(10):
        week = []
        for weekday in range(snake.GRID_ROWS):
            count = 2 if (week_index + weekday) % 3 == 0 else 0
            week.append(
                snake.ContributionDay(
                    date=start + dt.timedelta(days=week_index * 7 + weekday),
                    count=count,
                    level="SECOND_QUARTILE" if count > 0 else "NONE",
                    weekday=weekday,
                )
            )
        weeks.append(week)
    return weeks

weeks = make_weeks()
svg = snake.render_svg("byteD-x", snake.THEMES["dark"], 123, weeks)
with open("test.svg", "w") as f:
    f.write(svg)
