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
    def test_active_targets_only_include_positive_cells(self) -> None:
        active_cells = {(0, 1), (2, 4), (4, 2)}
        weeks = make_weeks(active_cells, width=5)
        path = snake.build_snake_path(weeks)

        self.assertEqual(
            [(point.column, point.row) for point in path.active_targets],
            [(0, 1), (2, 4), (4, 2)],
        )
        self.assertTrue(all(key in active_cells for key in path.target_progresses))
        self.assertNotIn((1, 1), path.target_progresses)

    def test_diagonal_neighbors_are_clustered_together(self) -> None:
        weeks = make_weeks({(0, 0), (1, 1), (4, 4)}, width=5)
        clusters = snake.build_active_clusters(weeks)

        self.assertEqual(len(clusters), 2)
        self.assertEqual(len(clusters[0].cells), 2)
        self.assertEqual({(point.column, point.row) for point in clusters[0].cells}, {(0, 0), (1, 1)})

    def test_cluster_plan_prefers_local_serpentine_candidate(self) -> None:
        weeks = make_weeks({(0, 0), (0, 1), (1, 1)}, width=3)
        clusters = snake.build_active_clusters(weeks)
        active_coords = set(snake.active_points_from_weeks(weeks))
        plan = snake.build_cluster_plan(clusters[0], active_coords, len(weeks))

        self.assertEqual(
            [(point.column, point.row) for point in plan.active_targets],
            [(0, 0), (0, 1), (1, 1)],
        )
        self.assertLessEqual(plan.metrics.blank_steps, 1)
        self.assertLessEqual(plan.score, (0, 2, 1, 4))

    def test_long_sparse_jump_uses_hidden_bridge_and_caps_visible_blank_run(self) -> None:
        weeks = make_weeks({(0, 2), (5, 2)}, width=6)
        path = snake.build_snake_path(weeks)

        self.assertTrue(path.hidden_segments)
        self.assertLessEqual(path.max_visible_blank_run, snake.MAX_VISIBLE_BLANK_RUN)
        self.assertTrue(all(0.0 <= start < end <= 1.0 for start, end in path.hidden_segments))

    def test_render_svg_uses_motion_path_and_continuous_body(self) -> None:
        weeks = make_weeks({(0, 0), (1, 3), (2, 6), (4, 2)}, width=5)
        svg = snake.render_svg("byteD-x", snake.THEMES["dark"], 123, weeks)

        self.assertIn("<animateMotion", svg)
        self.assertNotIn('calcMode="discrete"', svg)
        self.assertIn('id="dark-snake-body-clip"', svg)
        self.assertIn('clip-path="url(#dark-snake-body-clip)"', svg)
        self.assertIn('class="snake-body-window snake-animated"', svg)
        self.assertNotIn('type="translate"', svg)
        self.assertIn('class="snake-head snake-animated"', svg)

    def test_food_clear_and_growth_share_target_progresses(self) -> None:
        active_cells = {(0, 0), (1, 3), (2, 6), (4, 2)}
        weeks = make_weeks(
            active_cells,
            counts={(0, 0): 2, (1, 3): 4, (2, 6): 7, (4, 2): 10},
            width=5,
        )
        path = snake.build_snake_path(weeks)
        svg = snake.render_svg("byteD-x", snake.THEMES["dark"], 123, weeks)
        timeline_progresses = {progress for progress, _ in path.body_length_timeline}

        self.assertEqual(set(path.target_progresses), active_cells)
        for key in active_cells:
            self.assertIn(path.target_progresses[key], timeline_progresses)
            self.assertIn(f"{path.target_progresses[key]:.5f}", svg)

        self.assertEqual(svg.count('class="food-marker snake-animated"'), len(active_cells))
        self.assertEqual(svg.count('class="contribution-cell active-cell grid-animated"'), len(active_cells))
        self.assertEqual(svg.count('attributeName="fill"'), len(active_cells))
        self.assertEqual(svg.count('attributeName="stroke"'), len(active_cells))

    def test_reduced_motion_structure_is_preserved(self) -> None:
        weeks = make_weeks({(0, 1), (2, 4)}, width=4)
        svg = snake.render_svg("byteD-x", snake.THEMES["light"], 42, weeks)

        self.assertIn("@media (prefers-reduced-motion: reduce)", svg)
        self.assertIn('class="grid-static"', svg)
        self.assertIn('class="snake-static"', svg)

    def test_zero_active_grid_omits_snake_animation(self) -> None:
        weeks = make_weeks(set(), width=4)
        path = snake.build_snake_path(weeks)
        svg = snake.render_svg("byteD-x", snake.THEMES["light"], 0, weeks)

        self.assertEqual(path.active_targets, ())
        self.assertEqual(path.hidden_segments, ())
        self.assertNotIn("<animateMotion", svg)
        self.assertNotIn('class="food-marker snake-animated"', svg)
        self.assertNotIn('class="snake-body-window snake-animated"', svg)


if __name__ == "__main__":
    unittest.main()
