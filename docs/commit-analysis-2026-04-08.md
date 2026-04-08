# ZeroClaw master 分支近 4 周 Commit 提交分析报告

> **报告基准日期**：2026-04-08
> **数据来源**：GitHub REST API (`GET /repos/ralf003/zeroclaw/commits`)，共收集 `master` 分支全部历史提交（约 1,400 条，分 15 页拉取）。

---

## 1. 统计方法说明

### 1.1 周区间划分

以**报告基准日期（2026-04-08）**为终点，向前滚动 28 天（4 × 7 天），形成 4 个统计周：

| 周次 | 区间（UTC，含首尾） |
|------|----------------------|
| 第 4 周（最近） | 2026-04-02..2026-04-08 |
| 第 3 周 | 2026-03-26..2026-04-01 |
| 第 2 周 | 2026-03-19..2026-03-25 |
| 第 1 周（最早） | 2026-03-12..2026-03-18 |

> ⚠️ **数据说明**：经 API 完整拉取，该仓库 `master` 分支最后一次提交时间为 **2026-03-08 03:33 UTC**（PR #2954，`fix: resolve unused import warnings`）。上述严格基准窗口（2026-03-12..2026-04-08）内**实际存在 0 条提交**，即仓库在报告日期前约 31 天已停止接收新提交。
>
> 因此，本报告**同时提供基于实际活跃周期的分析表格**——以最后提交日期（2026-03-08）为终点向前滚动 28 天（2026-02-09..2026-03-08），以保证分析结果具有实质意义。两套数据均已注明，便于读者对照。

### 1.2 数据收集方式

- **工具**：GitHub REST API `GET /repos/ralf003/zeroclaw/commits?sha=master&per_page=100`，分页遍历，去重（按 SHA）后合并，共采集 **1,400 条唯一提交**。
- **时间字段**：使用 `commit.author.date`（提交者本地创作时间）而非 `commit.committer.date`，更准确反映代码贡献时间点。
- **时区统一**：所有时间转换为 UTC 再进行区间归档。

### 1.3 排除规则

| 类型 | 识别标准 | 处理方式 |
|------|----------|----------|
| **Merge commit** | 消息以 `"Merge pull request"` 或 `"Merge branch"` 开头 | 计入总数，但在 Top 10 作者统计中可单独标注 |
| **Bot 提交** | 作者名或 GitHub login 包含 `[bot]`、`dependabot`、`github-actions` | 计入总数时单独列出，Top 10 中剔除 |

### 1.4 作者身份判定

优先使用 **GitHub 登录名（`author.login`）**作为作者标识（唯一且稳定）；若 API 返回的 `author` 字段为 `null`（外部贡献者未关联账户），则回退为 `commit.author.name`。

> **注意**：`chumyin`（GitHub login）与 `Chummy`（部分早期提交中的 `author.name`）为同一账号，已统一归并到 `chumyin`。

---

## 2. 提交统计表格

### 2A. 基于报告基准日期的严格窗口（2026-03-12..2026-04-08）

| 周次 | 区间 | 总提交数 | 有提交的作者数 | Top 10 作者（作者名：提交数） |
|------|------|:--------:|:------------:|-------------------------------|
| 第 4 周 | 2026-04-02..2026-04-08 | 0 | 0 | — |
| 第 3 周 | 2026-03-26..2026-04-01 | 0 | 0 | — |
| 第 2 周 | 2026-03-19..2026-03-25 | 0 | 0 | — |
| 第 1 周 | 2026-03-12..2026-03-18 | 0 | 0 | — |
| **合计** | 2026-03-12..2026-04-08 | **0** | **0** | — |

> 该窗口内无任何提交。仓库最近一次 commit 发生于 2026-03-08（窗口开始前 4 天）。

---

### 2B. 基于实际活跃周期的滚动窗口（2026-02-09..2026-03-08）

> 以仓库最后一次提交日期（2026-03-08）为终点，向前滚动 28 天。下表展示真实提交数据。

#### 汇总概览

| 周次 | 区间 | 总提交数 | Bot 提交数 | 人工提交数 | 有提交的作者数 |
|------|------|:--------:|:----------:|:----------:|:-------------:|
| 第 1 周 | 2026-02-09..2026-02-15 | 192 | 0 | 192 | 17 |
| 第 2 周 | 2026-02-16..2026-02-22 | 1,127 | 31 | 1,096 | 109 |
| 第 3 周 | 2026-02-23..2026-03-01 | 56 | 0 | 56 | 16 |
| 第 4 周 | 2026-03-02..2026-03-08 | 25 | 0 | 25 | 4 |
| **合计** | 2026-02-09..2026-03-08 | **1,400** | **31** | **1,369** | **~136** |

#### 第 1 周：2026-02-09..2026-02-15

