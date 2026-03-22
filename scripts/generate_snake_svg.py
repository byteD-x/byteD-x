#!/usr/bin/env python3
"""Generate a classic GitHub contribution snake SVG.

Inputs:
- `--github-user`: GitHub login to query.
- `--theme`: `light` or `dark`.
- `--output`: target SVG path.

Output:
- Writes a self-contained animated SVG file.

Failure:
- Exits non-zero when the GitHub token is missing, the GraphQL request fails,
  or the SVG cannot be written.
"""

from __future__ import annotations

import argparse
import calendar
import datetime as dt
import html
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
CARD_WIDTH = 1026
CARD_HEIGHT = 294
CARD_RADIUS = 18
GRID_LEFT = 38.0
GRID_TOP = 112.0
GRID_STEP = 18.0
CELL_SIZE = 14.0
GRID_ROWS = 7
GRID_HEIGHT = 122.0
GRID_CLIP_INSET = 1.0
LOOP_DURATION = 16.0
FOOD_HOLD_STEPS = 4
SEGMENT_STEP_GAP = 1
FOOD_FADE = 0.012
CLEAR_FADE = 0.016
REENTRY_FADE = 0.018
BASE_SEGMENTS = 5
MAX_SEGMENTS = 24
BODY_BLOCK_SIZE = 16.8
BODY_BLOCK_RADIUS = 4.0
HEAD_LENGTH = 18.0
HEAD_HEIGHT = 15.6
HEAD_BRIDGE_WIDTH = 7.2
HEAD_BRIDGE_HEIGHT = 13.8
HEAD_BRIDGE_OVERLAP = 4.4
FOOD_MARKER_SIZE = 4.2
SNAKE_SHADOW_STDDEV = 0.7

