---
layout: post
title: "Shared Long-Term Memory for Claude Code and Codex, Fully Local: A Hindsight Daemon Setup Guide"
date: 2026-10-23
tags: [ai, claude-code, codex, tutorial]
description: "Step-by-step: run Hindsight as a local daemon so Claude Code and Codex share per-repo memory, extracted with your ChatGPT plan (gpt-6-luna), with opt-in repos, a custom data folder, and a locked-down web UI."
image: /assets/images/2026-10-23-hindsight-local-daemon-cover.jpg
---

![Two AI coding agents feeding one local memory core inside a laptop](/assets/images/2026-10-23-hindsight-local-daemon-cover.jpg)

This is a start-to-finish guide to giving **Claude Code and Codex CLI a shared long-term memory that runs entirely on your Mac**. It uses [Hindsight](https://github.com/vectorize-io/hindsight), an MIT-licensed agent-memory engine, in **local daemon mode**. Your **ChatGPT plan** (model `gpt-6-luna`) does the memory extraction, the database lives in a folder you choose, and only the repositories you list are ever remembered.

I wrote it as the runbook for setting up a second laptop. Follow the steps in order.

> Versions used (Oct 2026): `@vectorize-io/hindsight-coding-agents` 0.8.2, `hindsight-api` 1.1.0, `hindsight` CLI 1.1.0, macOS on Apple Silicon, zsh. Newer releases may differ. See the [Coding Agents docs](https://hindsight.vectorize.io/sdks/integrations/coding-agents).

## What you will have at the end

```
Claude Code ─┐  hooks: SessionStart · UserPromptSubmit · Stop
             ├─►  Hindsight daemon (hindsight-embed)   http://127.0.0.1:9077
Codex CLI ───┘  MCP server: hindsight_* tools          │
                                                       ├─ embedded PostgreSQL (pg0)
                                                       │    data in ~/projects/hindsight-data
                                                       └─ LLM: chatgpt provider, gpt-6-luna
hindsight CLI ─────────────────────────────────────────┤
hindsight ui (web control plane, http://localhost:9999)┘
```

- **One plugin for both agents.** `@vectorize-io/hindsight-coding-agents` installs three hooks, an MCP server with the `hindsight_*` tools, and a companion skill into each agent.
- **One memory bank per repository**, named `coding-agent::<repo>`. Claude Code and Codex read and write the same bank, so a decision made in one is visible in the other.
- **Automatic capture and recall.** A session's first prompt gets a memory synthesis injected. Each session is written back when it ends. Git history and a short codebase survey seed every new bank, and the survey re-runs as the code moves on.
- **Five knowledge pages per repo:** Component map, Conventions and patterns, Core concepts, Key decisions and rationale, and Initiatives and enhancements.
- **Opt-in only.** Repositories you don't list are never touched.

## Step 1 — Prerequisites

| Requirement | Why | Check / install |
|---|---|---|
| Claude Code and/or Codex CLI | The agents being wired | `claude --version`, `codex --version` |
| Node.js (npx) | Runs the plugin installer and the hooks | `node --version` |
| uv | The daemon is launched with `uvx` | `brew install uv` |
| Rust toolchain, current | Daemon mode on macOS builds a dependency (`litellm`) that has no macOS wheel | `rustup update stable` |
| ChatGPT plan that allows usage in third-party apps | Pays for memory extraction instead of an API key | Confirmed during sign-in (Step 3) |
| `hindsight` CLI (recommended) | Inspect banks, refresh pages, launch the web UI | `curl -fsSL https://hindsight.vectorize.io/get-cli \| bash` |

## Step 2 — Write the config file first

Create `~/.hindsight/coding-agent.json` **before** installing, so the first session already follows your rules:

```json
{
  "optInOnly": true,
  "optInPaths": ["~/projects/my-repo"],
  "pageTriggerCron": "H * * * *",
  "surveyRefreshCommits": 20
}
```

```bash
chmod 600 ~/.hindsight/coding-agent.json
```

What each key does:

- **`optInOnly: true`**: memory is off everywhere by default. A repository outside `optInPaths` is inert: no bank is created, nothing is retained, and nothing is seeded.
- **`optInPaths`**: path prefixes, with `~` expanded. `~/projects/my-repo` approves that repo and its git worktrees. `~/projects` would approve every repo under it, each with its own bank. To add a repo later, append its path; there is nothing to reinstall.
- **`pageTriggerCron: "H * * * *"`**: refreshes each knowledge page at most **once an hour**. This is the default; writing it out makes it easy to change. `H` is replaced by a value hashed from the bank and page name, so pages refresh at different minutes instead of all at once. A refresh is skipped when nothing new arrived. Each refresh is one LLM synthesis per page. With a local daemon that comes out of your ChatGPT plan, so hourly is affordable. Use `"H H * * *"` (once a day) if you want to save plan usage.
- **`surveyRefreshCommits: 20`**: the codebase survey that seeds a new bank's structural knowledge **re-runs whenever 20 new commits have landed** since the last survey. This is the default. In Claude Code each survey is a headless `claude -p --model haiku` run capped at $2 (`surveyModel`, `surveyBudgetUsd`). In Codex it runs through Codex itself. Set it to `0` to survey each repo only once, when it is first opened. Busy repos will otherwise keep re-surveying.

The installer adds `"serverMode": "daemon"` to this file in Step 5.

> **On a company laptop:** list only repositories you are allowed to process this way. With the daemon, memory stays on disk locally, but the extraction step still sends transcript text to your LLM provider (OpenAI, through your ChatGPT plan). Each laptop also has **its own** memory. Two daemons don't sync.

### Opt-in list or every repo?

The config file supports two modes. Pick one per machine:

| Mode | Config | When to use it |
|---|---|---|
| **Opt-in only** (allowlist) | `"optInOnly": true` + `"optInPaths": [...]` | A work laptop, or any machine where only some repositories may be processed |
| **Every repo** (denylist) | Remove `optInOnly` and `optInPaths` entirely; exclude individual repos with `banks.<id>.disabled` | A personal machine where you want memory everywhere |

Switching from opt-in to every repo means deleting the two keys:

```json
{
  "serverMode": "daemon",
  "pageTriggerCron": "H * * * *",
  "surveyRefreshCommits": 20,
  "banks": {
    "coding-agent::private-notes": { "disabled": true }
  }
}
```

The change applies at your next prompt, because the hooks re-read the file on every call. MCP tools pick it up in the next session. From then on, the first session in any repo creates its `coding-agent::<repo>` bank, seeds it from git history (the most recent commits, 300 by default), and runs a codebase survey. The survey runs again every `surveyRefreshCommits` (20) new commits. In Claude Code each survey is a `claude -p --model haiku` run with a $2 budget cap. Every repo's transcripts now go to your extraction LLM. With a local daemon the storage stays on your Mac, but the extraction still happens at the provider. Disable the repos where that is not acceptable.

Optional per-repo controls live in the same file, keyed by bank id:

```json
{
  "banks": {
    "coding-agent::some-repo": { "disabled": true },
    "coding-agent::big-monorepo": { "gitIngest": "full", "retainSessions": false }
  }
}
```

## Step 3 — Sign Hindsight in to your ChatGPT plan

Hindsight's `chatgpt` provider uses OpenAI's official *Sign in with ChatGPT* flow. Hindsight registers as its own OAuth client and stores its **own** credentials, separate from the Codex CLI's login.

```bash
uvx --from hindsight-api-slim hindsight-admin chatgpt login
```

A browser window opens. Sign in and **approve plan usage**. The command waits for the callback on `127.0.0.1:1455`, then saves `~/.hindsight/chatgpt/credentials.json` with mode `0600`.

You may see warnings that `sentence-transformers` is not installed. They come from running the admin tool out of the slim package and do not affect sign-in.

Confirm:

```bash
uvx --from hindsight-api-slim hindsight-admin chatgpt status
# Signed in: yes
# Plan usage enabled: yes
```

Tokens refresh automatically. Usage counts against your ChatGPT plan and shows at <https://chatgpt.com/settings/usage>.

## Step 4 — Pin the provider and model in your shell

Add to `~/.zshrc`:

```bash
# Hindsight daemon: extract memories with the ChatGPT plan, model pinned
export HINDSIGHT_API_LLM_PROVIDER=chatgpt
export HINDSIGHT_API_LLM_MODEL=gpt-6-luna
```

Open a **new** terminal and check:

```bash
echo "$HINDSIGHT_API_LLM_PROVIDER / $HINDSIGHT_API_LLM_MODEL"
# chatgpt / gpt-6-luna
```

Why set both explicitly:

- **Provider.** When the daemon starts, the plugin chooses the provider in this order: `HINDSIGHT_API_LLM_PROVIDER`, then whichever of `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, `GEMINI_API_KEY`, `GROQ_API_KEY` is set first, then `claude-code` if the `claude` CLI is on `PATH`. Setting it explicitly guarantees `chatgpt`, even if an API key happens to be in your environment.
- **Model.** `gpt-6-luna` is the `chatgpt` provider's default today. Pinning it keeps it if a future release changes the default. The runtime updates itself daily.
- All `HINDSIGHT_API_*` variables in the environment that starts the daemon are passed on to it. To use a different model only for extraction, use the per-operation variables (for example `HINDSIGHT_API_RETAIN_LLM_MODEL`).

## Step 5 — Install the plugin in daemon mode

From that new terminal:

```bash
npx @vectorize-io/hindsight-coding-agents install claude-code codex --server daemon
```

The output should include `local extraction will use chatgpt (from HINDSIGHT_API_LLM_PROVIDER)`. The installer:

| Agent | What gets wired |
|---|---|
| Claude Code | 3 hooks merged into `~/.claude/settings.json`; MCP server registered with `claude mcp add` (user scope); skill at `~/.claude/skills/hindsight-coding-agent` |
| Codex CLI | 3 hooks merged into `~/.codex/hooks.json`; `[mcp_servers.hindsight]` in `~/.codex/config.toml`; skill at `~/.agents/skills/hindsight-coding-agent` |
| Shared | Runtime copied to `~/.hindsight/coding-agents`; `"serverMode": "daemon"` written to `~/.hindsight/coding-agent.json` |

Codex also needs its hooks feature flag. If `~/.codex/config.toml` has no `[features]` section, the installer adds one for you. If the section already exists, the installer prints a reminder instead, and you add the line yourself:

```toml
[features]
hooks = true
```

The installer accepts either `hooks = true` or the older spelling `codex_hooks = true`, which some docs still use.

Notes:

- The plugin is installed with npx, not through a Claude Code marketplace, so it is not listed under `/plugin`. Manage it with `npx @vectorize-io/hindsight-coding-agents install | uninstall | update | stats`.
- If an older per-agent Hindsight plugin (such as `hindsight-memory`) is installed, uninstall it first so only one set of hooks runs.

## Step 6 — Start the daemon and verify it

The SessionStart and Stop hooks start the daemon by themselves, in the background, whenever port 9077 is free. Start it once by hand so the slow first run (download, Rust build, model load) happens while you watch:

```bash
node ~/.hindsight/coding-agents/dist/daemon-start.js --harness claude-code
```

Verify:

```bash
lsof -iTCP:9077 -sTCP:LISTEN                 # a python process on localhost:9077

PID=$(lsof -tiTCP:9077 -sTCP:LISTEN)
ps eww -p $PID | tr ' ' '\n' | grep '^HINDSIGHT_API_LLM_'
# HINDSIGHT_API_LLM_PROVIDER=chatgpt
# HINDSIGHT_API_LLM_MODEL=gpt-6-luna
```

Under the hood, the plugin asks `hindsight-embed` to start the server. `hindsight-embed` runs `hindsight-api --idle-timeout 0 --port 9077` together with an embedded PostgreSQL 18 instance managed by `pg0`.

## Step 7 — Pin the provider in the daemon profile file

The daemon also has a per-profile env file, `~/.hindsight/profiles/coding-agent.env`, created on first start. Make it agree with your shell. Then a daemon started from a context that doesn't load `~/.zshrc`, such as an agent opened from the Dock, still uses ChatGPT and `gpt-6-luna`:

```bash
f=~/.hindsight/profiles/coding-agent.env
cp "$f" "$f.bak"
grep -n '^HINDSIGHT_API_LLM_' "$f"        # inspect what it currently says
```

Edit it so it contains these two lines, and remove any `HINDSIGHT_API_LLM_API_KEY=` line:

```bash
HINDSIGHT_API_LLM_PROVIDER=chatgpt
HINDSIGHT_API_LLM_MODEL=gpt-6-luna
```

```bash
chmod 600 "$f" "$f.bak"
```

## Step 8 — Put the memory bank where you want it

By default the database lives in `~/.pg0/instances/hindsight-embed-coding-agent/data`. Hindsight has no setting for this path, but `pg0` follows a symlink. Here is how to move it to `~/projects/hindsight-data`.

1. **Stop the daemon and its PostgreSQL.** Never copy a running database.

   ```bash
   kill $(lsof -tiTCP:9077 -sTCP:LISTEN)
   # wait until postgres has exited and postmaster.pid is gone
   pgrep -f 'postgres -D .*hindsight-embed-coding-agent' || echo "postgres stopped"
   ls ~/.pg0/instances/hindsight-embed-coding-agent/data/postmaster.pid 2>/dev/null || echo "clean shutdown"
   ```

2. **Copy, verify, then swap in a symlink:**

   ```bash
   SRC=~/.pg0/instances/hindsight-embed-coding-agent
   DST=~/projects/hindsight-data
   mkdir -p "$DST"
   cp -a "$SRC" "$DST/"                                       # -a keeps the 0700 permissions PostgreSQL requires
   diff -rq "$SRC" "$DST/hindsight-embed-coding-agent" && echo "identical"
   mv "$SRC" "$SRC.old"
   ln -s "$DST/hindsight-embed-coding-agent" "$SRC"
   ```

3. **Restart and confirm** PostgreSQL now runs from the new folder:

   ```bash
   node ~/.hindsight/coding-agents/dist/daemon-start.js --harness claude-code
   lsof -p $(pgrep -f 'postgres -D .*hindsight-embed-coding-agent' | head -1) | grep -m1 hindsight-data
   ```

4. Once everything works (Step 12), delete `$SRC.old`.

Keep `~/projects/hindsight-data` **out of git and out of iCloud Drive or Dropbox**. Live syncing can corrupt a running database. To back it up, stop the daemon and copy the folder.

## Step 9 — Seed memory from past conversations

From inside each opted-in repository:

```bash
cd ~/projects/my-repo
npx @vectorize-io/hindsight-coding-agents install claude-code --import-conversations
# and/or: ... install codex --import-conversations
```

- The import reads the agent's local transcripts and keeps only sessions whose **recorded working directory** is this repository.
- It uses LLM tokens in proportion to the history (your ChatGPT plan here). It is safe to re-run, because documents are de-duplicated by id.
- Git commit messages and a codebase survey are ingested automatically at the next session start. New commits are appended as they land, and the survey re-runs every 20 commits (`surveyRefreshCommits`).
- `CLAUDE.md` and Claude Code's auto-memory notes (`~/.claude/projects/*/memory/*.md`) are not imported. `CLAUDE.md` is loaded into every session anyway. To store a memory note in the bank, ask the agent to save it with the `hindsight_ingest_document` tool.

## Step 10 — Start fresh agent sessions

The hooks read `~/.hindsight/coding-agent.json` every time they run. The MCP server behind the `hindsight_*` tools reads it **once, when it starts**. After installing, start new Claude Code and Codex sessions. In an already-open Claude Code session, run `/mcp` → `hindsight` → **Reconnect**.

In a new session you should see the Hindsight memory banner. The tools the agent can call:

| Tool | Use |
|---|---|
| `hindsight_search_knowledge_pages` / `hindsight_read_knowledge_page` / `hindsight_list_knowledge_pages` | Look up architecture, conventions, decisions |
| `hindsight_reflect` | Deep reasoning over all memory ("why is X like this?") |
| `hindsight_ingest_document` | Save notes or a document into memory |
| `hindsight_capture_initiative` | Track a new feature or plan as its own page |
| `hindsight_sync_status` / `hindsight_diagnose` | Check ingestion status and configuration |

## Step 11 — Point the CLI at the daemon

Without configuration the `hindsight` CLI targets `http://localhost:8888`. Point it at the daemon:

```bash
hindsight configure --api-url http://localhost:9077
chmod 600 ~/.hindsight/config
```

Useful commands (`<bank>` is `coding-agent::my-repo`):

```bash
hindsight health                              # Status: healthy · Database: connected
hindsight bank list
hindsight bank stats <bank>                   # nodes, links, documents, pending/failed operations
hindsight document list <bank>
hindsight operation list <bank>               # retain / consolidation / refresh jobs and their status
hindsight mental-model list <bank>            # the knowledge pages
hindsight mental-model refresh <bank> <id>    # refresh one page now
hindsight explore                             # interactive terminal explorer
```

The plugin also ships a one-shot status report:

```bash
node ~/.hindsight/coding-agents/dist/status.js --repo ~/projects/my-repo
# {"bank":"coding-agent::my-repo","gitlogPresent":true,"chatDocs":…,"pagesCount":5,"surveyDocs":4,"synced":true,…}
```

### Querying another repo's memory (cross-bank)

The `hindsight_*` MCP tools are bound to the **current repo's bank**. None of them takes a bank parameter, so an agent working in repo A can't use them to ask what was decided in repo B. Use the CLI against the other bank instead:

```bash
hindsight bank list                                    # find the bank id
hindsight memory recall 'coding-agent::other-repo' "how do we handle retries on 4xx?" -o json
hindsight memory recall 'coding-agent::other-repo' "deployment steps" -t world,experience -o json
```

- **Use `recall`, not `reflect`, for cross-bank lookups.** `recall` returns the stored memories (facts, experiences, observations) ranked by relevance. `reflect` synthesizes an answer through the target bank's `reflect_mission` and disposition. Coding-agent banks get a debugging-assistant mission, so `reflect` answers in that bank's voice instead of showing you what it holds.
- `-t/--fact-type` narrows the types (`world`, `experience`, `observation`). Separate several with commas (`-t world,experience`) or repeat the flag. `-o json` makes the output easy for an agent to parse.
- **Say where a fact came from.** When an agent quotes cross-bank results, it should name the source bank (`coding-agent::other-repo`) so nobody mistakes it for the current repo's own memory.
- To make agents do this automatically, add a line like this to your global `~/.claude/CLAUDE.md` (and Codex's `AGENTS.md`):

  ```markdown
  - Cross-repo memory: `hindsight_*` MCP tools only see the current repo's bank. To read another repo's
    memory run `hindsight memory recall 'coding-agent::<repo>' "<question>" -o json` (recall, not reflect —
    reflect applies the target bank's mission) and cite the source bank in the answer.
  ```

- If some of your repos must never inform each other, write that rule next to it. Separate banks keep the data apart, but the agent can still bridge them with this command. The CLI query is the only path across banks, so the rule only has to govern that one command.

## Step 12 — Generate the knowledge pages

A new bank's pages show "No content yet." until their first hourly slot comes, which can take up to an hour. To build them right away (this only uses your ChatGPT plan):

```bash
B=coding-agent::my-repo
for id in $(hindsight mental-model list $B -o json | python3 -c "import sys,json;[print(m['id']) for m in json.load(sys.stdin)['items']]"); do
  hindsight mental-model refresh $B $id
done
hindsight operation list $B          # wait for the refresh_mental_model jobs to finish
```

From then on, each page refreshes at most once an hour, and only when there is new material.

## Step 13 — The web UI

The CLI can launch Hindsight's web control plane (`@vectorize-io/hindsight-control-plane`, a Next.js app) against the API URL in your CLI config, which is the daemon. It needs Node.js.

**By default it is reachable from your whole network with no login.** It binds to `0.0.0.0` and requires no sign-in unless an access key is set. Launch it locked down instead:

```bash
KEY=$(openssl rand -hex 16); echo "UI access key: $KEY"
HOSTNAME=127.0.0.1 HINDSIGHT_CP_ACCESS_KEY="$KEY" hindsight ui
```

- `HOSTNAME=127.0.0.1` binds it to localhost only, so other devices on the network can't reach it. The startup log then shows `Network: http://localhost:9999` instead of `0.0.0.0`.
- `HINDSIGHT_CP_ACCESS_KEY` turns on the login page. Opening `/` redirects to `/login`, and the UI's API routes return 401 until you enter the key printed above.
- The line `No API key configured (public access)` in the log is about the key the UI sends **to the daemon** (`HINDSIGHT_CP_DATAPLANE_API_KEY`). The local daemon needs none. That line does not mean the UI itself is open.

Then:

1. The first run installs the control-plane package through npx, which takes about a minute. When it is ready it prints `Local: http://localhost:9999` and `Connecting to dataplane at: http://localhost:9077`.
2. Open **<http://localhost:9999>** and sign in with the key. The dashboard lists your banks. Inside a bank you can browse documents, memories, entities and the memory graph, look at the knowledge pages (mental models), check operations, and try recall and reflect queries.
3. Stop it when you're done:

   ```bash
   kill $(lsof -tiTCP:9999 -sTCP:LISTEN)
   ```

For a quick look without a browser, `hindsight explore` opens a terminal explorer of the same data.

## How it behaves day to day

- **Start:** the SessionStart and Stop hooks of Claude Code or Codex start the daemon in the background if port 9077 is free. Both agents and all repos share one daemon.
- **Stop:** it does **not** exit when idle. Closing your agents leaves it running, using roughly 1–1.5 GB of RAM and no LLM usage while idle. It stops on reboot and comes back with the next session. To stop it yourself: `kill $(lsof -tiTCP:9077 -sTCP:LISTEN)`.
- **Changing provider, model or other daemon settings:** a running daemon is reused and never restarted, so stop it after any change. The next session (or `daemon-start.js`) starts it with the new settings.
- **Updates:** the plugin checks npm once a day and updates its runtime. Re-run `install` only when a release adds new hooks.
- **Writes are asynchronous:** a saved document appears once its retain job completes (`hindsight operation list <bank>`).
- **Logs:** `~/.hindsight/coding-agents-logs/plugin.log`, `diag.jsonl` (every reflect/retain/page event), `usage.jsonl`. Summary: `npx @vectorize-io/hindsight-coding-agents stats`.

## Final checklist

- [ ] `~/.zshrc`: `HINDSIGHT_API_LLM_PROVIDER=chatgpt`, `HINDSIGHT_API_LLM_MODEL=gpt-6-luna`, visible in a new terminal
- [ ] `hindsight-admin chatgpt status`: signed in, plan usage enabled
- [ ] `~/.hindsight/coding-agent.json`: `serverMode: "daemon"`, `pageTriggerCron: "H * * * *"`, `surveyRefreshCommits` set the way you want (20 by default, `0` = survey once), mode `600`. Either `optInOnly: true` with the right `optInPaths`, or no opt-in keys plus `banks.<id>.disabled` for the repos to exclude.
- [ ] Cross-bank lookup works: `hindsight memory recall 'coding-agent::<repo>' "<question>" -o json` returns results
- [ ] `~/.hindsight/profiles/coding-agent.env`: `chatgpt` + `gpt-6-luna`, no API-key line, mode `600`
- [ ] `~/.codex/config.toml`: `hooks = true` under `[features]`, `[mcp_servers.hindsight]` present
- [ ] Daemon on `127.0.0.1:9077` with the right `HINDSIGHT_API_LLM_*` in `ps eww`; `hindsight health` healthy
- [ ] `~/.pg0/instances/hindsight-embed-coding-agent` → symlink to `~/projects/hindsight-data/…`; PostgreSQL has files open there
- [ ] Per repo: `status.js --repo …` shows `synced: true`, `pagesCount: 5`, `surveyDocs: 4`; `hindsight operation list` shows nothing `failed`
- [ ] In a new agent session, `hindsight_sync_status` returns the same numbers as `status.js`
- [ ] Web UI launched only with `HOSTNAME=127.0.0.1` and `HINDSIGHT_CP_ACCESS_KEY`, and stopped when not in use (nothing listening on `:9999`)

## Uninstall

```bash
npx @vectorize-io/hindsight-coding-agents uninstall all     # removes the hooks, MCP entries and skills install added
                                                            # (Codex's [features] hooks flag stays, since other hooks may use it)
kill $(lsof -tiTCP:9077 -sTCP:LISTEN)                       # stop the daemon
# memory data: ~/projects/hindsight-data (and the symlink in ~/.pg0/instances) — delete only if you mean it
```
