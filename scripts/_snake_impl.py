from __future__ import annotations

import argparse
import calendar
import datetime as dt
import heapq
import html
import json
import math
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
FOOD_FADE = 0.012
CLEAR_FADE = 0.016
HIDDEN_FADE = 0.018
GROWTH_FADE = 0.020
BASE_SEGMENTS = 5
MAX_SEGMENTS = 24
BODY_STROKE_WIDTH = 14.0
HEAD_LENGTH = 14.0
HEAD_HEIGHT = 14.0
HEAD_BRIDGE_WIDTH = 14.0
HEAD_BRIDGE_HEIGHT = 14.0
HEAD_BRIDGE_OVERLAP = 0.0
FOOD_MARKER_SIZE = 8.0
SNAKE_SHADOW_STDDEV = 0.7
GUIDE_PATH_LENGTH = 1000.0
GUIDE_CORNER_RADIUS = 5.2
TURN_PENALTY = 0.75
BLANK_PENALTY = 2.60
MAX_VISIBLE_BLANK_RUN = 3

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

Direction = tuple[int, int]


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
class RouteMetrics:
    steps: int
    turns: int
    backtracks: int
    blank_steps: int
    max_blank_run: int
    left_steps: int


@dataclass(frozen=True)
class ActiveCluster:
    cells: tuple[GridPoint, ...]
    min_column: int
    max_column: int
    min_row: int
    max_row: int


@dataclass(frozen=True)
class ClusterPlan:
    cluster: ActiveCluster
    active_targets: tuple[GridPoint, ...]
    route_points: tuple[GridPoint, ...]
    metrics: RouteMetrics
    score: tuple[int, int, int, int]
    start_direction: Direction | None
    end_direction: Direction | None


@dataclass(frozen=True)
class ConnectorResult:
    points: tuple[GridPoint, ...]
    metrics: RouteMetrics
    visible: bool


@dataclass(frozen=True)
class SnakePath:
    active_targets: tuple[GridPoint, ...]
    clusters: tuple[ActiveCluster, ...]
    route_points: tuple[GridPoint, ...]
    guide_path_d: str
    target_progresses: dict[tuple[int, int], float]
    body_length_timeline: tuple[tuple[float, float], ...]
    hidden_segments: tuple[tuple[float, float], ...]
    total_length: float
    target_route_indexes: dict[tuple[int, int], int]
    final_head_point: GridPoint | None
    final_head_angle: float
    max_visible_blank_run: int


def require_token() -> str:
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not token:
        raise SystemExit("Missing GITHUB_TOKEN or GH_TOKEN for GitHub GraphQL access.")
    return token


def iso_datetime(value: dt.date, end_of_day: bool = False) -> str:
    suffix = "23:59:59Z" if end_of_day else "00:00:00Z"
    return f"{value.isoformat()}T{suffix}"


def fetch_contributions(user: str, token: str) -> tuple[int, list[list[ContributionDay]]]:
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


def progress_at(distance: float, total_length: float) -> float:
    if total_length <= 0:
        return 0.0
    return max(0.0, min(1.0, distance / total_length))


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


def active_points_from_weeks(weeks: Sequence[Sequence[ContributionDay]]) -> dict[tuple[int, int], GridPoint]:
    points: dict[tuple[int, int], GridPoint] = {}
    for column, week in enumerate(weeks):
        for day in week:
            if day.count > 0:
                points[(column, day.weekday)] = make_grid_point(column, day.weekday)
    return points


def build_active_clusters(weeks: Sequence[Sequence[ContributionDay]]) -> tuple[ActiveCluster, ...]:
    active_points = active_points_from_weeks(weeks)
    remaining = set(active_points)
    clusters: list[ActiveCluster] = []

    while remaining:
        start = remaining.pop()
        stack = [start]
        component = {start}

        while stack:
            column, row = stack.pop()
            for delta_column in (-1, 0, 1):
                for delta_row in (-1, 0, 1):
                    if delta_column == 0 and delta_row == 0:
                        continue
                    neighbor = (column + delta_column, row + delta_row)
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        component.add(neighbor)
                        stack.append(neighbor)

        cells = tuple(sorted((active_points[key] for key in component), key=lambda point: (point.column, point.row)))
        clusters.append(
            ActiveCluster(
                cells=cells,
                min_column=min(point.column for point in cells),
                max_column=max(point.column for point in cells),
                min_row=min(point.row for point in cells),
                max_row=max(point.row for point in cells),
            )
        )

    clusters.sort(key=lambda cluster: (cluster.min_column, cluster.min_row, cluster.max_column, cluster.max_row))
    return tuple(clusters)