GRAPHQL_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            contributionCount
            contributionLevel
            date
            weekday
          }
        }
      }
    }
  }
}
"""


@dataclass(frozen=True)
class Theme:
    name: str
    card_bg: str
    card_border: str
    panel_bg: str
    panel_border: str
    title: str
    subtitle: str
    meta: str
    empty_fill: str
    empty_stroke: str
    level_1: str
    level_2: str
    level_3: str
    level_4: str
    snake_fill: str
    snake_fill_alt: str
    snake_stroke: str
    head_fill: str
    head_fill_alt: str
    head_stroke: str
    eye: str
    food_fill: str
    food_stroke: str
    shadow_color: str


THEMES = {
    "light": Theme(
        name="light",
        card_bg="#FFFFFF",
        card_border="#D0D7DE",
        panel_bg="#F6F8FA",
        panel_border="#D0D7DE",
        title="#24292F",
        subtitle="#57606A",
        meta="#6E7781",
        empty_fill="#EBEDF0",
        empty_stroke="#D8DEE4",
        level_1="#9BE9A8",
        level_2="#40C463",
        level_3="#30A14E",
        level_4="#216E39",
        snake_fill="#2DA44E",
        snake_fill_alt="#3FB950",
        snake_stroke="#1A7F37",
        head_fill="#26A641",
        head_fill_alt="#3FB950",
        head_stroke="#1A7F37",
        eye="#F6F8FA",
        food_fill="#F78166",
        food_stroke="#CF222E",
        shadow_color="#2DA44E",
    ),
    "dark": Theme(
        name="dark",
        card_bg="#0D1117",
        card_border="#30363D",
        panel_bg="#0D1117",
        panel_border="#30363D",
        title="#C9D1D9",
        subtitle="#8B949E",
        meta="#7D8590",
        empty_fill="#161B22",
        empty_stroke="#21262D",
        level_1="#0E4429",
        level_2="#006D32",
        level_3="#26A641",
        level_4="#39D353",
        snake_fill="#2EA043",
        snake_fill_alt="#3FB950",
        snake_stroke="#238636",
        head_fill="#2EA043",
        head_fill_alt="#56D364",
        head_stroke="#238636",
        eye="#F0F6FC",
        food_fill="#FF7B72",
        food_stroke="#F85149",
        shadow_color="#238636",
    ),
}


@dataclass(frozen=True)
class ContributionDay:
    date: dt.date
    count: int
    level: str
    weekday: int


@dataclass(frozen=True)
class GridPoint:
    column: int
    row: int
    x: float
    y: float


@dataclass(frozen=True)
class SnakePath:
    visible_points: tuple[GridPoint, ...]
    full_points: tuple[GridPoint, ...]
    first_visible_indexes: dict[tuple[int, int], int]
    active_visit_indexes: tuple[int, ...]
    heading_angles: tuple[float, ...]
    hidden_start_index: int


def require_token() -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Missing GITHUB_TOKEN or GH_TOKEN for GitHub GraphQL access.")
    return token


def iso_datetime(value: dt.date, end_of_day: bool = False) -> str:
    suffix = "23:59:59Z" if end_of_day else "00:00:00Z"
    return f"{value.isoformat()}T{suffix}"


def fetch_contributions(user: str, token: str) -> tuple[int, list[list[ContributionDay]]]:
    """Fetch the past year of contribution calendar data for a user."""
    end_date = dt.date.today()
    start_date = end_date - dt.timedelta(days=365)
    payload = json.dumps(
        {
            "query": GRAPHQL_QUERY,
            "variables": {
                "login": user,
                "from": iso_datetime(start_date),
                "to": iso_datetime(end_date, end_of_day=True),
            },
        }
    ).encode("utf-8")

    request = Request(
        GRAPHQL_ENDPOINT,
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "byteD-x-snake-generator",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            data = json.load(response)
    except HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"GitHub GraphQL request failed: HTTP {exc.code}: {message}") from exc
    except URLError as exc:
        raise SystemExit(f"GitHub GraphQL request failed: {exc.reason}") from exc

    if data.get("errors"):
        messages = "; ".join(item.get("message", "Unknown GraphQL error") for item in data["errors"])
        raise SystemExit(f"GitHub GraphQL returned errors: {messages}")

    calendar_data = (
        data.get("data", {})
        .get("user", {})
        .get("contributionsCollection", {})
        .get("contributionCalendar")
    )
    if not calendar_data:
        raise SystemExit(f"No contribution calendar returned for user '{user}'.")

    weeks: list[list[ContributionDay]] = []
    for week in calendar_data["weeks"]:
        days = [
            ContributionDay(
                date=dt.date.fromisoformat(day["date"]),
                count=int(day["contributionCount"]),
                level=day["contributionLevel"],
                weekday=int(day["weekday"]),
            )
            for day in week["contributionDays"]
        ]
        weeks.append(days)

    return int(calendar_data["totalContributions"]), weeks


def make_grid_point(column: int, row: int) -> GridPoint:
    return GridPoint(
        column=column,
        row=row,
        x=GRID_LEFT + column * GRID_STEP + CELL_SIZE / 2.0,
        y=GRID_TOP + row * GRID_STEP + CELL_SIZE / 2.0,
    )


def grid_key(point: GridPoint) -> tuple[int, int]:
    return point.column, point.row


def progress_at(index: int, total_points: int) -> float:
    if total_points <= 1:
        return 0.0
    return index / float(total_points - 1)


def flatten_days(weeks: Sequence[Sequence[ContributionDay]]) -> list[ContributionDay]:
    return [day for week in weeks for day in week]


def build_month_labels(weeks: Sequence[Sequence[ContributionDay]]) -> list[tuple[int, str]]:
    labels: list[tuple[int, str]] = []
    seen: set[tuple[int, int]] = set()
    for week_index, week in enumerate(weeks):
        marker = next((day for day in week if day.date.day == 1), None)
        if marker is None:
            marker = next((day for day in week if day.date.day <= 7), None)
        if marker is None:
            continue
        key = (marker.date.year, marker.date.month)
        if key in seen:
            continue
        seen.add(key)
        labels.append((week_index, calendar.month_abbr[marker.date.month]))
    return labels


def color_for_day(theme: Theme, day: ContributionDay) -> str:
    if day.level == "FOURTH_QUARTILE":
        return theme.level_4
    if day.level == "THIRD_QUARTILE":
        return theme.level_3
    if day.level == "SECOND_QUARTILE":
        return theme.level_2
    if day.level == "FIRST_QUARTILE":
        return theme.level_1
    return theme.empty_fill


def walk_axis(start: int, end: int) -> Iterable[int]:
    if start == end:
        return []
    step = 1 if end > start else -1
    return range(start + step, end + step, step)


def build_visible_route(weeks: Sequence[Sequence[ContributionDay]]) -> list[GridPoint]:
    route: list[GridPoint] = []
    for column, _week in enumerate(weeks):
        rows = range(GRID_ROWS) if column % 2 == 0 else range(GRID_ROWS - 1, -1, -1)
        for row in rows:
            route.append(make_grid_point(column, row))
    return route


def choose_hidden_row(start: GridPoint, end: GridPoint) -> int:
    top_cost = start.row + end.row
    bottom_cost = (GRID_ROWS - 1 - start.row) + (GRID_ROWS - 1 - end.row)
    return -1 if top_cost <= bottom_cost else GRID_ROWS


def build_hidden_loop(start: GridPoint, end: GridPoint) -> list[GridPoint]:
    hidden_row = choose_hidden_row(start, end)
    return [
        make_grid_point(start.column, hidden_row),
        make_grid_point(end.column, hidden_row),
        end,
    ]


def build_heading_angles(points: Sequence[GridPoint]) -> tuple[float, ...]:
    if not points:
        return ()

    angles: list[float] = []
    for index, point in enumerate(points):
        next_point: GridPoint | None = None
        for future in points[index + 1 :]:
            if future.x != point.x or future.y != point.y:
                next_point = future
                break
        if next_point is None:
            for previous in reversed(points[:index]):
                if previous.x != point.x or previous.y != point.y:
                    next_point = point
                    point = previous
                    break

        if next_point is None:
            angles.append(0.0)
            continue

        dx = next_point.column - point.column
        dy = next_point.row - point.row
        if dx > 0:
            angles.append(0.0)
        elif dx < 0:
            angles.append(180.0)
        elif dy > 0:
            angles.append(90.0)
        else:
            angles.append(-90.0)
    return tuple(angles)


def build_snake_path(weeks: Sequence[Sequence[ContributionDay]]) -> SnakePath:
    route = build_visible_route(weeks)
    if not route:
        return SnakePath((), (), {}, (), (), 0)

    active_coords = {
        (column, day.weekday)
        for column, week in enumerate(weeks)
        for day in week
        if day.count > 0
    }

    visible_points: list[GridPoint] = []
    first_visible_indexes: dict[tuple[int, int], int] = {}
    active_visit_indexes: list[int] = []

    for point in route:
        visible_points.append(point)
        key = grid_key(point)
        if key not in first_visible_indexes:
            first_visible_indexes[key] = len(visible_points) - 1
            if key in active_coords:
                active_visit_indexes.append(first_visible_indexes[key])
        if key in active_coords:
            for _ in range(FOOD_HOLD_STEPS):
                visible_points.append(point)

    hidden_start_index = len(visible_points)
    hidden_points = build_hidden_loop(route[-1], route[0])
    full_points = visible_points + hidden_points

    return SnakePath(
        visible_points=tuple(visible_points),
        full_points=tuple(full_points),
        first_visible_indexes=first_visible_indexes,
        active_visit_indexes=tuple(active_visit_indexes),
        heading_angles=build_heading_angles(full_points),
        hidden_start_index=hidden_start_index,
    )


def segment_total_for_food_count(food_count: int) -> int:
    return min(MAX_SEGMENTS, BASE_SEGMENTS + max(food_count, 0))


def shift_points(points: Sequence[GridPoint], delay_steps: int) -> list[GridPoint]:
    if not points:
        return []
    shifted: list[GridPoint] = []
    for index in range(len(points)):
        shifted.append(points[max(0, index - delay_steps)])
    return shifted


def format_translate_values(points: Sequence[GridPoint]) -> str:
    return ";".join(f"{point.x:.1f} {point.y:.1f}" for point in points)


def format_rotation_values(angles: Sequence[float]) -> str:
    return ";".join(f"{angle:.1f}" for angle in angles)


def format_key_times(count: int) -> str:
    if count <= 1:
        return "0;1"
    return ";".join(f"{index / float(count - 1):.5f}" for index in range(count))


def hidden_loop_opacity_animation(path: SnakePath) -> str:
    total_points = len(path.full_points)
    hide_progress = progress_at(path.hidden_start_index, total_points)
    fade_out_progress = min(hide_progress + REENTRY_FADE, 0.999)
    fade_in_progress = max(fade_out_progress, 1.0 - REENTRY_FADE)
    return (
        f'<animate attributeName="opacity" values="1;1;0;0;1" '
        f'keyTimes="0;{hide_progress:.5f};{fade_out_progress:.5f};{fade_in_progress:.5f};1" '
        f'dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
    )


def reveal_animation(reveal_step: int | None, total_points: int) -> tuple[str, str]:
    if reveal_step is None:
        return "", ""
    start = progress_at(reveal_step, total_points)
    end = min(start + FOOD_FADE, 0.999)
    return (
        ' opacity="0"',
        (
            f'<animate attributeName="opacity" values="0;0;1;1" '
            f'keyTimes="0;{start:.5f};{end:.5f};1" '
            f'dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
        ),
    )


def make_heatmap_cells(
    theme: Theme,
    weeks: Sequence[Sequence[ContributionDay]],
    path: SnakePath,
) -> str:
    total_points = len(path.full_points)
    parts: list[str] = []

    for column, week in enumerate(weeks):
        for day in week:
            x = GRID_LEFT + column * GRID_STEP
            y = GRID_TOP + day.weekday * GRID_STEP
            active_fill = color_for_day(theme, day)
            cell_class = "contribution-cell grid-animated"
            content = [
                f'<rect class="{cell_class}" x="{x:.1f}" y="{y:.1f}" width="{CELL_SIZE:.0f}" height="{CELL_SIZE:.0f}" rx="3" '
                f'fill="{theme.empty_fill}" stroke="{theme.empty_stroke}" stroke-width="0.9" />'
            ]

            if day.count > 0:
                visit_index = path.first_visible_indexes[(column, day.weekday)]
                start = progress_at(visit_index, total_points)
                end = min(start + CLEAR_FADE, 0.999)
                active_class = "contribution-cell active-cell grid-animated"
                content = [
                    f'<rect class="{active_class}" x="{x:.1f}" y="{y:.1f}" width="{CELL_SIZE:.0f}" height="{CELL_SIZE:.0f}" rx="3" '
                    f'fill="{active_fill}" stroke="{active_fill}" stroke-width="0.9">',
                    f'<animate attributeName="fill" values="{active_fill};{active_fill};{theme.empty_fill};{theme.empty_fill};{active_fill}" '
                    f'keyTimes="0;{start:.5f};{end:.5f};0.999;1" dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />',
                    f'<animate attributeName="stroke" values="{active_fill};{active_fill};{theme.empty_stroke};{theme.empty_stroke};{active_fill}" '
                    f'keyTimes="0;{start:.5f};{end:.5f};0.999;1" dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />',
                    "</rect>",
                ]

            parts.append("".join(content))

    return "".join(parts)


def make_static_grid(theme: Theme, weeks: Sequence[Sequence[ContributionDay]]) -> str:
    parts: list[str] = ['<g class="grid-static">']
    for column, week in enumerate(weeks):
        for day in week:
            x = GRID_LEFT + column * GRID_STEP
            y = GRID_TOP + day.weekday * GRID_STEP
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL_SIZE:.0f}" height="{CELL_SIZE:.0f}" rx="3" '
                f'fill="{theme.empty_fill}" stroke="{theme.empty_stroke}" stroke-width="0.9" />'
            )
    parts.append("</g>")
    return "".join(parts)


def make_food_svg(
    theme: Theme,
    weeks: Sequence[Sequence[ContributionDay]],
    path: SnakePath,
) -> str:
    total_points = len(path.full_points)
    half = FOOD_MARKER_SIZE / 2.0
    parts: list[str] = []

    for column, week in enumerate(weeks):
        for day in week:
            if day.count <= 0:
                continue
            point = make_grid_point(column, day.weekday)
            visit_index = path.first_visible_indexes[(column, day.weekday)]
            hide_progress = progress_at(visit_index, total_points)
            hidden_progress = min(hide_progress + FOOD_FADE, 0.999)
            parts.append(
                (
                    f'<g class="food-marker snake-animated" transform="translate({point.x:.1f} {point.y:.1f})">'
                    f'<animate attributeName="opacity" values="1;1;0;0;1" '
                    f'keyTimes="0;{hide_progress:.5f};{hidden_progress:.5f};0.999;1" '
                    f'dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
                    f'<circle cx="0" cy="0" r="{half:.2f}" fill="{theme.food_fill}" stroke="{theme.food_stroke}" stroke-width="0.7" />'
                    f"</g>"
                )
            )
    return "".join(parts)


def head_inner_svg(theme: Theme) -> str:
    bridge_x = -(HEAD_LENGTH / 2.0) - HEAD_BRIDGE_OVERLAP
    bridge_y = -(HEAD_BRIDGE_HEIGHT / 2.0)
    head_path = (
        f"M {-HEAD_LENGTH / 2.0:.2f} {-HEAD_HEIGHT / 2.0:.2f} "
        f"H {HEAD_LENGTH / 10.0:.2f} "
        f"L {HEAD_LENGTH / 2.0:.2f} 0 "
        f"L {HEAD_LENGTH / 10.0:.2f} {HEAD_HEIGHT / 2.0:.2f} "
        f"H {-HEAD_LENGTH / 2.0:.2f} Z"
    )
    return (
        f'<rect x="{bridge_x:.2f}" y="{bridge_y:.2f}" width="{HEAD_BRIDGE_WIDTH:.2f}" '
        f'height="{HEAD_BRIDGE_HEIGHT:.2f}" rx="3.2" fill="url(#{theme.name}-snake-body)" '
        f'stroke="{theme.snake_stroke}" stroke-width="1.0" />'
        f'<path d="{head_path}" fill="url(#{theme.name}-snake-head)" '
        f'stroke="{theme.head_stroke}" stroke-width="1.0" />'
        f'<circle cx="-2.10" cy="-2.55" r="0.95" fill="{theme.eye}" />'
        f'<circle cx="-2.10" cy="2.55" r="0.95" fill="{theme.eye}" />'
    )


def make_body_segments(theme: Theme, path: SnakePath) -> str:
    total_points = len(path.full_points)
    key_times = format_key_times(total_points)
    translate_values_cache: dict[int, str] = {}
    parts: list[str] = []
    segment_total = segment_total_for_food_count(len(path.active_visit_indexes))

    for segment_index in range(segment_total):
        delay_steps = (segment_index + 1) * SEGMENT_STEP_GAP
        if delay_steps not in translate_values_cache:
            translate_values_cache[delay_steps] = format_translate_values(shift_points(path.full_points, delay_steps))

        reveal_step: int | None = None
        if segment_index >= BASE_SEGMENTS:
            reveal_index = segment_index - BASE_SEGMENTS
            if reveal_index < len(path.active_visit_indexes):
                reveal_step = path.active_visit_indexes[reveal_index]
        initial_opacity, reveal = reveal_animation(reveal_step, total_points)
        parts.append(
            (
                f'<g class="snake-animated">'
                f"{hidden_loop_opacity_animation(path)}"
                f"<g{initial_opacity}>"
                f"{reveal}"
                f'<g filter="url(#{theme.name}-snake-shadow)">'
                f'<rect x="-{BODY_BLOCK_SIZE / 2.0:.2f}" y="-{BODY_BLOCK_SIZE / 2.0:.2f}" '
                f'width="{BODY_BLOCK_SIZE:.2f}" height="{BODY_BLOCK_SIZE:.2f}" rx="{BODY_BLOCK_RADIUS:.2f}" '
                f'fill="url(#{theme.name}-snake-body)" stroke="{theme.snake_stroke}" stroke-width="1.0" />'
                f'<animateTransform attributeName="transform" type="translate" '
                f'values="{translate_values_cache[delay_steps]}" keyTimes="{key_times}" '
                f'dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
                f"</g></g></g>"
            )
        )
    return "".join(parts)


def make_head_svg(theme: Theme, path: SnakePath) -> str:
    total_points = len(path.full_points)
    key_times = format_key_times(total_points)
    translate_values = format_translate_values(path.full_points)
    rotate_values = format_rotation_values(path.heading_angles)
    return (
        f'<g class="snake-animated">'
        f"{hidden_loop_opacity_animation(path)}"
        f'<g filter="url(#{theme.name}-snake-shadow)">'
        f'<animateTransform attributeName="transform" type="translate" values="{translate_values}" '
        f'keyTimes="{key_times}" dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
        f'<g>{head_inner_svg(theme)}'
        f'<animateTransform attributeName="transform" type="rotate" values="{rotate_values}" '
        f'keyTimes="{key_times}" calcMode="discrete" dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
        f"</g></g></g>"
    )


def make_static_snapshot(theme: Theme, path: SnakePath) -> str:
    if not path.full_points:
        return ""

    end_step = max(0, path.hidden_start_index - 1)
    segment_total = segment_total_for_food_count(len(path.active_visit_indexes))
    parts: list[str] = ['<g class="snake-static">']

    for segment_index in reversed(range(segment_total)):
        delay_steps = (segment_index + 1) * SEGMENT_STEP_GAP
        point = path.full_points[max(0, end_step - delay_steps)]
        parts.append(
            f'<rect x="{point.x - BODY_BLOCK_SIZE / 2.0:.2f}" y="{point.y - BODY_BLOCK_SIZE / 2.0:.2f}" '
            f'width="{BODY_BLOCK_SIZE:.2f}" height="{BODY_BLOCK_SIZE:.2f}" rx="{BODY_BLOCK_RADIUS:.2f}" '
            f'fill="url(#{theme.name}-snake-body)" stroke="{theme.snake_stroke}" stroke-width="1.0" />'
        )

    head_point = path.full_points[end_step]
    head_angle = path.heading_angles[end_step] if path.heading_angles else 0.0
    parts.append(
        f'<g transform="translate({head_point.x:.2f} {head_point.y:.2f}) rotate({head_angle:.1f})">'
        f"{head_inner_svg(theme)}"
        f"</g>"
    )
    parts.append("</g>")
    return "".join(parts)


def make_month_labels(months: Sequence[tuple[int, str]], theme: Theme) -> str:
    parts: list[str] = []
    for week_index, label in months:
        x = GRID_LEFT + week_index * GRID_STEP
        parts.append(
            f'<text x="{x:.1f}" y="100" fill="{theme.meta}" font-family="Segoe UI, Microsoft YaHei, sans-serif" '
            f'font-size="10">{html.escape(label)}</text>'
        )
    return "".join(parts)


def make_weekday_labels(theme: Theme) -> str:
    labels = [("Mon", 1), ("Wed", 3), ("Fri", 5)]
    parts: list[str] = []
    for label, weekday in labels:
        y = GRID_TOP + weekday * GRID_STEP + CELL_SIZE / 2.0 + 1.0
        parts.append(
            f'<text x="10" y="{y:.1f}" fill="{theme.meta}" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="10">{label}</text>'
        )
    return "".join(parts)


def render_svg(user: str, theme: Theme, total_contributions: int, weeks: list[list[ContributionDay]]) -> str:
    if not weeks:
        raise SystemExit("No contribution weeks returned.")

    flat_days = flatten_days(weeks)
    if not flat_days:
        raise SystemExit("No contribution days returned.")

    path = build_snake_path(weeks)
    months = build_month_labels(weeks)
    start_date = min(day.date for day in flat_days)
    end_date = max(day.date for day in flat_days)
    active_count = sum(1 for day in flat_days if day.count > 0)
    grid_width = len(weeks) * GRID_STEP - 4

    return (
        f'<svg width="{CARD_WIDTH}" height="{CARD_HEIGHT}" viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">'
        f'<title id="title">{html.escape(user)} GitHub contribution snake</title>'
        f'<desc id="desc">A classic GitHub contribution snake animation that clears contribution cells and grows after eating active cells.</desc>'
        f"<defs>"
        f'<linearGradient id="{theme.name}-snake-body" x1="-10" y1="-10" x2="10" y2="10" gradientUnits="userSpaceOnUse">'
        f'<stop stop-color="{theme.snake_fill_alt}" />'
        f'<stop offset="1" stop-color="{theme.snake_fill}" />'
        f"</linearGradient>"
        f'<linearGradient id="{theme.name}-snake-head" x1="-10" y1="-10" x2="10" y2="10" gradientUnits="userSpaceOnUse">'
        f'<stop stop-color="{theme.head_fill_alt}" />'
        f'<stop offset="1" stop-color="{theme.head_fill}" />'
        f"</linearGradient>"
        f'<filter id="{theme.name}-snake-shadow" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feDropShadow dx="0" dy="0" stdDeviation="{SNAKE_SHADOW_STDDEV:.1f}" '
        f'flood-color="{theme.shadow_color}" flood-opacity="0.18" />'
        f"</filter>"
        f'<clipPath id="{theme.name}-grid-clip">'
        f'<rect x="{GRID_LEFT + GRID_CLIP_INSET:.1f}" y="{GRID_TOP + GRID_CLIP_INSET:.1f}" '
        f'width="{grid_width - GRID_CLIP_INSET * 2:.1f}" height="{GRID_HEIGHT - GRID_CLIP_INSET * 2:.1f}" rx="6" />'
        f"</clipPath>"
        f"</defs>"
        f"<style>"
        f".grid-static,.snake-static{{display:none;}}"
        f"@media (prefers-reduced-motion: reduce){{.grid-animated,.snake-animated{{display:none;}}.grid-static,.snake-static{{display:inline;}}}}"
        f"</style>"
        f'<rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" rx="{CARD_RADIUS}" fill="{theme.card_bg}" />'
        f'<rect x="1" y="1" width="{CARD_WIDTH - 2}" height="{CARD_HEIGHT - 2}" rx="{CARD_RADIUS - 1}" stroke="{theme.card_border}" />'
        f'<rect x="28" y="24" width="{CARD_WIDTH - 56}" height="222" rx="14" fill="{theme.panel_bg}" stroke="{theme.panel_border}" />'
        f'<text x="{GRID_LEFT:.0f}" y="46" fill="{theme.title}" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="20" font-weight="700">GitHub contribution snake</text>'
        f'<text x="{GRID_LEFT:.0f}" y="68" fill="{theme.subtitle}" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="12">{html.escape(user)} · {total_contributions} contributions</text>'
        f'<text x="{GRID_LEFT:.0f}" y="86" fill="{theme.meta}" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="10">{start_date.isoformat()} to {end_date.isoformat()}</text>'
        f'<text x="{CARD_WIDTH - 38}" y="46" text-anchor="end" fill="{theme.meta}" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="10">active cells {active_count}</text>'
        f"{make_month_labels(months, theme)}"
        f"{make_weekday_labels(theme)}"
        f'<g clip-path="url(#{theme.name}-grid-clip)">'
        f"{make_heatmap_cells(theme, weeks, path)}"
        f"{make_static_grid(theme, weeks)}"
        f"{make_food_svg(theme, weeks, path)}"
        f"{make_body_segments(theme, path)}"
        f"{make_head_svg(theme, path)}"
        f"{make_static_snapshot(theme, path)}"
        f"</g>"
        f"</svg>"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--github-user", required=True, help="GitHub login to query.")
    parser.add_argument("--theme", choices=sorted(THEMES.keys()), required=True, help="SVG theme.")
    parser.add_argument("--output", required=True, help="Output SVG path.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    token = require_token()
    total_contributions, weeks = fetch_contributions(args.github_user, token)
    svg = render_svg(args.github_user, THEMES[args.theme], total_contributions, weeks)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
