---
layout: post
title: "Memory Is Understood Backward: Anthropic's Agent-Memory Components, Checked Against My Claude Code Setup"
date: 2026-11-12
tags: [ai, claude-code, agents, memory]
description: "Anthropic splits agent memory into notes written in the moment and dreaming done afterward. What its experiments found, how my stack of transcripts, ctx_search, MEMORY.md and Hindsight lines up with it, and why I still keep automatic consolidation off."
image: /assets/images/2026-11-12-agent-memory-components-my-claude-code-setup-cover.jpg
---

![A dim archive at night: a small lit desk with a few index cards in the foreground, and behind it a vast, softly glowing library of shelves fading into darkness](/assets/images/2026-11-12-agent-memory-components-my-claude-code-setup-cover.jpg)

On November 6, 2026, Anthropic published [*The components of agent memory*](https://www.anthropic.com/research/components-of-agent-memory), and a [Chinese translation](https://x.com/leo_xiaolei/status/2120190829864301000) went round on X a few days later. It opens with Kierkegaard: life can only be understood backward, but it must be lived forward. An agent has the same problem with memory. It writes notes in the middle of a task, before it knows which details will matter later.

I use Claude Code every working day, with a memory stack I built one piece at a time: raw session transcripts, a search index over tool output, a size-capped notes index, and a [local Hindsight daemon](/2026/10/23/hindsight-local-daemon-setup.html). The article gave me a chance to check that stack against Anthropic's own experiments. This post summarises the article, maps my layers onto it, and lists the gaps it made me see. The mapping is my analogy, not Anthropic's.

## What the article says

The article defines agent memory as knowledge Claude gains from experience and keeps between sessions, saved as context it can read later. It excludes three neighbours: changes to weights, in-context learning within one conversation, and compaction.

It then separates two components:

| Component | When | What it does | Cost |
|---|---|---|---|
| **Memory notes** | During the task | Claude writes notes to a store (a folder of files, a database) | Takes attention from the main task; sees only the current session |
| **Dreaming** | Between sessions | Claude rereads logs and transcripts to fix mistakes and build new notes and representations | Needs compute; its output is not available immediately |

Dreaming builds on the idea of [sleep-time compute](https://arxiv.org/abs/2504.13171) from researchers at Letta and UC Berkeley: use idle time between interactions to reorganise what you already have.

The experiments behind it:

1. **Strong models choose what to remember better than fixed rules do.** About 10,000 steps into Pokémon, Sonnet 3.7 had written 413 memory files across 225 folders and earned one badge. Fable 5 had nine files in two folders plus one `global.md`, and four badges. At one point Sonnet 3.7 spent 17 steps creating six files and deleting nine without taking a single action in the game.
2. **Steering helps older models; rules can hurt newer ones.** On a CL-Bench 1.0 database task, telling Sonnet 4.6 to read its memory before answering and to test its theories nearly doubled its score. Sonnet 5 read its memory first 9 times out of 10 without being told. When Opus 5 and Opus 4.7 were told to "record only failures", they lost much of the gain memory had given them.
3. **A transcript gives dreaming a ground truth to check notes against.** In Mt. Moon, Claude had noted the wrong side of the mountain for a landmark and walked off a one-way ledge. A dreaming pass checked the note against the transcript, rewrote it, and with the corrected note Claude went straight back into the cave.
4. **Wikis help with cross-document questions and can also bloat.** On merger questions that needed several documents, Claude scored 87% from a wiki it had built against 73% from search alone. On a task where a single text search found the answer, the wiki added nothing clear. On another, the wiki grew larger than the documents, like the map in Borges's story that is as large as the empire.
5. **Dreaming can promote notes.** It can float notes to the top of the memory hierarchy, where the harness loads them at the start of every session, so Claude does not need to know there is something to search for.
6. **Dreaming fills gaps one session leaves.** A second pass found nine wiki links to a missing page, repointed them to the existing page for the same document, and added three pages, including an index.

The open questions at the end: when to write memory (in the moment distracts; in the background is late), and how to keep it current, perhaps by aiming dreaming at information that is likely to change or tuning its cadence by how often memories are accessed. The article also calls it reasonable to treat transcript search as the foundation that other representations sit on.

## My stack, layer by layer

| Layer | Tool | What it holds | How it gets read |
|---|---|---|---|
| Raw transcripts | Claude Code session files + `find-session.py` | Every prompt, tool result and reply | Regex search, on demand |
| Working set | context-mode `ctx_search` | Large tool output, fetched pages, indexed docs, a journal of the session | BM25 search, on demand |
| Curated notes | Auto-memory files + `MEMORY.md` | One fact per file, with why and how to apply it | Index preloaded every session; files read on demand |
| Always-loaded rules | `~/.claude/rules/*.md` | Facts promoted from one project to all of them | Preloaded in every project |
| Long-term store | Hindsight, one bank per repo | Retained transcripts, deliberate documents, mirrored notes, generated pages | Pages injected on the first prompt; recall, document get and reflect on demand |

### `find-session.py`: the transcript as ground truth

`find-session.py` is a short Python script of mine that searches Claude Code's session transcripts with a regex. By default it searches only the prompts I typed. Injected instructions, memory text, subagent hand-backs and compaction summaries are skipped, because they appear in every session and would match everything. `--deep` widens the search to every transcript line, including tool results and Claude's replies. `--all` searches every project instead of the current one. Each hit prints the last activity time, the session id, and the command to reopen it. It reads Codex CLI sessions too: their rollout files under `~/.codex/sessions/` record the working directory and mark which user messages were typed, so the same rules apply, and those hits are tagged `[codex]` with a `codex resume` command. `--memories` also greps Codex's own memory files, line by line.

```bash
find-session.py 'review again' --all       # sessions where I typed it, newest first
find-session.py 'some error text' --deep   # also tool results and replies
```

This is the article's foundation layer. Semantic recall is good at "what was that about"; a regex over transcripts is exhaustive for "where did I see this exact string", and it is the record that a note can be checked against.

### `ctx_search`: keeping output out of the context

The [context-mode](https://github.com/mksglu/context-mode) plugin indexes tool output that is too large to paste back. Its README describes the mechanics: output over 4,096 bytes goes into a per-project SQLite database whole, and the agent gets only the best-matching chunks plus a pointer for the rest. Each chunk lands in two FTS5 tables, one word-stemmed and one trigram. `ctx_search` ranks each table with BM25 and fuses the two lists with Reciprocal Rank Fusion. A search can cover the current session, the worktree (the default), or the whole project. After compaction, `ctx_resume` gives back a small state block.

By the article's definition most of this is not memory. It is context management, close to compaction, which the article excludes. It earns its place differently: a 50 KB log never enters the conversation, and I can query it ten minutes later without running the command again.

### `MEMORY.md`: notes promoted by hand, with a hard cap

Claude Code's auto-memory writes notes to Markdown files in a per-project folder. The format I use keeps one fact per file, with a type (`user`, `feedback`, `project`, `reference`) and, for feedback, a **Why** and a **How to apply** line. `MEMORY.md` is the index: one line per memory. [Claude Code's documentation](https://code.claude.com/docs/en/memory) says the first 200 lines or 25 KB of it, whichever comes first, load at the start of every conversation, and the rest does not.

Today my index for one busy repo is 125 lines and about 18 KB, pointing at 204 memory files. A SessionStart hook of mine warns when the index reaches 80% of either limit. Closed items move to an `ARCHIVE.md` that does not load. A memory that matters in every project gets promoted again, out of the project and into `~/.claude/rules/`, which loads everywhere.

This is the article's "top of the memory hierarchy", with one difference: nothing promotes my notes automatically. I do it, or Claude does it when I ask.

### Hindsight: retain, recall, pages, reflect

[Hindsight](https://github.com/vectorize-io/hindsight) runs as a local daemon with one memory bank per repository. These are the operations I use:

- **Retain, automatic.** The coding-agent plugin writes each session's transcript into the repo's bank when Claude stops.
- **Retain, deliberate.** A durable finding or an external document goes in under a fixed document id. To update it, I retain the full new text under the same id, then read it back with `document get` and compare it with the source before trusting it.
- **Mirror.** A sync script ([`hindsight-sync-memory.py`](https://github.com/james-wang-sage/james-wang-sage.github.io/blob/main/assets/scripts/hindsight-sync-memory.py)) copies my auto-memory files into the same bank, one document per section, and re-retains only what changed. Hooks run it in the background at session end, and on Stop at most once every ten minutes, because a long-lived session can go days without ending.
- **Pages.** Hindsight keeps a set of generated pages per bank, a curated digest of the memory behind them. I set the plugin's `autoInject` to `pages`, so the first prompt of a session gets the page passages that match it.
- **Recall.** Semantic search that returns extracted facts, not the stored text. It is good for "why did we decide this". It is bad for exact values, because table cells and literal strings get lost in extraction, so exact values come from `document get`.
- **Reflect.** An LLM synthesis over the bank. In my setup it runs on an open-weights model through a router (see [my consolidation settings](/2026/10/24/hindsight-consolidation-settings.html)). On November 6 I stopped relying on its answers: once it drew only on the current session and proposed a change that ran against the purpose of the design I had asked about. I read stored memory instead, through pages, recall and `document get`, and check each fact against its source.

The split between the two stores is deliberate. `MEMORY.md` holds only what must reach every session: hard rules, feedback that changes behaviour, and one-line pointers. Reference data, dates, recipes, history and closed items go to Hindsight, which has no load limit. Moving an item means writing it to Hindsight, reading it back, and only then trimming the note to a pointer.

## Where the article and my setup agree

**Judgement over rules.** The "record only failures" result matches how my notes are written. Many of them start from a mistake, but each one is written as a rule plus its reason, not as a log of what went wrong. The reason lets the model handle the case the rule did not foresee.

**Check the note against the record.** The article uses the transcript to correct a wrong note. The Hindsight plugin's injected guide says the same thing about everything it surfaces: what it returns is "a past record, not a live reading". A note that says "fixed" or "version X is deployed" is what someone said then. I re-read the code or the live system before acting on it.

**Volatile facts.** The article suggests aiming dreaming at information that is likely to change. My answer so far is to not store volatile values at all. Where a fact changes weekly, such as what version is deployed where, the memory holds the command that fetches it, not the value. A pointer to a command cannot go stale the way a copied value does.

**Borges's map.** The article's oversized wiki is why I like a hard cap on the always-loaded tier. 200 lines force abstraction: one line per entry, details one link away. Hindsight has no such cap, which is one more reason I read exact values from stored documents and not from a synthesis.

## Where I differ: no automatic dreaming

My `settings.json` has `autoDreamEnabled: false`. I could not find that setting in Claude Code's public documentation, so I describe only my reason for it. A background pass that merges and deletes entries on its own judgement is exactly the process most likely to misjudge a rare hard rule, and a wrong deletion is silent. The article names the related costs: notes can be wrong from the start or drift, dreaming to fix them requires compute, and maintained representations have to be kept from accumulating errors or hallucinations.

So my consolidation happens in two supervised places. When the size hook warns, I tidy `MEMORY.md` with Claude and read the diff. Hindsight builds its pages in a separate store, where nothing it does can delete a note I wrote. Promotion is manual all the way up: project note, then index line, then global rule. It is slower than dreaming, and a person has read every promoted line.

## Gaps the article showed me

- **Nothing fills cross-session gaps.** The article's second dreaming pass fixed nine broken wiki links. My notes link to each other with `[[name]]`, and a link to a note not yet written is allowed on purpose, as a marker of something worth writing. Nothing ever sweeps those links. A read-only check that lists dangling links and index lines whose file is gone would get the benefit of that pass without the risk of automatic deletion.
- **Writing in the moment has a cost.** My notes are written mid-task, which the article says distracts from the task. I accept that for now, because the notes I most need are corrections, and those are clearest at the moment they happen.
- **Synthesis is the weakest layer.** The article's wiki works because Claude both builds and checks it. My generated pages and reflect answers are useful leads, but until I can check them against their sources as cheaply as a note against a transcript, they stay leads.

## References

- Lance Martin, Anthropic, [*The components of agent memory*](https://www.anthropic.com/research/components-of-agent-memory), November 6, 2026.
- 刘老板 ([@leo_xiaolei](https://x.com/leo_xiaolei)), [Chinese translation of the article on X](https://x.com/leo_xiaolei/status/2120190829864301000), November 10, 2026.
- Lin et al., [*Sleep-time Compute: Beyond Inference Scaling at Test-time*](https://arxiv.org/abs/2504.13171), Letta and UC Berkeley, 2025.
- Claude Code documentation, [How Claude remembers your project](https://code.claude.com/docs/en/memory).
- [context-mode README](https://github.com/mksglu/context-mode), "How it works" section.
- My earlier posts: [a local Hindsight daemon for Claude Code and Codex](/2026/10/23/hindsight-local-daemon-setup.html), [Hindsight consolidation settings](/2026/10/24/hindsight-consolidation-settings.html), and [choosing long-term memory for Hermes](/2026/10/23/choosing-long-term-memory-for-hermes.html).