def cluster_order_by_columns(cluster: ActiveCluster) -> tuple[GridPoint, ...]:
    ordered: list[GridPoint] = []
    columns = sorted({point.column for point in cluster.cells})
    for index, column in enumerate(columns):
        ordered.extend(
            sorted(
                (point for point in cluster.cells if point.column == column),
                key=lambda point: point.row,
                reverse=bool(index % 2),
            )
        )
    return tuple(ordered)


def cluster_order_by_rows(cluster: ActiveCluster) -> tuple[GridPoint, ...]:
    ordered: list[GridPoint] = []
    rows = sorted({point.row for point in cluster.cells})
    for index, row in enumerate(rows):
        ordered.extend(
            sorted(
                (point for point in cluster.cells if point.row == row),
                key=lambda point: point.column,
                reverse=bool(index % 2),
            )
        )
    return tuple(ordered)


def is_visible_point(point: GridPoint, width: int) -> bool:
    return 0 <= point.column < width and 0 <= point.row < GRID_ROWS


def direction_between(start: GridPoint, end: GridPoint) -> Direction | None:
    delta_column = end.column - start.column
    delta_row = end.row - start.row
    if delta_column == 0 and delta_row == 0:
        return None
    if delta_column != 0 and delta_row != 0:
        raise ValueError("Snake route segments must remain orthogonal.")
    if delta_column > 0:
        return (1, 0)
    if delta_column < 0:
        return (-1, 0)
    if delta_row > 0:
        return (0, 1)
    return (0, -1)


def opposite_direction(direction: Direction) -> Direction:
    return (-direction[0], -direction[1])


def angle_for_direction(direction: Direction | None) -> float:
    if direction is None:
        return 0.0
    if direction == (1, 0):
        return 0.0
    if direction == (-1, 0):
        return 180.0
    if direction == (0, 1):
        return 90.0
    return -90.0


def orthogonal_neighbors(coord: tuple[int, int], width: int) -> Iterable[tuple[int, int]]:
    column, row = coord
    candidates = ((column + 1, row), (column - 1, row), (column, row + 1), (column, row - 1))
    for next_column, next_row in candidates:
        if 0 <= next_column < width and 0 <= next_row < GRID_ROWS:
            yield next_column, next_row


def summarize_route(
    points: Sequence[GridPoint],
    active_coords: set[tuple[int, int]],
    initial_direction: Direction | None = None,
    visible_width: int | None = None,
) -> RouteMetrics:
    steps = 0
    turns = 0
    backtracks = 0
    blank_steps = 0
    max_blank_run = 0
    left_steps = 0
    blank_run = 0
    previous_direction = initial_direction

    for previous, current in zip(points, points[1:]):
        direction = direction_between(previous, current)
        if direction is None:
            continue
        steps += 1

        if previous_direction is not None and direction != previous_direction:
            turns += 1
            if direction == opposite_direction(previous_direction):
                backtracks += 1
        previous_direction = direction

        if direction == (-1, 0):
            left_steps += 1

        if visible_width is not None and not is_visible_point(current, visible_width):
            blank_run = 0
            continue

        if grid_key(current) in active_coords:
            blank_run = 0
            continue

        blank_steps += 1
        blank_run += 1
        max_blank_run = max(max_blank_run, blank_run)

    return RouteMetrics(
        steps=steps,
        turns=turns,
        backtracks=backtracks,
        blank_steps=blank_steps,
        max_blank_run=max_blank_run,
        left_steps=left_steps,
    )


def first_direction(points: Sequence[GridPoint]) -> Direction | None:
    for previous, current in zip(points, points[1:]):
        direction = direction_between(previous, current)
        if direction is not None:
            return direction
    return None


def last_direction(points: Sequence[GridPoint]) -> Direction | None:
    for previous, current in zip(reversed(points[:-1]), reversed(points[1:])):
        direction = direction_between(previous, current)
        if direction is not None:
            return direction
    return None


def append_points(target: list[GridPoint], new_points: Sequence[GridPoint]) -> None:
    if not new_points:
        return
    if not target:
        target.extend(new_points)
        return
    start_index = 1 if target[-1] == new_points[0] else 0
    target.extend(new_points[start_index:])


