"""
Tests for scripts/commit_stats.py

Run from the repository root:
    python -m pytest scripts/tests/test_commit_stats.py -v
"""

from __future__ import annotations

import sys
import os
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Make the scripts directory importable without installation.
sys.path.insert(0, str(Path(__file__).parent.parent))

import commit_stats as cs


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _utc_date(year: int, month: int, day: int) -> datetime:
    return datetime(year, month, day, tzinfo=timezone.utc)


# ---------------------------------------------------------------------------
# build_windows
# ---------------------------------------------------------------------------

class TestBuildWindows:
    def test_four_windows_returned(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref, total_days=28, window_size=7)
        assert len(wins) == 4

    def test_most_recent_window_ends_today(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        _, end = wins[0]
        assert end.date() == ref.date()

    def test_most_recent_window_starts_six_days_ago(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        start, _ = wins[0]
        assert start.date() == (ref - timedelta(days=6)).date()

    def test_windows_are_contiguous(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        for i in range(len(wins) - 1):
            start_curr, end_curr = wins[i]
            start_next, end_next = wins[i + 1]
            # Each window covers exactly 7 days: end - start = 6 days.
            assert (end_curr - start_curr).days == 6
            # Adjacent windows are non-overlapping and gap-free:
            # start_curr = end_next + 1 day.
            assert (start_curr - end_next).days == 1

    def test_invalid_total_days_raises(self):
        import pytest
        with pytest.raises(ValueError):
            cs.build_windows(total_days=10, window_size=7)

    def test_custom_window_size(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref, total_days=14, window_size=7)
        assert len(wins) == 2


# ---------------------------------------------------------------------------
# compute_stats
# ---------------------------------------------------------------------------

class TestComputeStats:
    def _make_commits(self) -> list:
        # Week 1 (0-6 days ago from 2026-04-08): 2026-04-03 to 2026-04-08
        # Week 2 (7-13 days ago):                 2026-03-27 to 2026-04-02
        return [
            {"date": _utc_date(2026, 4, 8), "author": "alice"},
            {"date": _utc_date(2026, 4, 7), "author": "alice"},
            {"date": _utc_date(2026, 4, 6), "author": "bob"},
            {"date": _utc_date(2026, 4, 1), "author": "charlie"},  # week 2
            {"date": _utc_date(2026, 3, 28), "author": "charlie"},  # week 2
        ]

    def test_commit_counts_per_window(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        stats = cs.compute_stats(self._make_commits(), wins)
        # Week 1: 3 commits, Week 2: 2 commits, Weeks 3-4: 0
        assert stats[0]["commits"] == 3
        assert stats[1]["commits"] == 2
        assert stats[2]["commits"] == 0
        assert stats[3]["commits"] == 0

    def test_author_counts_per_window(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        stats = cs.compute_stats(self._make_commits(), wins)
        assert stats[0]["authors"] == 2   # alice, bob
        assert stats[1]["authors"] == 1   # charlie

    def test_top10_ordering(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        stats = cs.compute_stats(self._make_commits(), wins)
        # alice has 2 commits, bob has 1 in week 1 — alice should be first
        top = stats[0]["top10"]
        assert top[0][0] == "alice"
        assert top[0][1] == 2
        assert top[1][0] == "bob"
        assert top[1][1] == 1

    def test_top_n_respected(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        commits = [{"date": _utc_date(2026, 4, 8), "author": f"user{i}"} for i in range(20)]
        stats = cs.compute_stats(commits, wins, top_n=5)
        assert len(stats[0]["top10"]) == 5

    def test_empty_commits(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        stats = cs.compute_stats([], wins)
        for row in stats:
            assert row["commits"] == 0
            assert row["authors"] == 0
            assert row["top10"] == []


# ---------------------------------------------------------------------------
# render_markdown_table
# ---------------------------------------------------------------------------

class TestRenderMarkdownTable:
    def test_output_contains_header(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        stats = cs.compute_stats([], wins)
        table = cs.render_markdown_table(stats)
        assert "Week Range" in table
        assert "Commits" in table
        assert "Authors" in table
        assert "Top10" in table

    def test_week_range_format(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        stats = cs.compute_stats([], wins)
        table = cs.render_markdown_table(stats)
        # Most recent window: 2026-04-02..2026-04-08
        assert "2026-04-02..2026-04-08" in table

    def test_row_count_matches_windows(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        stats = cs.compute_stats([], wins)
        table = cs.render_markdown_table(stats)
        # header + separator + 4 data rows = 6 lines
        lines = [l for l in table.splitlines() if l.strip()]
        assert len(lines) == 6

    def test_top10_author_count_format(self):
        ref = _utc_date(2026, 4, 8)
        wins = cs.build_windows(reference=ref)
        commits = [
            {"date": _utc_date(2026, 4, 8), "author": "alice"},
            {"date": _utc_date(2026, 4, 8), "author": "alice"},
            {"date": _utc_date(2026, 4, 7), "author": "bob"},
        ]
        stats = cs.compute_stats(commits, wins)
        table = cs.render_markdown_table(stats)
        assert "alice:2" in table
        assert "bob:1" in table


# ---------------------------------------------------------------------------
# parse_args
# ---------------------------------------------------------------------------

class TestParseArgs:
    def test_repo_flag(self):
        args = cs.parse_args(["--repo", "ralf003/zeroclaw"])
        assert args.repo == "ralf003/zeroclaw"

    def test_local_flag(self):
        args = cs.parse_args(["--local"])
        assert args.local is True

    def test_default_ref(self):
        args = cs.parse_args(["--local"])
        assert args.ref == "master"

    def test_custom_ref(self):
        args = cs.parse_args(["--local", "--ref", "main"])
        assert args.ref == "main"

    def test_default_days(self):
        args = cs.parse_args(["--local"])
        assert args.days == 28

    def test_custom_days(self):
        args = cs.parse_args(["--local", "--days", "14"])
        assert args.days == 14
