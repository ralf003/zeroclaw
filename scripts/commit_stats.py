#!/usr/bin/env python3
"""
commit_stats.py — Rolling 28-day commit statistics for a GitHub repository.

Fetches commits from the target branch over the past 28 days (inclusive of
today) and divides them into four consecutive 7-day windows:

  Week 1 : 0–6 days ago   (most recent)
  Week 2 : 7–13 days ago
  Week 3 : 14–20 days ago
  Week 4 : 21–27 days ago

Outputs a Markdown table with columns:
  Week Range (YYYY-MM-DD..YYYY-MM-DD) | Commits | Authors | Top10 (author:count, …)

Data source preference:
  1. GitHub REST API (requires --repo and optionally --token / GITHUB_TOKEN env var)
  2. Local ``git log`` when running inside the target repository (--local flag)

Usage:
  python scripts/commit_stats.py --repo owner/repo [--token ghp_...] [--ref master]
  python scripts/commit_stats.py --local [--ref master]

Options:
  --repo  OWNER/REPO   GitHub repository slug (e.g. ralf003/zeroclaw)
  --token TOKEN        GitHub personal-access token (falls back to GITHUB_TOKEN env var)
  --ref   REF          Branch / tag / SHA to analyse  (default: master)
  --local              Use local ``git log`` instead of GitHub API
  --days  N            Total window in days (default: 28, must be a multiple of 7)
  --help               Print this message and exit
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import urllib.request
import urllib.error
import json
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional, Tuple


# ---------------------------------------------------------------------------
# Types
# ---------------------------------------------------------------------------

CommitRecord = Dict[str, Any]
"""Minimal commit info: {"date": datetime, "author": str}"""


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def _utcnow() -> datetime:
    return datetime.now(tz=timezone.utc)


def build_windows(
    reference: Optional[datetime] = None,
    total_days: int = 28,
    window_size: int = 7,
) -> List[Tuple[datetime, datetime]]:
    """Return a list of (start, end) datetime pairs (UTC, inclusive on both ends).

    Week 1 is the most recent window ending at *reference* (today).
    """
    if total_days % window_size != 0:
        raise ValueError(
            f"total_days ({total_days}) must be a multiple of window_size ({window_size})"
        )
    base = (reference or _utcnow()).replace(hour=0, minute=0, second=0, microsecond=0)
    windows: List[Tuple[datetime, datetime]] = []
    for i in range(total_days // window_size):
        end = base - timedelta(days=i * window_size)
        start = end - timedelta(days=window_size - 1)
        windows.append((start, end))
    return windows


# Max characters of an error-response body included in exception messages.
_ERROR_BODY_MAX = 400

# End-of-day time components used to make the upper bound of each date window
# inclusive (23:59:59.999999 on the window's last calendar day).
_EOD_HOUR = 23
_EOD_MINUTE = 59
_EOD_SECOND = 59
_EOD_MICROSECOND = 999999


# ---------------------------------------------------------------------------
# GitHub API source
# ---------------------------------------------------------------------------

def _github_api_get(url: str, token: Optional[str]) -> Any:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("X-GitHub-Api-Version", "2022-11-28")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        body = exc.read().decode(errors="replace")
        raise RuntimeError(
            f"GitHub API error {exc.code} for {url}: {body[:_ERROR_BODY_MAX]}"
        ) from exc


def _next_link(link_header: str) -> Optional[str]:
    """Parse GitHub ``Link:`` response header and return the next-page URL."""
    if not link_header:
        return None
    for part in link_header.split(","):
        url_part, *rels = part.strip().split(";")
        for rel in rels:
            if 'rel="next"' in rel:
                return url_part.strip().strip("<>")
    return None


def fetch_commits_github(
    repo: str,
    ref: str,
    since: datetime,
    token: Optional[str] = None,
) -> List[CommitRecord]:
    """Fetch all commits on *ref* since *since* via GitHub REST API (handles paging)."""
    since_iso = since.strftime("%Y-%m-%dT%H:%M:%SZ")
    base_url = (
        f"https://api.github.com/repos/{repo}/commits"
        f"?sha={ref}&per_page=100&since={since_iso}"
    )
    records: List[CommitRecord] = []
    url: Optional[str] = base_url

    while url:
        req = urllib.request.Request(url)
        req.add_header("Accept", "application/vnd.github+json")
        req.add_header("X-GitHub-Api-Version", "2022-11-28")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode())
                link_header = resp.headers.get("Link", "")
        except urllib.error.HTTPError as exc:
            body = exc.read().decode(errors="replace")
            raise RuntimeError(
                f"GitHub API error {exc.code} fetching commits: {body[:_ERROR_BODY_MAX]}"
            ) from exc

        for item in data:
            date_str = (
                (item.get("commit") or {})
                .get("author", {})
                .get("date", "")
            )
            if not date_str:
                continue
            try:
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                continue

            # Prefer GitHub login; fall back to commit author name / email.
            login = (item.get("author") or {}).get("login", "")
            if not login:
                commit_author = (item.get("commit") or {}).get("author", {})
                login = commit_author.get("name") or commit_author.get("email") or "unknown"

            records.append({"date": dt, "author": login})

        url = _next_link(link_header)

    return records


# ---------------------------------------------------------------------------
# Local git log source
# ---------------------------------------------------------------------------

def fetch_commits_local(
    ref: str,
    since: datetime,
    repo_dir: str = ".",
) -> List[CommitRecord]:
    """Fetch commits from local ``git log``."""
    since_str = since.strftime("%Y-%m-%d %H:%M:%S")
    cmd = [
        "git",
        "-C", repo_dir,
        "log", ref,
        f"--since={since_str}",
        "--format=%aI\t%ae\t%an",
    ]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True
        )
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"git log failed: {exc.stderr.strip()}") from exc

    records: List[CommitRecord] = []
    for line in result.stdout.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 3:
            continue
        date_str, email, name = parts
        try:
            dt = datetime.fromisoformat(date_str)
        except ValueError:
            continue
        author = name or email or "unknown"
        records.append({"date": dt, "author": author})
    return records


# ---------------------------------------------------------------------------
# Statistics
# ---------------------------------------------------------------------------

def compute_stats(
    commits: List[CommitRecord],
    windows: List[Tuple[datetime, datetime]],
    top_n: int = 10,
) -> List[Dict[str, Any]]:
    """Bucket commits into windows and compute per-window statistics."""
    results = []
    for start, end in windows:
        window_end = end.replace(
            hour=_EOD_HOUR,
            minute=_EOD_MINUTE,
            second=_EOD_SECOND,
            microsecond=_EOD_MICROSECOND,
        )
        window_commits = [
            c for c in commits if start <= c["date"] <= window_end
        ]
        author_counts: Counter = Counter(c["author"] for c in window_commits)
        top10 = author_counts.most_common(top_n)
        results.append(
            {
                "start": start,
                "end": end,
                "commits": len(window_commits),
                "authors": len(author_counts),
                "top10": top10,
            }
        )
    return results


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def render_markdown_table(stats: List[Dict[str, Any]]) -> str:
    """Render a Markdown table from computed statistics."""
    header = "| Week Range | Commits | Authors | Top10 (author:count) |"
    separator = "|---|---|---|---|"
    rows = [header, separator]
    for row in stats:
        week_range = f"{row['start'].strftime('%Y-%m-%d')}..{row['end'].strftime('%Y-%m-%d')}"
        top10_str = ", ".join(f"{a}:{c}" for a, c in row["top10"]) or "—"
        rows.append(
            f"| {week_range} | {row['commits']} | {row['authors']} | {top10_str} |"
        )
    return "\n".join(rows)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="commit_stats.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--repo", metavar="OWNER/REPO", help="GitHub repository slug")
    source.add_argument(
        "--local",
        action="store_true",
        help="Use local git log instead of GitHub API",
    )
    parser.add_argument(
        "--token",
        metavar="TOKEN",
        default=os.environ.get("GITHUB_TOKEN", ""),
        help="GitHub personal-access token (default: $GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--ref",
        default="master",
        help="Branch / tag / SHA to analyse (default: master)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=28,
        help="Total window in days, must be a multiple of 7 (default: 28)",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=10,
        help="Number of top authors to show (default: 10)",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> None:
    args = parse_args(argv)

    if args.days <= 0 or args.days % 7 != 0:
        print(
            f"Error: --days must be a positive multiple of 7, got {args.days}",
            file=sys.stderr,
        )
        sys.exit(1)

    now = _utcnow()
    windows = build_windows(reference=now, total_days=args.days)
    since = windows[-1][0]  # earliest start across all windows

    if args.local:
        commits = fetch_commits_local(ref=args.ref, since=since)
    elif args.repo:
        commits = fetch_commits_github(
            repo=args.repo,
            ref=args.ref,
            since=since,
            token=args.token or None,
        )
    else:
        print(
            "Error: specify either --repo OWNER/REPO or --local",
            file=sys.stderr,
        )
        sys.exit(1)

    stats = compute_stats(commits, windows, top_n=args.top)
    print(render_markdown_table(stats))

    # Sanity check: total commits in table equals total fetched
    total_in_table = sum(s["commits"] for s in stats)
    total_fetched = len(commits)
    if total_in_table != total_fetched:
        print(
            f"\n[warn] Sanity check: {total_in_table} commits in table "
            f"vs {total_fetched} fetched (some may fall outside the windows)",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