def find_visible_path(
    start: GridPoint,
    end: GridPoint,
    width: int,
    active_coords: set[tuple[int, int]],
    blocked_coords: set[tuple[int, int]],
    initial_direction: Direction | None = None,
) -> ConnectorResult | None:
    if start == end:
        metrics = RouteMetrics(steps=0, turns=0, backtracks=0, blank_steps=0, max_blank_run=0, left_steps=0)
        return ConnectorResult(points=(start,), metrics=metrics, visible=True)

    start_key = grid_key(start)
    end_key = grid_key(end)
    initial_blank = 0 if start_key in active_coords else 1
    start_state = (start_key, initial_direction, initial_blank)
    cost_so_far: dict[tuple[tuple[int, int], Direction | None, int], float] = {start_state: 0.0}
    previous_state: dict[tuple[tuple[int, int], Direction | None, int], tuple[tuple[int, int], Direction | None, int]] = {}
    queue: list[tuple[float, float, int, tuple[tuple[int, int], Direction | None, int]]] = []
    heapq.heappush(queue, (0.0, 0.0, 0, start_state))
    push_index = 1
    final_state: tuple[tuple[int, int], Direction | None, int] | None = None

    while queue:
        _, current_cost, _, state = heapq.heappop(queue)
        if current_cost > cost_so_far.get(state, float("inf")):
            continue

        current_coord, previous_direction, blank_streak = state
        if current_coord == end_key:
            final_state = state
            break

        for neighbor in orthogonal_neighbors(current_coord, width):
            if neighbor in blocked_coords and neighbor != end_key:
                continue

            direction = (neighbor[0] - current_coord[0], neighbor[1] - current_coord[1])
            
            if previous_direction is not None and direction == opposite_direction(previous_direction):
                continue

            is_blank = neighbor not in active_coords
            next_blank_streak = blank_streak + 1 if is_blank else 0
            if next_blank_streak > MAX_VISIBLE_BLANK_RUN:
                continue

            turn_cost = TURN_PENALTY if previous_direction is not None and direction != previous_direction else 0.0
            next_cost = current_cost + 1.0 + turn_cost + (BLANK_PENALTY if is_blank else 0.0)
            next_state = (neighbor, direction, next_blank_streak)

            if next_cost + 1e-9 >= cost_so_far.get(next_state, float("inf")):
                continue

            cost_so_far[next_state] = next_cost
            previous_state[next_state] = state
            heuristic = abs(end_key[0] - neighbor[0]) + abs(end_key[1] - neighbor[1])
            heapq.heappush(queue, (next_cost + heuristic, next_cost, push_index, next_state))
            push_index += 1

    if final_state is None:
        return None

    coords = [final_state[0]]
    state = final_state
    while state in previous_state:
        state = previous_state[state]
        coords.append(state[0])
    coords.reverse()

    points = tuple(make_grid_point(column, row) for column, row in coords)
    metrics = summarize_route(points, active_coords, initial_direction, visible_width=width)
    return ConnectorResult(points=points, metrics=metrics, visible=True)


def build_hidden_bridge_points(start: GridPoint, end: GridPoint) -> tuple[GridPoint, ...]:
    hidden_row = choose_hidden_row(start, end)
    points = [start]
    for row in walk_axis(start.row, hidden_row):
        points.append(make_grid_point(start.column, row))
    for column in walk_axis(start.column, end.column):
        points.append(make_grid_point(column, hidden_row))
    for row in walk_axis(hidden_row, end.row):
        points.append(make_grid_point(end.column, row))
    return tuple(points)


def choose_hidden_row(start: GridPoint, end: GridPoint) -> int:
    top_cost = start.row + end.row
    bottom_cost = (GRID_ROWS - 1 - start.row) + (GRID_ROWS - 1 - end.row)
    return -1 if top_cost <= bottom_cost else GRID_ROWS


def build_hidden_connector(
    start: GridPoint,
    end: GridPoint,
    active_coords: set[tuple[int, int]],
    width: int,
    initial_direction: Direction | None = None,
) -> ConnectorResult:
    points = build_hidden_bridge_points(start, end)
    metrics = summarize_route(points, active_coords, initial_direction, visible_width=width)
    return ConnectorResult(points=points, metrics=metrics, visible=False)


