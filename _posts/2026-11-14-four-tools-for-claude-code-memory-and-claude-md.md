---
layout: post
title: "Four Tools for Cleaning Up Claude Code's Memory and CLAUDE.md: Which One When"
date: 2026-11-14
tags: [ai, claude-code, coding-agents, memory]
description: "/doctor prompt-audit, improve-claude-md, claude-md-improver and a dream skill all promise tidier instructions, but they read different files and push in different directions. A side-by-side comparison and when to reach for each."
image: /assets/images/2026-11-14-four-tools-for-claude-code-memory-and-claude-md-cover.jpg
---

![A loupe, a pair of shears, a brush and a small press laid out on a dark workbench beside a stack of blank index cards](/assets/images/2026-11-14-four-tools-for-claude-code-memory-and-claude-md-cover.jpg)

My project's auto-memory index, `MEMORY.md`, sits at 125 lines and 18,104 bytes. Claude Code loads only the first 200 lines or 25KB of that file at the start of a session, so I went looking for a tool to compact it. I found four tools that clean up Claude Code's context files. Each reads a different set of files and pushes in a different direction, and only one of them touches `MEMORY.md`.

This post compares them from their source files and the official docs, as of November 14, 2026. The tools:

| Tool | Where it comes from |
|---|---|
| `/doctor prompt-audit` | Built into Claude Code (v2.1.283 or later) |
| `improve-claude-md` | [humanlayer/skills](https://github.com/humanlayer/skills/tree/main/plugins/improve-claude-md), a third-party skill |
| `claude-md-improver` | The `claude-md-management` plugin in Anthropic's [claude-plugins-official](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/claude-md-management) marketplace |
| `dream` | A skill I wrote for myself (private repo) |

## 1. Two kinds of context file

The four tools split along a line that is easy to miss: Claude Code has two different kinds of context file, and they have different limits.

- **Instruction files** are the ones you write: `CLAUDE.md`, `CLAUDE.local.md`, `AGENTS.md`, the rules under `.claude/rules/`, skills, commands, subagents and output styles. According to the [memory docs](https://code.claude.com/docs/en/memory), Claude gets the whole of each `CLAUDE.md` that loads at launch, as long as it is 4 MiB or smaller. That is a loading limit, not a target: the same page recommends keeping each `CLAUDE.md` under 200 lines, because longer files reduce adherence.
- **Auto memory** is what Claude writes for itself: a `MEMORY.md` index plus one topic file per fact. Only the first 200 lines or 25KB of `MEMORY.md` load at session start, whichever comes first. Content beyond that is not loaded at session start.

Claude Code already guards the second limit itself. After Claude writes to `MEMORY.md`, Claude Code measures it. Near a limit, it reminds Claude to keep one line per entry, move detail into topic files, and merge or drop stale entries. Over a limit, the write succeeds but Claude gets an error telling it to rewrite the index. That guard works one write at a time. The docs describe no pass over the whole directory that looks for duplicates or entries that have gone stale.

## 2. What each tool does

### `/doctor prompt-audit`: find what is wrong

The [docs](https://code.claude.com/docs/en/memory#audit-your-instruction-files) describe it as a check for "outdated or conflicting content": instructions written for older models, references to files or commands that don't exist, and files that contradict each other. You get a report with proposed edits, and nothing changes until you ask Claude to apply them.

By default it covers `CLAUDE.md`, `CLAUDE.local.md` and `AGENTS.md`, plus the rules, skills, commands, subagents and output styles under both `.claude/` and `~/.claude/`. You can pass a path to audit one file or directory. It runs through the bundled `/claude-api` skill, so it is unavailable if you have turned that skill off.

Auto-memory directories are not in that default list. A path argument could point it at one, but I have not tested whether it understands the memory file format.

### `improve-claude-md`: restructure one file

This skill rewrites a single `CLAUDE.md`. Its premise is that Claude Code tells the model a `CLAUDE.md` may or may not be relevant to the task, so a long file of flat rules gets partly ignored. Its fix is to leave project identity, the directory map and the tech stack as plain text at the top, and to wrap every task-specific rule in its own block with a narrow condition:

```markdown
<important if="you are writing or modifying tests">
- API: Jest + Supertest
- Use `createTestClient()` for API integration tests
</important>
```

While restructuring, it deletes rules a linter or formatter can enforce, code snippets (replaced with file path references) and vague advice such as "follow best practices". It keeps every command from the original. It does not check whether anything in the file is still true.

### `claude-md-improver`: score and fill gaps

This skill finds the `CLAUDE.md` files in a repository and scores each one from 0 to 100, graded A to F. It uses six criteria: commands, architecture clarity, non-obvious patterns, conciseness, currency and actionability. It always prints the report first, asks before changing anything, and then applies changes as diffs.

Its update guidelines say "Propose targeted additions only". It is built to fill gaps: missing commands, undocumented gotchas, package relationships.

Two limits of its discovery step are visible in the skill file, which matches the upstream `main` branch:

1. It finds files with `find . -name "CLAUDE.md" -o -name ".claude.md" -o -name ".claude.local.md"`. The pattern `.claude.local.md` starts with a dot, so it never matches `CLAUDE.local.md`, the file name Claude Code actually reads. A `CLAUDE.local.md` in the repo is not in the list it scores.
2. The command does not look at `.claude/rules/` or `AGENTS.md`. If most of your instructions live in rules files, the score describes a fraction of them.

Its closing tips also tell users to press `#` during a session to add learnings to `CLAUDE.md`. I could not find that shortcut on the current memory, commands or interactive-mode doc pages.

### `dream`: consolidate auto memory

I wrote `dream` for the one job the other three skip. It works on a project's memory directory in four phases:

1. **Orient.** Read `MEMORY.md` and list orphan files, which have no index entry, and dead pointers, which have no file.
2. **Gather signal.** Grep the 40 most recently modified session transcripts for corrections, approaches the user confirmed, repeated friction and decisions with a rationale. It skips anything the repo or git history already records.
3. **Consolidate.** Merge duplicates. Resolve contradictions so the newest claim wins and the old one is deleted. Turn relative dates into absolute ones. Drop entries that name a file, flag or endpoint that no longer exists.
4. **Prune and index.** Rebuild `MEMORY.md` with one line per memory.

It never edits memory in place. It copies the directory to a sibling `memory.dream/`, works on the copy, and ends with a `diff -rq` plus the swap command for me to run myself. Two rules exist because of how this memory format fails. First, before deleting a file, grep for inbound `[[wikilinks]]` and repoint them. Second, never merge a `feedback` memory (how to work) with a `reference` memory (what is true), even when both are about the same topic.

The first version deleted outright, which was the wrong default for my setup. I keep long-term facts in a separate store, Hindsight, as described in [my earlier post on agent memory](/2026/11/12/agent-memory-components-my-claude-code-setup.html). A sync job mirrors auto memory into that store, so a file deleted from memory soon disappears from both places. The current version therefore treats auto memory as the place for what every session needs, and moves reference data, project history and closed items out to Hindsight. Nothing leaves memory without a copy. Every removal, whether a deleted file, a merge that drops text or a superseded claim, is first written to Hindsight as its own document. That document is read back and compared with the source, and only on an exact match does the file leave `memory.dream/`. These documents are the one write outside the copy. They only add, and the report lists them so a rejected dream can delete them.

## 3. Side by side

| | `/doctor prompt-audit` | `improve-claude-md` | `claude-md-improver` | `dream` |
|---|---|---|---|---|
| **Reads** | Instruction files, including rules and skills | One `CLAUDE.md` | `CLAUDE.md` files its `find` matches | Auto memory plus recent transcripts |
| **Looks for** | Stale, broken and contradictory instructions | Structure and adherence | Missing content | Duplicates, contradictions, stale facts, missing memories |
| **Direction** | Correct | Restructure, cut | Add | Merge, cut, add from transcripts |
| **Writes** | Report first; edits only when you ask | The rewritten file | Report and diffs; edits after you approve | A copy in `memory.dream/`, which you swap in; removed text is first copied to a long-term store |
| **Compacts `MEMORY.md`** | No | No | No | Yes |
| **Knows the memory format** | No | No | No | Yes |

## 4. When to use which

- **`MEMORY.md` is near its limit or full of near-duplicates:** `dream`. None of the other three reads auto memory by default, and only `dream` knows not to merge across memory types. Review the diff before swapping, because consolidation is lossy and a wrong merge is silent.
- **Your rules have grown over months and you suspect some are stale or contradict each other:** `/doctor prompt-audit`. Its default scope reaches `~/.claude/` rules and skills, where most of a long-lived setup sits, and it changes nothing until you ask.
- **One `CLAUDE.md` is a long flat list that the agent seems to skim past:** `improve-claude-md`. If the file already uses conditional blocks, a second pass adds little. Path-scoped rules, with a `paths:` field in their frontmatter, do the same job by harness logic rather than model judgment. Claude Code loads them only when Claude works with matching files.
- **A new or neglected repository with a thin or missing `CLAUDE.md`:** `claude-md-improver`. On a mature setup that is already close to its size budget, a tool built to add content works against you. It also misses `CLAUDE.local.md` and `.claude/rules/`.

The pattern behind the list: three of the four tools subtract or correct, and one adds. Which you need depends on whether your context is missing information or carrying too much of it. For a setup that has run for months, it is usually carrying too much.
