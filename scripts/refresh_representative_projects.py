#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

README_START_MARKER = "<!-- representative-projects:start -->"
README_END_MARKER = "<!-- representative-projects:end -->"
DEFAULT_USERNAME = "byteD-x"
DEFAULT_LIMIT = 4
REQUEST_TIMEOUT_SECONDS = 20


@dataclass(frozen=True)
class RepositoryCard:
    owner: str
    name: str
    url: str
    description: str
    language: str
    stars: int
    forks: int

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="根据 GitHub 实时仓库数据刷新 README 代表项目区块。")
    parser.add_argument("--readme", type=Path, default=Path("README.md"), help="需要回写的 README 路径。")
    parser.add_argument("--username", default=os.environ.get("PROFILE_USERNAME", DEFAULT_USERNAME), help="GitHub 用户名。")
    parser.add_argument(
        "--limit",
        type=int,
        default=int(os.environ.get("REPRESENTATIVE_REPOS_LIMIT", DEFAULT_LIMIT)),
        help="代表项目数量。",
    )
    parser.add_argument(
        "--fixture",
        type=Path,
        help="离线验证夹具文件，内容为仓库对象数组；提供后不访问网络。",
    )
    return parser.parse_args()


def build_headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "byteD-x-readme-refresh",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_json(url: str, token: str | None) -> Any:
    request = Request(url, headers=build_headers(token))
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        return json.load(response)


def load_fixture(path: Path) -> list[dict[str, Any]]:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_owned_repositories(username: str, token: str | None) -> list[dict[str, Any]]:
    page = 1
    repositories: list[dict[str, Any]] = []

    while True:
        url = (
            f"https://api.github.com/users/{username}/repos"
            f"?per_page=100&type=owner&sort=updated&page={page}"
        )
        page_items = fetch_json(url, token)
        if not isinstance(page_items, list) or not page_items:
            break

        repositories.extend(page_items)
        if len(page_items) < 100:
            break
        page += 1

    return repositories


def to_repository_card(raw_repo: dict[str, Any], username: str) -> RepositoryCard:
    owner = ((raw_repo.get("owner") or {}).get("login") or username).strip()
    name = str(raw_repo.get("name") or "").strip()
    description = str(raw_repo.get("description") or "").strip() or "该仓库暂未填写描述，README 将在下次刷新时继续同步。"
    language = str(raw_repo.get("language") or "").strip() or "待识别"
    stars = int(raw_repo.get("stargazers_count") or 0)
    forks = int(raw_repo.get("forks_count") or 0)
    url = str(raw_repo.get("html_url") or raw_repo.get("url") or f"https://github.com/{owner}/{name}").strip()

    return RepositoryCard(
        owner=owner,
        name=name,
        url=url,
        description=description,
        language=language,
        stars=stars,
        forks=forks,
    )


def parse_timestamp(value: str) -> float:
    if not value:
        return 0.0

    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
    except ValueError:
        return 0.0


def repository_rank_key(raw_repo: dict[str, Any]) -> tuple[int, int, int, float, int]:
    description = str(raw_repo.get("description") or "").strip()
    return (
        1 if description else 0,
        int(raw_repo.get("stargazers_count") or 0),
        int(raw_repo.get("forks_count") or 0),
        parse_timestamp(str(raw_repo.get("pushed_at") or raw_repo.get("updated_at") or "")),
        int(raw_repo.get("size") or 0),
    )


def select_repositories(repositories: list[dict[str, Any]], username: str, limit: int) -> list[RepositoryCard]:
    normalized_username = username.lower()
    filtered = [
        repo
        for repo in repositories
        if not repo.get("fork")
        and not repo.get("archived")
        and ((repo.get("owner") or {}).get("login") or "").lower() == normalized_username
        and str(repo.get("name") or "").lower() != normalized_username
    ]

    filtered.sort(key=repository_rank_key, reverse=True)
    return [to_repository_card(repo, username) for repo in filtered[:limit]]


def render_stats_badges(card: RepositoryCard) -> str:
    stars_url = (
        "https://img.shields.io/github/stars/"
        f"{quote(card.full_name)}?style=flat-square&color=2563EB&labelColor=18181B"
    )
    forks_url = (
        "https://img.shields.io/github/forks/"
        f"{quote(card.full_name)}?style=flat-square&color=60A5FA&labelColor=18181B"
    )
    last_commit_url = (
        "https://img.shields.io/github/last-commit/"
        f"{quote(card.full_name)}?style=flat-square&color=34D399&labelColor=18181B"
    )
    return "\n".join(
        [
            f'      <img src="{stars_url}" alt="{html.escape(card.name)} stars" />',
            f'      <img src="{forks_url}" alt="{html.escape(card.name)} forks" />',
            f'      <img src="{last_commit_url}" alt="{html.escape(card.name)} last commit" />',
        ]
    )


def render_card(card: RepositoryCard) -> str:
    description = html.escape(card.description)
    language = html.escape(card.language)
    name = html.escape(card.name)
    url = html.escape(card.url, quote=True)

    return "\n".join(
        [
            '    <td width="50%" valign="top" style="border: 1px solid #E4E4E7; padding: 16px;">',
            f'      <h4><a href="{url}" style="color: #2563EB; text-decoration: none;">{name}</a></h4>',
            f'      <p style="font-size: 13px; color: #52525B;">{description}</p>',
            f'      <code>{language}</code>',
            '      <br><br>',
            render_stats_badges(card),
            "    </td>",
        ]
    )


def render_empty_card() -> str:
    return "\n".join(
        [
            '    <td width="50%" valign="top" style="border: 1px solid #E4E4E7; padding: 16px;">',
            '      <p style="font-size: 13px; color: #A1A1AA;">暂无更多实时项目数据。</p>',
            "    </td>",
        ]
    )


def render_projects_table(cards: list[RepositoryCard]) -> str:
    rows: list[str] = ['<table width="100%" style="border-collapse: collapse; border: none;">']

    for index in range(0, len(cards), 2):
        rows.append("  <tr>")
        rows.append(render_card(cards[index]))
        if index + 1 < len(cards):
            rows.append(render_card(cards[index + 1]))
        else:
            rows.append(render_empty_card())
        rows.append("  </tr>")

    rows.append("</table>")
    return "\n".join(rows)


def replace_between_markers(content: str, replacement: str) -> str:
    if README_START_MARKER not in content or README_END_MARKER not in content:
        raise ValueError("README 中缺少代表项目标记，无法安全替换。")

    start = content.index(README_START_MARKER) + len(README_START_MARKER)
    end = content.index(README_END_MARKER)
    return f"{content[:start]}\n{replacement}\n{content[end:]}"


def main() -> int:
    args = parse_args()
    token = os.environ.get("GITHUB_TOKEN")

    try:
        raw_repositories = load_fixture(args.fixture) if args.fixture else fetch_owned_repositories(args.username, token)
        cards = select_repositories(raw_repositories, args.username, args.limit)
        if not cards:
            raise RuntimeError("未获取到可展示的代表项目数据。")

        readme_content = args.readme.read_text(encoding="utf-8")
        replacement = render_projects_table(cards)
        updated_content = replace_between_markers(readme_content, replacement)
        args.readme.write_text(updated_content, encoding="utf-8")
        return 0
    except (HTTPError, URLError, TimeoutError, RuntimeError, ValueError) as exc:
        print(f"刷新 README 代表项目失败：{exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