def build_cluster_plan(
    cluster: ActiveCluster,
    active_coords: set[tuple[int, int]],
    width: int,
) -> ClusterPlan:
    candidates = [cluster_order_by_columns(cluster), cluster_order_by_rows(cluster)]
    best_plan: ClusterPlan | None = None

    for active_targets in candidates:
        route_points = [active_targets[0]]
        visited = {grid_key(active_targets[0])}
        current_direction: Direction | None = None
        failed = False

        for target in active_targets[1:]:
            blocked_coords = active_coords - visited - {grid_key(target)}
            connector = find_visible_path(
                route_points[-1],
                target,
                width=width,
                active_coords=active_coords,
                blocked_coords=blocked_coords,
                initial_direction=current_direction,
            )
            if connector is None:
                failed = True
                break
            append_points(route_points, connector.points)
            visited.add(grid_key(target))
            current_direction = last_direction(route_points)

        if failed:
            continue

        metrics = summarize_route(route_points, active_coords, visible_width=width)
        score = (metrics.backtracks, metrics.turns, metrics.blank_steps, metrics.steps)
        plan = ClusterPlan(
            cluster=cluster,
            active_targets=active_targets,
            route_points=tuple(route_points),
            metrics=metrics,
            score=score,
            start_direction=first_direction(route_points),
            end_direction=last_direction(route_points),
        )
        if best_plan is None or plan.score < best_plan.score:
            best_plan = plan

    if best_plan is None:
        point = cluster.cells[0]
        metrics = RouteMetrics(steps=0, turns=0, backtracks=0, blank_steps=0, max_blank_run=0, left_steps=0)
        return ClusterPlan(
            cluster=cluster,
            active_targets=(point,),
            route_points=(point,),
            metrics=metrics,
            score=(0, 0, 0, 0),
            start_direction=None,
            end_direction=None,
        )
    return best_plan


def connector_cost_key(connector: ConnectorResult) -> tuple[int, int, int, int]:
    blank_rank = connector.metrics.blank_steps if connector.visible else MAX_VISIBLE_BLANK_RUN + 1
    return (
        connector.metrics.left_steps,
        connector.metrics.turns,
        blank_rank,
        connector.metrics.steps,
    )


def choose_cluster_order(
    cluster_plans: Sequence[ClusterPlan],
    active_coords: set[tuple[int, int]],
    width: int,
) -> tuple[list[ClusterPlan], list[ConnectorResult]]:
    if not cluster_plans:
        return [], []

    remaining = list(cluster_plans)
    current = min(remaining, key=lambda plan: (plan.cluster.min_column, plan.cluster.min_row, plan.cluster.max_row))
    remaining.remove(current)
    ordered = [current]
    connectors: list[ConnectorResult] = []

    while remaining:
        remaining_active = {grid_key(point) for plan in remaining for point in plan.active_targets}
        candidate_rows: list[tuple[tuple[int, int, int, int], int, int, ConnectorResult, ClusterPlan]] = []

        for plan in remaining:
            visible_connector = find_visible_path(
                current.route_points[-1],
                plan.active_targets[0],
                width=width,
                active_coords=active_coords,
                blocked_coords=remaining_active - {grid_key(plan.active_targets[0])},
                initial_direction=current.end_direction,
            )
            connector = visible_connector or build_hidden_connector(
                current.route_points[-1],
                plan.active_targets[0],
                active_coords=active_coords,
                width=width,
                initial_direction=current.end_direction,
            )
            candidate_rows.append(
                (
                    connector_cost_key(connector),
                    plan.cluster.min_column,
                    plan.cluster.min_row,
                    connector,
                    plan,
                )
            )

        _, _, _, connector, current = min(candidate_rows, key=lambda row: (row[0], row[1], row[2]))
        remaining.remove(current)
        ordered.append(current)
        connectors.append(connector)

    return ordered, connectors


def build_entry_points(first_point: GridPoint, reference_point: GridPoint | None) -> tuple[GridPoint, ...]:
    hidden_row = choose_hidden_row(first_point, reference_point or first_point)
    points = [make_grid_point(first_point.column, hidden_row)]
    for row in walk_axis(hidden_row, first_point.row):
        points.append(make_grid_point(first_point.column, row))
    return tuple(points)


def build_exit_points(last_point: GridPoint, reference_point: GridPoint | None) -> tuple[GridPoint, ...]:
    hidden_row = choose_hidden_row(reference_point or last_point, last_point)
    points = [last_point]
    for row in walk_axis(last_point.row, hidden_row):
        points.append(make_grid_point(last_point.column, row))
    return tuple(points)


