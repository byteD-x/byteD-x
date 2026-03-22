#!/usr/bin/env python3
"""Generate a polished GitHub contribution snake SVG.

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
from typing import Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GRAPHQL_ENDPOINT = "https://api.github.com/graphql"
CARD_WIDTH = 1026
CARD_HEIGHT = 294
GRID_LEFT = 38.0
GRID_TOP = 108.0
GRID_STEP = 18.0
CELL_SIZE = 14.0
GRID_HEIGHT = 122.0
CARD_RADIUS = 26
LOOP_DURATION = 16.0
PULSE_DURATION = 0.96
SPAWN_FADE = 0.010
FOOD_FADE = 0.010
BASE_SEGMENTS = 6
MAX_SEGMENTS = 18

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
    card_start: str
    card_end: str
    border: str
    panel_fill: str
    title: str
    subtitle: str
    meta: str
    path_stroke: str
    shadow_color: str
    food_glow: str
    body_start: str
    body_end: str
    head_start: str
    head_end: str
    eye: str
    tongue: str
    food: str
    level_none: str
    level_1: str
    level_2: str
    level_3: str
    level_4: str
    level_none_opacity: float
    level_1_opacity: float
    level_2_opacity: float
    level_3_opacity: float
    level_4_opacity: float
    stats_bg: str
    stats_stroke: str


THEMES = {
    "light": Theme(
        name="light",
        card_start="#FCFDFE",
        card_end="#F5F7FB",
        border="#D6DCE8",
        panel_fill="#DBEAFE",
        title="#0F172A",
        subtitle="#334155",
        meta="#2563EB",
        path_stroke="#CBD5E1",
        shadow_color="#93C5FD",
        food_glow="#FCD34D",
        body_start="#2563EB",
        body_end="#60A5FA",
        head_start="#0F172A",
        head_end="#2563EB",
        eye="#F8FAFC",
        tongue="#F87171",
        food="#F59E0B",
        level_none="#DCEAFE",
        level_1="#BFDBFE",
        level_2="#93C5FD",
        level_3="#60A5FA",
        level_4="#2563EB",
        level_none_opacity=0.60,
        level_1_opacity=0.72,
        level_2_opacity=0.84,
        level_3_opacity=0.90,
        level_4_opacity=0.96,
        stats_bg="#EEF4FF",
        stats_stroke="#D6E4FF",
    ),
    "dark": Theme(
        name="dark",
        card_start="#0B1220",
        card_end="#020617",
        border="#1E293B",
        panel_fill="#0F172A",
        title="#E2E8F0",
        subtitle="#94A3B8",
        meta="#60A5FA",
        path_stroke="#334155",
        shadow_color="#1D4ED8",
        food_glow="#F59E0B",
        body_start="#2563EB",
        body_end="#38BDF8",
        head_start="#E2E8F0",
        head_end="#60A5FA",
        eye="#020617",
        tongue="#F87171",
        food="#F59E0B",
        level_none="#1F2937",
        level_1="#1D4ED8",
        level_2="#2563EB",
        level_3="#38BDF8",
        level_4="#7DD3FC",
        level_none_opacity=0.68,
        level_1_opacity=0.74,
        level_2_opacity=0.82,
        level_3_opacity=0.90,
        level_4_opacity=0.96,
        stats_bg="#0F172A",
        stats_stroke="#1E293B",
    ),
}


@dataclass(frozen=True)
class ContributionDay:
    date: dt.date
    count: int
    level: str
    weekday: int


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


def color_for_day(theme: Theme, day: ContributionDay) -> tuple[str, float]:
    if day.level == "FOURTH_QUARTILE":
        return theme.level_4, theme.level_4_opacity
    if day.level == "THIRD_QUARTILE":
        return theme.level_3, theme.level_3_opacity
    if day.level == "SECOND_QUARTILE":
        return theme.level_2, theme.level_2_opacity
    if day.level == "FIRST_QUARTILE":
        return theme.level_1, theme.level_1_opacity
    return theme.level_none, theme.level_none_opacity


def build_month_labels(weeks: list[list[ContributionDay]]) -> list[tuple[int, str]]:
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


def build_path_points(
    weeks: list[list[ContributionDay]],
) -> tuple[list[tuple[float, float]], list[tuple[float, float]], list[ContributionDay], dict[dt.date, tuple[float, float]]]:
    forward_points: list[tuple[float, float]] = []
    forward_days: list[ContributionDay] = []
    centers: dict[dt.date, tuple[float, float]] = {}

    for week_index, week in enumerate(weeks):
        ordered_days = week if week_index % 2 == 0 else list(reversed(week))
        for day in ordered_days:
            center_x = GRID_LEFT + week_index * GRID_STEP + CELL_SIZE / 2.0
            center_y = GRID_TOP + day.weekday * GRID_STEP + CELL_SIZE / 2.0
            point = (center_x, center_y)
            forward_points.append(point)
            forward_days.append(day)
            centers[day.date] = point

    reverse_points = list(reversed(forward_points[:-1]))
    full_points = forward_points + reverse_points
    return full_points, forward_points, forward_days, centers


def choose_food_indices(days: list[ContributionDay], target_count: int = 12) -> list[int]:
    nonzero_days = [index for index, day in enumerate(days) if day.count > 0]
    if not nonzero_days:
        return []

    target_count = max(6, min(target_count, len(nonzero_days)))
    if len(nonzero_days) <= target_count:
        return nonzero_days

    selections: list[int] = []
    anchor_step = (len(nonzero_days) - 1) / float(target_count - 1)

    for slot in range(target_count):
        anchor_position = round(slot * anchor_step)
        start = max(0, anchor_position - 2)
        end = min(len(nonzero_days), anchor_position + 3)
        candidate_indexes = nonzero_days[start:end]
        chosen_index = max(
            candidate_indexes,
            key=lambda index: (
                days[index].count,
                days[index].level == "FOURTH_QUARTILE",
                days[index].level == "THIRD_QUARTILE",
                -abs(index - nonzero_days[anchor_position]),
            ),
        )
        selections.append(chosen_index)

    return sorted(set(selections))


def format_path(points: Iterable[tuple[float, float]]) -> str:
    points_list = list(points)
    if not points_list:
        return ""
    values = [f"M {points_list[0][0]:.1f} {points_list[0][1]:.1f}"]
    for x, y in points_list[1:]:
        values.append(f"L {x:.1f} {y:.1f}")
    return " ".join(values)


def progress_at(index: int, total_points: int) -> float:
    if total_points <= 1:
        return 0.0
    return index / float(total_points - 1)


def stats_summary(days: list[ContributionDay]) -> tuple[int, int, int]:
    active_cells = sum(1 for day in days if day.count > 0)
    best_day = max((day.count for day in days), default=0)
    streak_like = max(sum(1 for day in week if day.count > 0) for week in chunk_days(days))
    return active_cells, best_day, streak_like


def chunk_days(days: list[ContributionDay], width: int = 7) -> Iterable[list[ContributionDay]]:
    for index in range(0, len(days), width):
        yield days[index : index + width]


def make_food_svg(theme: Theme, food_indices: list[int], days: list[ContributionDay], centers: dict[dt.date, tuple[float, float]], total_points: int) -> str:
    parts: list[str] = []
    for index in food_indices:
        day = days[index]
        cx, cy = centers[day.date]
        eat_progress = progress_at(index, total_points)
        hide_progress = min(eat_progress + FOOD_FADE, 0.999)
        parts.append(
            (
                f'<g filter="url(#{theme.name}-food-glow)">'
                f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="3.6" fill="{theme.food}">'
                f'<animate attributeName="r" values="3.1;4.5;3.1" dur="{PULSE_DURATION:.2f}s" repeatCount="indefinite" />'
                f'<animate attributeName="opacity" values="1;1;0;0;1" '
                f'keyTimes="0;{eat_progress:.5f};{hide_progress:.5f};0.999;1" '
                f'dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
                f"</circle></g>"
            )
        )
    return "".join(parts)


def make_body_segments(theme: Theme, food_indices: list[int], total_points: int) -> str:
    extra_segments = min(len(food_indices), MAX_SEGMENTS - BASE_SEGMENTS)
    segment_total = BASE_SEGMENTS + extra_segments
    if total_points <= 0:
        return ""

    time_per_step = LOOP_DURATION / max(total_points - 1, 1)
    segment_spacing = time_per_step * 2.45
    parts: list[str] = []

    for segment_index in range(segment_total):
        progress = segment_index / float(max(segment_total - 1, 1))
        rx = 4.1 + progress * 1.2
        ry = 3.75 + progress * 0.7
        begin = -(segment_total - 1 - segment_index) * segment_spacing

        opacity_animation = ""
        if segment_index >= BASE_SEGMENTS:
            food_progress = progress_at(food_indices[segment_index - BASE_SEGMENTS], total_points)
            reveal_progress = min(food_progress + SPAWN_FADE, 0.999)
            opacity_animation = (
                f'<animate attributeName="opacity" values="0;0;1;1" '
                f'keyTimes="0;{food_progress:.5f};{reveal_progress:.5f};1" '
                f'dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
            )
        group_opacity = ' opacity="0"' if opacity_animation else ""

        parts.append(
            (
                f'<g filter="url(#{theme.name}-snake-glow)" opacity="1">'
                f"<g{group_opacity}>"
                f'<ellipse cx="0" cy="0" rx="{rx:.2f}" ry="{ry:.2f}" fill="url(#{theme.name}-body-gradient)" />'
                f"{opacity_animation}"
                f'<animateMotion dur="{LOOP_DURATION:.1f}s" begin="{begin:.3f}s" repeatCount="indefinite" rotate="auto">'
                f'<mpath href="#{theme.name}-snake-path" />'
                f"</animateMotion>"
                f"</g></g>"
            )
        )

    return "".join(parts)


def make_head_svg(theme: Theme) -> str:
    return (
        f'<g filter="url(#{theme.name}-snake-glow)">'
        f"<g>"
        f'<ellipse cx="0" cy="0" rx="6.45" ry="5.85" fill="url(#{theme.name}-head-gradient)" />'
        f'<circle cx="2.15" cy="-1.55" r="0.95" fill="{theme.eye}" />'
        f'<circle cx="2.15" cy="1.55" r="0.95" fill="{theme.eye}" />'
        f'<circle cx="3.85" cy="0" r="0.55" fill="{theme.tongue}" fill-opacity="0.92" />'
        f'<animateMotion dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" rotate="auto">'
        f'<mpath href="#{theme.name}-snake-path" />'
        f"</animateMotion>"
        f"</g></g>"
    )


def make_month_labels(months: list[tuple[int, str]], theme: Theme) -> str:
    parts: list[str] = []
    for week_index, label in months:
        x = GRID_LEFT + week_index * GRID_STEP
        parts.append(
            f'<text x="{x:.1f}" y="98" fill="{theme.meta}" font-family="Space Mono, Consolas, monospace" '
            f'font-size="10" font-weight="600">{html.escape(label)}</text>'
        )
    return "".join(parts)


def make_weekday_labels(theme: Theme) -> str:
    labels = [("Mon", 1), ("Wed", 3), ("Fri", 5)]
    parts = []
    for label, weekday in labels:
        y = GRID_TOP + weekday * GRID_STEP + CELL_SIZE / 2.0 + 1.0
        parts.append(
            f'<text x="10" y="{y:.1f}" fill="{theme.subtitle}" font-family="Space Mono, Consolas, monospace" font-size="10">{label}</text>'
        )
    return "".join(parts)


def make_heatmap_rects(theme: Theme, weeks: list[list[ContributionDay]]) -> str:
    parts: list[str] = []
    for week_index, week in enumerate(weeks):
        for day in week:
            x = GRID_LEFT + week_index * GRID_STEP
            y = GRID_TOP + day.weekday * GRID_STEP
            fill, opacity = color_for_day(theme, day)
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL_SIZE:.0f}" height="{CELL_SIZE:.0f}" rx="4" '
                f'fill="{fill}" fill-opacity="{opacity:.2f}" />'
            )
    return "".join(parts)


def make_stats_row(theme: Theme, active_cells: int, best_day: int, weekly_burst: int) -> str:
    chips = [
        (GRID_LEFT, f"active:{active_cells}"),
        (GRID_LEFT + 176, f"peak:{best_day}"),
        (GRID_LEFT + 324, f"burst:{weekly_burst}"),
        (GRID_LEFT + 484, f"loop:{LOOP_DURATION:.0f}s"),
    ]
    parts: list[str] = []
    for x, label in chips:
        width = 118 if label.startswith("loop") else 128
        parts.append(
            f'<rect x="{x:.1f}" y="248" width="{width}" height="24" rx="12" fill="{theme.stats_bg}" stroke="{theme.stats_stroke}" />'
        )
        parts.append(
            f'<text x="{x + 16:.1f}" y="264" fill="{theme.subtitle}" font-family="Space Mono, Consolas, monospace" font-size="11" font-weight="600">{html.escape(label)}</text>'
        )
    return "".join(parts)


def render_svg(user: str, theme: Theme, total_contributions: int, weeks: list[list[ContributionDay]]) -> str:
    months = build_month_labels(weeks)
    full_points, forward_points, forward_days, centers = build_path_points(weeks)
    food_indices = choose_food_indices(forward_days)
    path_data = format_path(full_points)
    start_date = min(day.date for day in forward_days)
    end_date = max(day.date for day in forward_days)
    active_cells, best_day, weekly_burst = stats_summary(forward_days)
    meta_text = f"growth:adaptive loop:{LOOP_DURATION:.0f}s motion:polished"

    return (
        f'<svg width="{CARD_WIDTH}" height="{CARD_HEIGHT}" viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">'
        f'<title id="title">{html.escape(user)} contribution snake</title>'
        f'<desc id="desc">A polished GitHub contribution snake animation with adaptive growth and highlighted milestones.</desc>'
        f"<defs>"
        f'<linearGradient id="{theme.name}-card-bg" x1="0" y1="0" x2="{CARD_WIDTH}" y2="{CARD_HEIGHT}" gradientUnits="userSpaceOnUse">'
        f'<stop stop-color="{theme.card_start}" />'
        f'<stop offset="1" stop-color="{theme.card_end}" />'
        f"</linearGradient>"
        f'<linearGradient id="{theme.name}-body-gradient" x1="-8" y1="-8" x2="8" y2="8" gradientUnits="userSpaceOnUse">'
        f'<stop stop-color="{theme.body_start}" />'
        f'<stop offset="1" stop-color="{theme.body_end}" />'
        f"</linearGradient>"
        f'<linearGradient id="{theme.name}-head-gradient" x1="-8" y1="-8" x2="8" y2="8" gradientUnits="userSpaceOnUse">'
        f'<stop stop-color="{theme.head_start}" />'
        f'<stop offset="1" stop-color="{theme.head_end}" />'
        f"</linearGradient>"
        f'<filter id="{theme.name}-snake-glow" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feDropShadow dx="0" dy="0" stdDeviation="3.8" flood-color="{theme.shadow_color}" flood-opacity="0.45" />'
        f"</filter>"
        f'<filter id="{theme.name}-food-glow" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feDropShadow dx="0" dy="0" stdDeviation="3.2" flood-color="{theme.food_glow}" flood-opacity="0.55" />'
        f"</filter>"
        f'<clipPath id="{theme.name}-grid-clip">'
        f'<rect x="{GRID_LEFT:.0f}" y="{GRID_TOP:.0f}" width="{len(weeks) * GRID_STEP - 4:.0f}" height="{GRID_HEIGHT:.0f}" rx="8" />'
        f"</clipPath>"
        f'<path id="{theme.name}-snake-path" d="{path_data}" />'
        f"</defs>"
        f'<rect width="{CARD_WIDTH}" height="{CARD_HEIGHT}" rx="{CARD_RADIUS}" fill="url(#{theme.name}-card-bg)" />'
        f'<rect x="1" y="1" width="{CARD_WIDTH - 2}" height="{CARD_HEIGHT - 2}" rx="{CARD_RADIUS - 1}" stroke="{theme.border}" />'
        f'<rect x="28" y="24" width="{CARD_WIDTH - 56}" height="216" rx="20" fill="{theme.panel_fill}" fill-opacity="0.22" />'
        f'<text x="{GRID_LEFT:.0f}" y="38" fill="{theme.title}" font-family="Space Mono, Consolas, monospace" font-size="18" font-weight="700">contribution://snake</text>'
        f'<text x="{GRID_LEFT:.0f}" y="60" fill="{theme.subtitle}" font-family="Segoe UI, Microsoft YaHei, sans-serif" font-size="13" font-weight="600">'
        f"{html.escape(user)} route {total_contributions} contributions"
        f"</text>"
        f'<text x="{GRID_LEFT:.0f}" y="80" fill="{theme.subtitle}" font-family="Space Mono, Consolas, monospace" font-size="11">'
        f"{start_date.isoformat()} to {end_date.isoformat()}"
        f"</text>"
        f'<text x="{CARD_WIDTH - 38}" y="38" text-anchor="end" fill="{theme.meta}" font-family="Space Mono, Consolas, monospace" font-size="11" font-weight="700">'
        f"{html.escape(meta_text)}"
        f"</text>"
        f"{make_month_labels(months, theme)}"
        f'<g opacity="0.95">{make_heatmap_rects(theme, weeks)}</g>'
        f'<path d="{path_data}" stroke="{theme.path_stroke}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" stroke-opacity="0.38" />'
        f"<g>{make_weekday_labels(theme)}</g>"
        f'<g clip-path="url(#{theme.name}-grid-clip)">'
        f"<g>{make_food_svg(theme, food_indices, forward_days, centers, len(full_points))}</g>"
        f"<g>{make_body_segments(theme, food_indices, len(full_points))}{make_head_svg(theme)}</g>"
        f"</g>"
        f"{make_stats_row(theme, active_cells, best_day, weekly_burst)}"
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
    if not weeks:
        raise SystemExit("No contribution weeks returned.")

    svg = render_svg(args.github_user, THEMES[args.theme], total_contributions, weeks)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(svg, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
