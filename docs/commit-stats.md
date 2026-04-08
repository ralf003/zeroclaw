# Commit Statistics Tool

`scripts/commit_stats.py` is a zero-dependency Python script that computes
rolling 28-day commit statistics for any GitHub repository branch and prints
a Markdown table to stdout.

## Output

The script prints a table with four rows (one per 7-day window) and four
columns:

| Week Range | Commits | Authors | Top10 (author:count) |
|---|---|---|---|
| 2026-03-12..2026-03-18 | 42 | 7 | alice:12, bob:9, … |
| 2026-03-19..2026-03-25 | 38 | 5 | alice:15, charlie:8, … |
| 2026-03-26..2026-04-01 | 51 | 9 | bob:11, … |
| 2026-04-02..2026-04-08 | 29 | 6 | alice:10, … |

- **Week Range** — `YYYY-MM-DD..YYYY-MM-DD` for the 7-day window (week 1 =
  most recent 0–6 days ago, week 4 = 21–27 days ago).
- **Commits** — total commits in that window.
- **Authors** — unique author count for that window.
- **Top10** — up to 10 authors ordered by commit count (`author:count` pairs,
  comma-separated). Author identity prefers the GitHub login; falls back to
  the commit `author.name` / `author.email` field when a login is absent.

## Requirements

- Python 3.8+
- No third-party packages required (uses only the standard library).
- For the GitHub API mode, a
  [GitHub personal-access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens)
  is recommended to avoid the 60 req/h unauthenticated rate limit.

## Usage

### GitHub API mode (recommended)

```sh
# Using a token passed explicitly
python scripts/commit_stats.py --repo ralf003/zeroclaw --token ghp_…

# Using the GITHUB_TOKEN environment variable (e.g. inside CI)
export GITHUB_TOKEN=ghp_…
python scripts/commit_stats.py --repo ralf003/zeroclaw

# Analyse a different branch
python scripts/commit_stats.py --repo ralf003/zeroclaw --ref develop
```

### Local git log mode

Run from inside the repository (or pass `--ref` to specify a branch):

```sh
python scripts/commit_stats.py --local
python scripts/commit_stats.py --local --ref main
```

### Options

| Flag | Default | Description |
|---|---|---|
| `--repo OWNER/REPO` | — | GitHub repository slug |
| `--local` | — | Use local `git log` instead of GitHub API |
| `--token TOKEN` | `$GITHUB_TOKEN` | GitHub personal-access token |
| `--ref REF` | `master` | Branch / tag / SHA to analyse |
| `--days N` | `28` | Total window in days (must be a multiple of 7) |
| `--top N` | `10` | Number of top authors to display |

## Running the tests

```sh
python -m pytest scripts/tests/test_commit_stats.py -v
```

The tests use fixed sample data and do not make network calls.

## Notes

- The script handles GitHub API pagination automatically; repositories with
  thousands of commits over 28 days are covered correctly.
- When running without a token against a public repository, the GitHub API
  allows 60 unauthenticated requests per hour. A single 28-day window
  typically requires 1–5 pages (100 commits per page), well within that
  limit.
- The `--local` mode does not require network access and works offline.