def cumulative_lengths(points: Sequence[GridPoint]) -> list[float]:
    lengths = [0.0]
    for previous, current in zip(points, points[1:]):
        lengths.append(lengths[-1] + math.hypot(current.x - previous.x, current.y - previous.y))
    return lengths


def normalize_timed_values(values: Sequence[tuple[float, float]]) -> tuple[tuple[float, float], ...]:
    normalized: list[tuple[float, float]] = []
    for progress, value in sorted(values, key=lambda item: item[0]):
        clamped_progress = max(0.0, min(1.0, progress))
        if normalized and abs(clamped_progress - normalized[-1][0]) < 1e-9:
            normalized[-1] = (clamped_progress, value)
            continue
        normalized.append((clamped_progress, value))
    if not normalized:
        return ((0.0, 0.0), (1.0, 0.0))
    if normalized[0][0] > 0.0:
        normalized.insert(0, (0.0, normalized[0][1]))
    if normalized[-1][0] < 1.0:
        normalized.append((1.0, normalized[-1][1]))
    return tuple(normalized)


def build_body_length_timeline(
    active_targets: Sequence[GridPoint],
    target_progresses: dict[tuple[int, int], float],
) -> tuple[tuple[float, float], ...]:
    timeline: list[tuple[float, float]] = [(0.0, float(BASE_SEGMENTS))]
    current_segments = BASE_SEGMENTS
    growth_slots = MAX_SEGMENTS - BASE_SEGMENTS

    for target in active_targets[:growth_slots]:
        progress = target_progresses[grid_key(target)]
        timeline.append((progress, float(current_segments)))
        current_segments += 1
        timeline.append((min(progress + GROWTH_FADE, 0.999), float(current_segments)))

    timeline.append((0.999, float(current_segments)))
    timeline.append((1.0, float(BASE_SEGMENTS)))
    return normalize_timed_values(timeline)


def compress_route_points(points: Sequence[GridPoint]) -> tuple[GridPoint, ...]:
    if len(points) <= 2:
        return tuple(points)

    compressed = [points[0]]
    for index in range(1, len(points) - 1):
        previous = compressed[-1]
        current = points[index]
        following = points[index + 1]
        if direction_between(previous, current) == direction_between(current, following):
            continue
        compressed.append(current)
    compressed.append(points[-1])
    return tuple(compressed)


def build_guide_path_d(points: Sequence[GridPoint]) -> str:
    if not points:
        return ""

    compressed = compress_route_points(points)
    if len(compressed) == 1:
        point = compressed[0]
        return f"M {point.x:.2f} {point.y:.2f}"

    segments = [f"M {compressed[0].x:.2f} {compressed[0].y:.2f}"]

    for index in range(1, len(compressed)):
        current = compressed[index]
        segments.append(f"L {current.x:.2f} {current.y:.2f}")

    return " ".join(segments)


def head_angle_for_index(points: Sequence[GridPoint], index: int, width: int) -> float:
    current = points[index]

    for following in points[index + 1 :]:
        if following == current:
            continue
        if is_visible_point(following, width):
            return angle_for_direction(direction_between(current, following))
        break

    for previous in reversed(points[:index]):
        if previous == current:
            continue
        if is_visible_point(previous, width):
            return angle_for_direction(direction_between(previous, current))
        break

    return 0.0


