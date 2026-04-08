#!/usr/bin/env python3
"""ZeroClaw 周提交统计脚本

使用方式:
    python3 scripts/commit_weekly_stats.py \\
        --owner ralf003 \\
        --repo zeroclaw \\
        --branch master \\
        --base-date 2026-04-08 \\
        --weeks 4

环境变量:
    GITHUB_TOKEN  (可选) GitHub Personal Access Token，可提升 API 速率上限
"""

import argparse
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import requests


def fetch_commits(owner: str, repo: str, branch: str, token: str | None = None) -> list[dict]:
    """分页拉取指定分支的全部提交（按 author.date 降序返回）。"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_commits: list[dict] = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        resp = requests.get(
            url,
            headers=headers,
            params={"sha": branch, "per_page": 100, "page": page},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        all_commits.extend(data)
        page += 1
    return all_commits


def parse_date(commit: dict) -> datetime:
    """解析 commit.author.date 为带时区的 datetime（UTC）。"""
    return datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", "+00:00"))


def get_author(commit: dict) -> str:
    """优先返回 GitHub login；若不可用则回退到 commit author name。"""
    author_obj = commit.get("author")
    if author_obj and author_obj.get("login") and "[bot]" not in author_obj["login"]:
        return author_obj["login"]
    return commit["commit"]["author"]["name"]


def is_bot(commit: dict) -> bool:
    """判断是否为 bot 提交（dependabot、github-actions 等）。"""
    name = commit["commit"]["author"]["name"].lower()
    login = (commit.get("author") or {}).get("login", "").lower()
    return any(kw in name or kw in login for kw in ("[bot]", "dependabot", "github-actions"))


def is_merge(commit: dict) -> bool:
    """判断是否为 merge commit。"""
    msg = commit["commit"]["message"]
    return msg.startswith("Merge pull request") or msg.startswith("Merge branch")


def build_weeks(base_date: datetime, n_weeks: int) -> list[tuple[datetime, datetime]]:
    """构建滚动周区间，返回 [(week_start, week_end), ...] 从最旧到最新排列。"""
    weeks: list[tuple[datetime, datetime]] = []
    end = base_date.replace(hour=23, minute=59, second=59, microsecond=0)
    for _ in range(n_weeks):
        start = (end - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        weeks.append((start, end))
        end = start - timedelta(seconds=1)
    return list(reversed(weeks))


def analyze(commits: list[dict], weeks: list[tuple[datetime, datetime]], top_n: int = 10) -> None:
    """输出 Markdown 格式的周统计表格。"""
    print(
        "\n| 周次 | 区间 | 总提交数 | Bot 提交 | 人工提交 | 作者数 | "
        f"Top {top_n} 作者（作者:提交数） |"
    )
    print("|------|------|:--------:|:--------:|:--------:|:------:|---|")

    for i, (wstart, wend) in enumerate(weeks, 1):
        wc = [c for c in commits if wstart <= parse_date(c) <= wend]
        n_bot = sum(1 for c in wc if is_bot(c))
        author_counts: dict[str, int] = defaultdict(int)
        for c in wc:
            if not is_bot(c):
                author_counts[get_author(c)] += 1
        top = sorted(author_counts.items(), key=lambda x: -x[1])[:top_n]
        top_str = ", ".join(f"`{a}`:{n}" for a, n in top) if top else "—"
        label = f"{wstart.strftime('%Y-%m-%d')}..{wend.strftime('%Y-%m-%d')}"
        human = len(wc) - n_bot
        print(
            f"| W{i} | {label} | {len(wc)} | {n_bot} | {human} | "
            f"{len(author_counts)} | {top_str} |"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="ZeroClaw 周提交统计")
    parser.add_argument("--owner", required=True, help="仓库所有者（用户名/组织名）")
    parser.add_argument("--repo", required=True, help="仓库名称")
    parser.add_argument("--branch", default="master", help="分支名（默认：master）")
    parser.add_argument(
        "--base-date",
        default=None,
        help="统计基准日期 YYYY-MM-DD（默认：今天 UTC）",
    )
    parser.add_argument("--weeks", type=int, default=4, help="统计周数（默认：4）")
    parser.add_argument("--top", type=int, default=10, help="Top N 作者（默认：10）")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if args.base_date:
        base = datetime.strptime(args.base_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    else:
        base = datetime.now(tz=timezone.utc)

    weeks = build_weeks(base, args.weeks)

    print(f"# ZeroClaw 提交周报")
    print(f"仓库: {args.owner}/{args.repo}  分支: {args.branch}")
    print(f"基准日期: {base.strftime('%Y-%m-%d')}  统计周数: {args.weeks}")
    print(f"\n正在拉取提交历史（可能需要数分钟）…")

    commits = fetch_commits(args.owner, args.repo, args.branch, token)
    print(f"共拉取 {len(commits)} 条提交。\n")
    analyze(commits, weeks, top_n=args.top)


if __name__ == "__main__":
    main()
