import datetime as dt
import unittest

from scripts import generate_snake_svg as snake


def level_for_count(count: int) -> str:
    if count >= 8:
        return "FOURTH_QUARTILE"
    if count >= 5:
        return "THIRD_QUARTILE"
    if count >= 3:
        return "SECOND_QUARTILE"
    if count >= 1:
        return "FIRST_QUARTILE"
    return "NONE"


def make_weeks(
    active_cells: set[tuple[int, int]],
    counts: dict[tuple[int, int], int] | None = None,
    width: int = 6,
) -> list[list[snake.ContributionDay]]:
    counts = counts or {}
    start = dt.date(2025, 1, 5)
    weeks: list[list[snake.ContributionDay]] = []
    for week_index in range(width):
        week: list[snake.ContributionDay] = []
        for weekday in range(snake.GRID_ROWS):
            key = (week_index, weekday)
            count = counts.get(key, 2 if key in active_cells else 0)
            week.append(
                snake.ContributionDay(
                    date=start + dt.timedelta(days=week_index * 7 + weekday),
                    count=count,
                    level=level_for_count(count),
                    weekday=weekday,
                )
            )
        weeks.append(week)
    return weeks


class GenerateSnakeSvgTests(unittest.TestCase):
    def test_build_snake_path_covers_grid_and_hides_reset_outside_grid(self) -> None:
        weeks = make_weeks({(0, 1), (2, 4), (4, 2)})
        path = snake.build_snake_path(weeks)
        unique_visible = list(dict.fromkeys((point.column, point.row) for point in path.visible_points))
        expected_cells = len(weeks) * snake.GRID_ROWS

        self.assertEqual(len(unique_visible), expected_cells)
        self.assertEqual(path.hidden_start_index, len(path.visible_points))

        for previous, current in zip(path.visible_points, path.visible_points[1:]):
            if (previous.column, previous.row) == (current.column, current.row):
                continue
            distance = abs(previous.column - current.column) + abs(previous.row - current.row)
            self.assertEqual(distance, 1)

        hidden_points = path.full_points[path.hidden_start_index : -1]
        self.assertTrue(hidden_points)
        self.assertTrue(all(point.row < 0 or point.row >= snake.GRID_ROWS for point in hidden_points))
        self.assertEqual(path.full_points[-1], path.visible_points[0])

    def test_segment_total_grows_one_per_food_until_cap(self) -> None:
        max_extra = snake.MAX_SEGMENTS - snake.BASE_SEGMENTS

        self.assertEqual(snake.segment_total_for_food_count(0), snake.BASE_SEGMENTS)
        self.assertEqual(snake.segment_total_for_food_count(1), snake.BASE_SEGMENTS + 1)
        self.assertEqual(snake.segment_total_for_food_count(5), snake.BASE_SEGMENTS + 5)
        self.assertEqual(snake.segment_total_for_food_count(max_extra + 10), snake.MAX_SEGMENTS)

    def test_render_svg_clears_active_cells_and_drops_arcade_hud(self) -> None:
        weeks = make_weeks(
            {(0, 0), (1, 3), (2, 6), (4, 2)},
            counts={(0, 0): 2, (1, 3): 4, (2, 6): 7, (4, 2): 10},
        )
        svg = snake.render_svg("byteD-x", snake.THEMES["dark"], 123, weeks)
        active_count = sum(1 for day in snake.flatten_days(weeks) if day.count > 0)

        self.assertIn("GitHub contribution snake", svg)
        self.assertIn('class="food-marker snake-animated"', svg)
        self.assertIn('class="contribution-cell active-cell grid-animated"', svg)
        self.assertIn('class="grid-static"', svg)
        self.assertIn('class="snake-static"', svg)
        self.assertIn("@media (prefers-reduced-motion: reduce)", svg)
        self.assertEqual(svg.count('class="food-marker snake-animated"'), active_count)
        self.assertEqual(svg.count('class="contribution-cell active-cell grid-animated"'), active_count)
        self.assertEqual(svg.count('attributeName="fill"'), active_count)
        self.assertEqual(svg.count('attributeName="stroke"'), active_count)
        self.assertNotIn("ARCADE SNAKE", svg)
        self.assertNotIn("SCORE", svg)
        self.assertNotIn("PRESS START", svg)


if __name__ == "__main__":
    unittest.main()