def build_snake_path(weeks: Sequence[Sequence[ContributionDay]]) -> SnakePath:
    width = len(weeks)
    active_points = active_points_from_weeks(weeks)
    active_coords = set(active_points)
    clusters = build_active_clusters(weeks)

    if not clusters:
        return SnakePath(
            active_targets=(),
            clusters=(),
            route_points=(),
            guide_path_d="",
            target_progresses={},
            body_length_timeline=(),
            hidden_segments=(),
            total_length=0.0,
            target_route_indexes={},
            final_head_point=None,
            final_head_angle=0.0,
            max_visible_blank_run=0,
        )

    cluster_plans = [build_cluster_plan(cluster, active_coords, width) for cluster in clusters]
    ordered_plans, connectors = choose_cluster_order(cluster_plans, active_coords, width)

    route_points: list[GridPoint] = []
    hidden_index_ranges: list[tuple[int, int]] = []

    first_plan = ordered_plans[0]
    first_reference = first_plan.route_points[1] if len(first_plan.route_points) > 1 else first_plan.route_points[0]
    append_points(route_points, build_entry_points(first_plan.route_points[0], first_reference))
    append_points(route_points, first_plan.route_points)

    max_visible_blank_run = first_plan.metrics.max_blank_run

    for connector, plan in zip(connectors, ordered_plans[1:]):
        start_index = max(0, len(route_points) - 1)
        append_points(route_points, connector.points)
        end_index = len(route_points) - 1
        if not connector.visible and end_index > start_index:
            hidden_index_ranges.append((start_index, end_index))
        if connector.visible:
            max_visible_blank_run = max(max_visible_blank_run, connector.metrics.max_blank_run)
        append_points(route_points, plan.route_points)
        max_visible_blank_run = max(max_visible_blank_run, plan.metrics.max_blank_run)

    last_plan = ordered_plans[-1]
    last_reference = last_plan.route_points[-2] if len(last_plan.route_points) > 1 else last_plan.route_points[-1]
    append_points(route_points, build_exit_points(last_plan.route_points[-1], last_reference))

    cumulative = cumulative_lengths(route_points)
    total_length = cumulative[-1] if cumulative else 0.0
    active_targets = tuple(point for plan in ordered_plans for point in plan.active_targets)

    target_route_indexes: dict[tuple[int, int], int] = {}
    active_keys = {grid_key(point) for point in active_targets}
    for index, point in enumerate(route_points):
        key = grid_key(point)
        if key in active_keys and key not in target_route_indexes:
            target_route_indexes[key] = index

    target_progresses = {
        key: progress_at(cumulative[index], total_length)
        for key, index in target_route_indexes.items()
    }
    body_length_timeline = build_body_length_timeline(active_targets, target_progresses)
    hidden_segments = tuple(
        (progress_at(cumulative[start], total_length), progress_at(cumulative[end], total_length))
        for start, end in hidden_index_ranges
    )

    final_target = active_targets[-1]
    final_index = target_route_indexes[grid_key(final_target)]
    final_head_point = route_points[final_index]
    final_head_angle = head_angle_for_index(route_points, final_index, width)

    return SnakePath(
        active_targets=active_targets,
        clusters=clusters,
        route_points=tuple(route_points),
        guide_path_d=build_guide_path_d(route_points),
        target_progresses=target_progresses,
        body_length_timeline=body_length_timeline,
        hidden_segments=hidden_segments,
        total_length=total_length,
        target_route_indexes=target_route_indexes,
        final_head_point=final_head_point,
        final_head_angle=final_head_angle,
        max_visible_blank_run=max_visible_blank_run,
    )


def segment_total_for_food_count(food_count: int) -> int:
    return min(MAX_SEGMENTS, BASE_SEGMENTS + max(food_count, 0))


def format_timed_key_times(values: Sequence[tuple[float, float]]) -> str:
    return ";".join(f"{progress:.5f}" for progress, _ in values)


def hidden_opacity_animation(hidden_segments: Sequence[tuple[float, float]]) -> str:
    if not hidden_segments:
        return ""

    values: list[tuple[float, float]] = [(0.0, 1.0)]
    for start, end in hidden_segments:
        fade_out = min(start + HIDDEN_FADE, end)
        fade_in = max(end - HIDDEN_FADE, fade_out)
        values.extend(
            [
                (start, 1.0),
                (fade_out, 0.0),
                (fade_in, 0.0),
                (end, 1.0),
            ]
        )
    values.append((1.0, 1.0))
    normalized = normalize_timed_values(values)
    opacity_values = ";".join(f"{value:.1f}" for _, value in normalized)
    return (
        f'<animate attributeName="opacity" values="{opacity_values}" '
        f'keyTimes="{format_timed_key_times(normalized)}" dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
    )


def body_dash_length(path: SnakePath, segment_count: float) -> float:
    if path.total_length <= 0:
        return 0.0
    unit_length = GUIDE_PATH_LENGTH * GRID_STEP / path.total_length
    return min(GUIDE_PATH_LENGTH, max(unit_length * segment_count, unit_length))


def body_dasharray_animation(path: SnakePath) -> str:
    if not path.body_length_timeline:
        return ""
    values = ";".join(
        f"{body_dash_length(path, segments):.2f} {GUIDE_PATH_LENGTH:.2f}"
        for _, segments in path.body_length_timeline
    )
    return (
        f'<animate attributeName="stroke-dasharray" values="{values}" '
        f'keyTimes="{format_timed_key_times(path.body_length_timeline)}" '
        f'dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
    )


