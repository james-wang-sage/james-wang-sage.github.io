---
layout: post
title: "Why I Removed RTK from Claude Code: Reading JetBrains' Paired Benchmark"
date: 2026-11-06
tags: [ai, claude-code, coding-agents, tokens, benchmarks]
description: "RTK advertised 60–90% fewer tokens; a paired benchmark measured a 7.6% cost increase at low effort and no change at high effort. A commentary on why the saving had nowhere to live, checked against my own Claude Code sessions."
image: /assets/images/2026-11-06-why-i-removed-rtk-from-claude-code-cover.jpg
---

![A thin stream of terminal output passing through a small compressor beside a much larger reservoir of cached context](/assets/images/2026-11-06-why-i-removed-rtk-from-claude-code-cover.jpg)

Until July 2026 I ran [RTK](https://github.com/rtk-ai/rtk) v0.39.0 ("Rust Token Killer") in Claude Code. It is a CLI proxy: a `PreToolUse` hook rewrites shell commands such as `git status` into `rtk git status`, RTK runs the real command, and the model receives a compressed version of the output. The pitch was 60–90% fewer tokens.

On July 20, 2026, JetBrains published [a paired A/B benchmark of RTK](https://blog.jetbrains.com/ai/2026/07/rtk-claude-code-token-savings/). On July 22 I removed it: the hook, the instruction file it adds, and the binary. This post explains why I think the benchmark is right, where it is limited, and what my own session data says.

**Scope.** This is a commentary, not a new benchmark. The JetBrains numbers are theirs. My own numbers come from 247 Claude Code session transcripts on my machine (September–November 2026), recorded *after* RTK was gone, so they estimate what RTK could touch if I reinstalled it today. They are not a before/after comparison.

## 1. What JetBrains measured

The article is part 2 of a series that runs the same paired benchmark against public "token saving" add-ons for coding agents. Part 1 tested the caveman skill (advertised −65%, measured −8.5%).

| | |
|---|---|
| Agent | Claude Code 2.1.201, headless, pinned in both arms |
| Model | `claude-sonnet-5`, full run at low and at high reasoning effort |
| Benchmark | SkillsBench, 86 of 87 tasks, auto-graded with partial credit |
| Treatment | RTK v0.43.0 exactly as `rtk init -g` ships it: binary, `PreToolUse` hook, `RTK.md` |
| Volume | 425 billed trials, about USD 320 |

The results:

| | Low effort | High effort |
|---|---|---|
| Median per-task cost change with RTK | **+7.6%** (p=0.004) | **+0.1%** (p=0.99) |
| Turns | +13.8% (p=0.03) | +0.0 (p=0.74) |
| Task quality (better / worse / tie) | 5 / 4 / 71 | 5 / 4 / 62 |

So RTK did not hurt quality, and at no effort level did it save money. At low effort it cost slightly more: more turns, more cache reads. Pairs where the hook rewrote many commands cost about 24% more than baseline; pairs it barely touched cost about 5% more.

What I value in the method is that it measured the **bill**, paired by task, with the endpoints fixed before any paid run. It also kept RTK's own audit log for every trial, so "RTK saved nothing" can be told apart from "RTK never ran."

## 2. Why the advertised saving had nowhere to live

The compression itself is real. `git status` turned into three lines and `pytest` reduced to its failures look great in a demo. The article's point is that the demo measures the wrong thing. Three mechanisms do most of the work.

**The hook sees only a fraction of the context.** Claude Code reads files with its built-in `Read` tool and searches with `Grep`. Neither goes through the Bash hook; RTK's own README says so: "The hook only fires on Bash tool calls. Built-in tools like `Read`, `Grep` and `Glob` do not pass through it." Of the Bash calls left, JetBrains found that many are `python3 …` and other commands RTK has no filter for, or heredocs and substitutions that RTK deliberately does not rewrite. In JetBrains' replay of 83 baseline transcripts, the commands RTK could rewrite carried just under 20% of tool-result characters. Compress all of that by 70%, and the ceiling is about **3% of input tokens**.

**Claude Code already truncates the pathological cases.** RTK's scoreboard (`rtk gain`) counts the full raw output as what it saved. One `cat` of a 1.2 MB CSV logged 320k tokens "saved", but Claude Code truncates a tool result long before that size, so the model would have received a few thousand tokens either way.

**Most of the input bill is cached re-reads.** Every turn re-reads the whole context from the prompt cache, billed at a tenth of the normal input price. RTK estimates tokens as characters ÷ 4 at the moment the command runs, which says nothing about how that output is billed afterwards.

Put together, RTK's scoreboard reported 96.2 million tokens saved during the low-effort run, while the measured bill for the same trials went up.

## 3. Checking it against my own sessions

My workflow is more shell-heavy than a benchmark agent's. I tell the agent to filter output at the source (`grep`, `head`, `jq`) and to keep `Read` for files it is about to edit. So I checked whether RTK's ceiling is higher for me. I replayed the transcripts and attributed every tool result to the tool that produced it:

| Share of all tool-result characters | My sessions |
|---|---|
| Bash, any command | 66.2% |
| Bash, without a heredoc, command substitution or file redirect | 42.3% |
| Bash, and the command contains one RTK has a filter for | **33.8%** (upper bound) |

That last line is generous. It counts the whole output of `grep … | head -20` as compressible, although `head` already cut it. Even so, RTK could reach about a third of my tool output, against just under a fifth in the benchmark.

Then the dilution starts. In the same transcripts, tool results were roughly **10%** of the tokens written into the prompt cache. Cache reads were **98%** of all input tokens. A third of a tenth is about 3% of what enters the context. Compressing it by 70% gives roughly **2–3%**. My workload is more exposed to RTK than SkillsBench, and the ceiling still lands where JetBrains put it.

Two caveats. Tokens here are characters ÷ 4, like RTK's own estimate. The replay covers main sessions only, not subagent transcripts.

## 4. Where the article stops

- **One model, one benchmark.** `claude-sonnet-5` on SkillsBench. The full 86-task runs were one attempt per task (k=1) at each effort level.
- **One RTK version.** The benchmark tested v0.43.0 (June 28, 2026) in hook mode. RTK v1.0.0 (October 13, 2026) added pipelines and an `rtk-proxy` daemon that works on the provider-API traffic itself; v1.1.0 (October 25) is the current release. Neither benchmark nor I tested that, and I would not extrapolate in either direction.
- **The README is more careful now.** On July 22, 2026, two days after the article, RTK added a "How Savings Work" section that scopes its numbers to bash output: "it is not the same as cutting your bill by the same amount." The header still promises compression "up to 90% smaller", now explicitly about bash output.

None of these change my decision. The structural argument, a filter on a fifth to a third of tool output inside a bill dominated by cached re-reads, does not depend on the model or the version.

## 5. What I use instead

I kept one layer: the [context-mode](https://github.com/mksglu/context-mode) plugin. Instead of compressing output after the fact, it runs a command or script in a sandbox and returns only what the script prints. A 2,000-line test log becomes "3 failed: …" because the script asked that question, not because a filter guessed what mattered.

I have not run a paired benchmark on it either. The lesson from this article applies to it as much as to RTK, and that is the main thing I took away:

> A tool's self-reported savings are a claim about its counterfactual, not about your bill.

If you are evaluating any context-compression tool for a coding agent, run the same tasks with and without it, pair them, and compare the invoices. Its own dashboard cannot tell you that.