| 排名 | 作者（GitHub 登录名） | 当周提交数 |
|------|----------------------|:---------:|
| 1 | theonlyhennygod | 119 |
| 2 | fettpl | 36 |
| 3 | ecschoye | 9 |
| 4 | Chummy (→ chumyin) | 6 |
| 5 | vrescobar | 5 |
| 6 | Codex | 3 |
| 7 | willsarg | 2 |
| 8 | kumanday | 2 |
| 9 | jbradf0rd | 2 |
| 10 | Abhishek | 1 |

> 该周从 2026-02-13 才有首次提交（初始版本发布 `feat: initial release — ZeroClaw v0.1.0`）。

#### 第 2 周：2026-02-16..2026-02-22

| 排名 | 作者（GitHub 登录名） | 当周提交数 |
|------|----------------------|:---------:|
| 1 | chumyin | 430 |
| 2 | willsarg | 119 |
| 3 | agorevski | 112 |
| 4 | theonlyhennygod | 56 |
| 5 | fettpl | 39 |
| 6 | ecschoye | 29 |
| 7 | zverozabr | 21 |
| 8 | vernonstinebaker | 19 |
| 9 | reidliu41 | 18 |
| 10 | v0l | 14 |

> 该周为活跃度峰值，共 1,127 次提交（含 31 次 bot 提交），109 位作者参与贡献。

#### 第 3 周：2026-02-23..2026-03-01

| 排名 | 作者（GitHub 登录名） | 当周提交数 |
|------|----------------------|:---------:|
| 1 | chumyin | 35 |
| 2 | theonlyhennygod | 4 |
| 3 | Preventnetworkhacking | 2 |
| 4 | Mike Johnson-Maxted | 2 |
| 5 | reidliu41 | 2 |
| 6 | Allen Huang | 1 |
| 7 | NorbertBodziony | 1 |
| 8 | adam-singer | 1 |
| 9 | bzivic | 1 |
| 10 | madamak | 1 |

#### 第 4 周：2026-03-02..2026-03-08

| 排名 | 作者（GitHub 登录名） | 当周提交数 |
|------|----------------------|:---------:|
| 1 | JordanTheJet | 21 |
| 2 | SimianAstronaut7 | 2 |
| 3 | theonlyhennygod | 1 |
| 4 | antonvice | 1 |

---

## 3. 简要分析总结

### 3.1 活跃度趋势

```
提交数
1127 |██████████████████████████████████████████
     |
 192 |████████
     |
  56 |███
  25 |█
     |—————————————————————————————————————————→ 周次
       W1(02/09) W2(02/16) W3(02/23) W4(03/02)
```

活跃度呈**极端倒 V 形**：仓库于 2026-02-13 初始发布，W2（2026-02-16..2026-02-22）仅用一周即爆发至 **1,127 次提交、109 位作者**，随后急剧回落——W3 降至 56 次（降幅 95%），W4 仅余 25 次。2026-03-08 后仓库不再有新提交（截至报告日 2026-04-08）。

### 3.2 Top 作者贡献特征

| 作者 | 总提交数（近 4 活跃周） | 主要活跃周 | 备注 |
|------|:-----------------------:|------------|------|
| **chumyin** | 471 | W2（430）、W3（35） | 核心维护者，峰值单周 430 次 |
| **theonlyhennygod** | 180 | W1（119）、W2（56） | 项目创始人（初始版本作者） |
| **willsarg** | 121 | W2（119）主导 | 集中贡献于峰值周 |
| **agorevski** | 112 | W2（112）主导 | 集中贡献于峰值周 |
| **fettpl** | 75 | W1（36）、W2（39） | 横跨前两周的早期贡献者 |
| **JordanTheJet** | 21 | W4（21）主导 | 后期主力，最后一批活跃贡献者 |

### 3.3 主力作者分析

- **明显主力作者存在**：`chumyin` 在 28 天内贡献了 **471 次提交（占比约 33.6%）**，是无可争议的核心维护者，高度集中在 W2 峰值周（430 次，占该周总数的 38.2%）。
- **冲刺型贡献者**：`willsarg`（119 次）、`agorevski`（112 次）在 W2 集中大量贡献后几乎退出，表现出典型的"冲刺合并"模式——可能是集中 PR review/merge 批量落库。
- **长期活跃作者**：`theonlyhennygod` 横跨 W1~W3 持续贡献（共 180 次），`fettpl` 横跨 W1~W2（共 75 次）。
- **后期收缩明显**：W3、W4 的参与作者数从峰值 109 位骤降至 16、4 位，表明该仓库在快速开发冲刺后进入低活跃维护期或已结束主动开发。

### 3.4 补充说明