def food_progress(path: SnakePath, key: tuple[int, int]) -> float:
    return path.target_progresses.get(key, 0.0)


def make_heatmap_cells(
    theme: Theme,
    weeks: Sequence[Sequence[ContributionDay]],
    path: SnakePath,
) -> str:
    parts: list[str] = []

    for column, week in enumerate(weeks):
        for day in week:
            x = GRID_LEFT + column * GRID_STEP
            y = GRID_TOP + day.weekday * GRID_STEP
            key = (column, day.weekday)
            active_fill = color_for_day(theme, day)
            cell_class = "contribution-cell grid-animated"
            content = [
                f'<rect class="{cell_class}" x="{x:.1f}" y="{y:.1f}" width="{CELL_SIZE:.0f}" height="{CELL_SIZE:.0f}" '
                f'fill="{theme.empty_fill}" stroke="{theme.empty_stroke}" stroke-width="0.9" />'
            ]

            if day.count > 0 and key in path.target_progresses:
                start = food_progress(path, key)
                end = min(start + CLEAR_FADE, 0.999)
                active_class = "contribution-cell active-cell grid-animated"
                content = [
                    f'<rect class="{active_class}" x="{x:.1f}" y="{y:.1f}" width="{CELL_SIZE:.0f}" height="{CELL_SIZE:.0f}" '
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
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL_SIZE:.0f}" height="{CELL_SIZE:.0f}" '
                f'fill="{theme.empty_fill}" stroke="{theme.empty_stroke}" stroke-width="0.9" />'
            )
    parts.append("</g>")
    return "".join(parts)


def make_body_clip_path(theme: Theme, weeks: Sequence[Sequence[ContributionDay]]) -> str:
    parts = [f'<clipPath id="{theme.name}-snake-body-clip" clipPathUnits="userSpaceOnUse">']
    for column, week in enumerate(weeks):
        for day in week:
            x = GRID_LEFT + column * GRID_STEP
            y = GRID_TOP + day.weekday * GRID_STEP
            parts.append(
                f'<rect x="{x:.1f}" y="{y:.1f}" width="{CELL_SIZE:.0f}" height="{CELL_SIZE:.0f}" />'
            )
    parts.append("</clipPath>")
    return "".join(parts)


def make_food_svg(
    theme: Theme,
    weeks: Sequence[Sequence[ContributionDay]],
    path: SnakePath,
) -> str:
    if not path.active_targets:
        return ""

    half = FOOD_MARKER_SIZE / 2.0
    parts: list[str] = []

    for column, week in enumerate(weeks):
        for day in week:
            if day.count <= 0:
                continue
            key = (column, day.weekday)
            if key not in path.target_progresses:
                continue
            point = make_grid_point(column, day.weekday)
            hide_progress = food_progress(path, key)
            hidden_progress = min(hide_progress + FOOD_FADE, 0.999)
            parts.append(
                (
                    f'<g class="food-marker snake-animated" transform="translate({point.x:.1f} {point.y:.1f})">'
                    f'<animate attributeName="opacity" values="1;1;0;0;1" '
                    f'keyTimes="0;{hide_progress:.5f};{hidden_progress:.5f};0.999;1" '
                    f'dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
                    f'<rect x="{-half:.2f}" y="{-half:.2f}" width="{FOOD_MARKER_SIZE:.2f}" height="{FOOD_MARKER_SIZE:.2f}" fill="{theme.food_fill}" stroke="{theme.food_stroke}" stroke-width="0.7" />'
                    f"</g>"
                )
            )
    return "".join(parts)


def head_inner_svg(theme: Theme) -> str:
    return (
        f'<rect x="7.0" y="-1.0" width="4.0" height="2.0" fill="{theme.food_fill}" />'
        f'<rect x="11.0" y="-3.0" width="2.0" height="2.0" fill="{theme.food_fill}" />'
        f'<rect x="11.0" y="1.0" width="2.0" height="2.0" fill="{theme.food_fill}" />'
        f'<rect x="{-HEAD_LENGTH / 2.0:.2f}" y="{-HEAD_HEIGHT / 2.0:.2f}" width="{HEAD_LENGTH:.2f}" '
        f'height="{HEAD_HEIGHT:.2f}" fill="url(#{theme.name}-snake-head)" />'
        f'<rect x="1.0" y="-4.0" width="2.5" height="2.5" fill="{theme.eye}" />'
        f'<rect x="1.0" y="1.5" width="2.5" height="2.5" fill="{theme.eye}" />'
    )