- **Merge commit 占比**：W2 包含约 101 次人工 merge commit，实际代码变更提交数约为 995 次。
- **Bot 提交**：W2 出现 31 次 `dependabot[bot]` 自动提交（依赖升级），其余三周无 bot 提交。
- **报告窗口差异说明**：基于当前日期的严格窗口（2026-03-12..2026-04-08）无数据，本报告以最后提交日（2026-03-08）为基准补充实际活跃数据分析，两套结果均已在 §2 中呈现。

---

## 4. 附录：辅助分析脚本

以下 Python 脚本可本地复现上述统计，仅需 GitHub Token 即可运行。

### 用法示例

```bash
# 安装依赖
pip install requests

# 设置 GitHub Token（可选，提升速率上限）
export GITHUB_TOKEN="your_token_here"

# 运行统计
python3 scripts/commit_weekly_stats.py \
  --owner ralf003 \
  --repo zeroclaw \
  --branch master \
  --base-date 2026-04-08 \
  --weeks 4
```

### 脚本核心逻辑（`scripts/commit_weekly_stats.py`）

```python
#!/usr/bin/env python3
"""
ZeroClaw 周提交统计脚本
用法: python3 commit_weekly_stats.py --owner OWNER --repo REPO [--base-date YYYY-MM-DD] [--weeks N]
"""

import argparse
import os
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

import requests


def fetch_commits(owner: str, repo: str, branch: str, token: str | None = None) -> list[dict]:
    """分页拉取全部提交，按 author.date 降序返回。"""
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    all_commits: list[dict] = []
    page = 1
    while True:
        url = f"https://api.github.com/repos/{owner}/{repo}/commits"
        resp = requests.get(url, headers=headers, params={"sha": branch, "per_page": 100, "page": page}, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        if not data:
            break
        all_commits.extend(data)
        page += 1
    return all_commits


def parse_date(commit: dict) -> datetime:
    return datetime.fromisoformat(commit["commit"]["author"]["date"].replace("Z", "+00:00"))


def get_author(commit: dict) -> str:
    author_obj = commit.get("author")
    if author_obj and author_obj.get("login") and "[bot]" not in author_obj["login"]:
        return author_obj["login"]
    return commit["commit"]["author"]["name"]


def is_bot(commit: dict) -> bool:
    name = commit["commit"]["author"]["name"].lower()
    login = (commit.get("author") or {}).get("login", "").lower()
    return any(kw in name or kw in login for kw in ("[bot]", "dependabot", "github-actions"))


def build_weeks(base_date: datetime, n_weeks: int) -> list[tuple[datetime, datetime]]:
    """返回 [(week_start, week_end), ...] 从最旧到最新排列。"""
    weeks = []
    end = base_date.replace(hour=23, minute=59, second=59, microsecond=0)
    for _ in range(n_weeks):
        start = end - timedelta(days=6)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        weeks.append((start, end))
        end = start - timedelta(seconds=1)
    return list(reversed(weeks))


def analyze(commits: list[dict], weeks: list[tuple[datetime, datetime]]) -> None:
    print(f"\n{'周次':<6} {'区间':<25} {'总提交':>6} {'Bot':>5} {'作者数':>6}  Top 10 作者")
    print("-" * 100)
    for i, (wstart, wend) in enumerate(weeks, 1):
        wc = [c for c in commits if wstart <= parse_date(c) <= wend]
        n_bot = sum(1 for c in wc if is_bot(c))
        author_counts: dict[str, int] = defaultdict(int)
        for c in wc:
            if not is_bot(c):
                author_counts[get_author(c)] += 1
        top10 = sorted(author_counts.items(), key=lambda x: -x[1])[:10]
        top_str = ", ".join(f"{a}:{n}" for a, n in top10)
        label = f"{wstart.strftime('%Y-%m-%d')}..{wend.strftime('%Y-%m-%d')}"
        print(f"W{i:<5} {label:<25} {len(wc):>6} {n_bot:>5} {len(author_counts):>6}  {top_str}")


def main() -> None:
    parser = argparse.ArgumentParser(description="ZeroClaw 周提交统计")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--branch", default="master")
    parser.add_argument("--base-date", default=datetime.now(tz=timezone.utc).strftime("%Y-%m-%d"))
    parser.add_argument("--weeks", type=int, default=4)
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    base = datetime.strptime(args.base_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    weeks = build_weeks(base, args.weeks)

    print(f"正在拉取 {args.owner}/{args.repo}@{args.branch} 的提交历史…")
    commits = fetch_commits(args.owner, args.repo, args.branch, token)
    print(f"共拉取 {len(commits)} 条提交。")
    analyze(commits, weeks)


if __name__ == "__main__":
    main()
```

> 脚本完整版本位于仓库 `scripts/commit_weekly_stats.py`（如该文件尚未创建，可将上述代码复制保存后直接运行）。

---

*本报告由 GitHub API 数据自动生成，生成时间：2026-04-08T08:10:13Z。*