def make_body_window(theme: Theme, path: SnakePath) -> str:
    if not path.active_targets or not path.guide_path_d:
        return ""

    opacity_animation = hidden_opacity_animation(path.hidden_segments)
    initial_dash = body_dash_length(path, BASE_SEGMENTS)
    return (
        f'<g class="snake-animated">'
        f"{opacity_animation}"
        f'<path class="snake-body-window snake-animated" d="{path.guide_path_d}" pathLength="{GUIDE_PATH_LENGTH:.0f}" '
        f'fill="none" stroke="url(#{theme.name}-snake-body)" stroke-width="{BODY_STROKE_WIDTH:.2f}" '
        f'clip-path="url(#{theme.name}-snake-body-clip)" '
        f'stroke-linecap="square" stroke-linejoin="miter" '
        f'stroke-dasharray="{initial_dash:.2f} {GUIDE_PATH_LENGTH:.2f}" '
        f'stroke-dashoffset="{GUIDE_PATH_LENGTH:.2f}" filter="url(#{theme.name}-snake-shadow)">'
        f'<animate attributeName="stroke-dashoffset" values="{GUIDE_PATH_LENGTH:.2f};0" '
        f'dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" />'
        f"{body_dasharray_animation(path)}"
        f"</path></g>"
    )


def make_head_svg(theme: Theme, path: SnakePath) -> str:
    if not path.active_targets or not path.guide_path_d:
        return ""

    opacity_animation = hidden_opacity_animation(path.hidden_segments)
    return (
        f'<g class="snake-head snake-animated">'
        f"{opacity_animation}"
        f'<g filter="url(#{theme.name}-snake-shadow)">'
        f'<g>{head_inner_svg(theme)}'
        f'<animateMotion dur="{LOOP_DURATION:.1f}s" repeatCount="indefinite" rotate="auto">'
        f'<mpath href="#{theme.name}-guide-path" />'
        f"</animateMotion>"
        f"</g></g></g>"
    )


def make_static_snapshot(theme: Theme, path: SnakePath) -> str:
    if not path.active_targets or not path.guide_path_d or path.final_head_point is None:
        return ""

    final_target = path.active_targets[-1]
    final_progress = path.target_progresses[grid_key(final_target)]
    final_segments = segment_total_for_food_count(len(path.active_targets))
    dash_length = body_dash_length(path, float(final_segments))
    dash_offset = GUIDE_PATH_LENGTH - (final_progress * GUIDE_PATH_LENGTH)

    return (
        f'<g class="snake-static">'
        f'<path d="{path.guide_path_d}" pathLength="{GUIDE_PATH_LENGTH:.0f}" fill="none" '
        f'stroke="url(#{theme.name}-snake-body)" stroke-width="{BODY_STROKE_WIDTH:.2f}" '
        f'clip-path="url(#{theme.name}-snake-body-clip)" '
        f'stroke-linecap="square" stroke-linejoin="miter" '
        f'stroke-dasharray="{dash_length:.2f} {GUIDE_PATH_LENGTH:.2f}" '
        f'stroke-dashoffset="{dash_offset:.2f}" filter="url(#{theme.name}-snake-shadow)" />'
        f'<g transform="translate({path.final_head_point.x:.2f} {path.final_head_point.y:.2f}) rotate({path.final_head_angle:.1f})">'
        f"{head_inner_svg(theme)}"
        f"</g></g>"
    )


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
    guide_path_def = (
        f'<path id="{theme.name}-guide-path" d="{path.guide_path_d}" pathLength="{GUIDE_PATH_LENGTH:.0f}" />'
        if path.guide_path_d
        else ""
    )

    return (
        f'<svg width="{CARD_WIDTH}" height="{CARD_HEIGHT}" viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}" fill="none" '
        f'xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">'
        f'<title id="title">{html.escape(user)} GitHub contribution snake</title>'
        f'<desc id="desc">A GitHub contribution snake that only targets active cells, clears them, and grows on each bite.</desc>'
        f"<defs>"
        f"{guide_path_def}"
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
        f"{make_body_clip_path(theme, weeks)}"
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
        f"{make_body_window(theme, path)}"
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
