#!/usr/bin/env python3
"""Mirror agent memory notes into each repo's Hindsight bank (coding-agent::<repo>).

Two sources, one document per unit, re-retained only when its text changed (local sha256 vs the
document's content_hash, which is sha256(original_text)):

  Claude Code auto-memory  ~/.claude/projects/<encoded-repo-path>/memory/
      one doc per `##` section of MEMORY.md / ARCHIVE.md   id claude-memory-[archive-]<section-slug>
  Codex memories           ~/.codex/memories/MEMORY.md (global; Codex rewrites it)
      one doc per `# Task Group`, routed by the group's cwd= entries   id codex-memory-<title-slug>

A bank is only ever written if it already exists (bank list); nothing here creates one. Documents
under those two id prefixes that no longer have a source are deleted; nothing else is touched.
Codex raw_memories.md / rollout_summaries/ (transcript-grade) and memory_summary.md (a global
profile, not per-repo) are deliberately not mirrored.

  hindsight-sync-memory.py              retain changed docs, delete orphans, wait, print a summary
  hindsight-sync-memory.py --check      list what would change; no LLM calls, no writes; exit 0
  hindsight-sync-memory.py --all        re-retain every doc
  ... --bank my-repo                    limit to one bank (repeatable)
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone

H = os.environ.get("HINDSIGHT_BIN") or shutil.which("hindsight") or sys.exit("hindsight CLI not found; set HINDSIGHT_BIN")
HOME = os.path.expanduser("~")
CLAUDE_PROJECTS = f"{HOME}/.claude/projects"
CODEX_MEMORY = f"{HOME}/.codex/memories/MEMORY.md"
PREFIXES = ("claude-memory-", "codex-memory-")
CTX_CLAUDE = ("Claude Code auto-memory for this repo: curated notes the agent saved across sessions "
              "(feedback = user preferences/rules, project = ongoing work, reference = where things are). "
              "Each fact reflects when its file was written.")
CTX_CODEX = ("Codex consolidated memory (~/.codex/memories/MEMORY.md) for this repo: one task group of "
             "past Codex work. Each fact reflects when that task ran.")
# Codex task groups never mirrored (regex on the title, case-insensitive), e.g. (r"personal", r"1:1").
# An excluded group's existing doc becomes an orphan and is deleted on the next sync.
EXCLUDE_CODEX = ()


def hs(*args):
    return subprocess.run([H, *args], check=True, capture_output=True, text=True).stdout


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def iso(epoch):
    return datetime.fromtimestamp(epoch, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


# ---- Claude Code auto-memory -------------------------------------------------------------------

def sections(path, default):
    """[(section name, [(index line, file)])] for one index file; entries before any ## go to `default`."""
    out, name, entries = [], default, []
    for line in open(path, encoding="utf-8"):
        if line.startswith("## "):
            out.append((name, entries))
            name, entries = line[3:].strip(), []
        else:
            for f in re.findall(r"\]\(([^)/]+\.md)\)", line):
                if f not in ("MEMORY.md", "ARCHIVE.md"):
                    entries.append((line.strip().removeprefix("- "), f))
    out.append((name, entries))
    return [(n, e) for n, e in out if e]


def claude_docs(memdir, repo):
    docs, seen = {}, set()
    for index, default, archived in (("MEMORY.md", "Unsectioned", False),
                                     ("ARCHIVE.md", "Archived (closed items)", True)):
        path = os.path.join(memdir, index)
        if not os.path.exists(path):
            continue
        for name, entries in sections(path, default):
            entries = [(l, f) for l, f in entries if os.path.exists(os.path.join(memdir, f))]
            if not entries:
                continue
            if archived:
                head = (f'ARCHIVED memory: section "{name}" of ARCHIVE.md, {repo} Claude Code auto-memory. '
                        "These entries were moved out of the active index because they are CLOSED, stale, or "
                        "duplicated by always-loaded rule files; treat them as history, not current state. "
                        "Each entry is one memory file (frontmatter + body). Facts reflect when each was written.")
            else:
                head = (f'Claude Code auto-memory for {repo}, section "{name}" of MEMORY.md. Each entry is one '
                        "memory file (frontmatter + body). Facts reflect when each was written.")
            parts = [head]
            for line, f in entries:
                seen.add(f)
                parts.append(f"### {f}\nIndex line: {line}\n\n" + open(os.path.join(memdir, f), encoding="utf-8").read())
            docs[f"claude-memory-{'archive-' if archived else ''}{slug(name)}"] = (
                "\n\n".join(parts), CTX_CLAUDE,
                iso(max(os.path.getmtime(os.path.join(memdir, f)) for _, f in entries)))
    # Files no index links to would otherwise vanish silently.
    loose = sorted(f for f in os.listdir(memdir) if f.endswith(".md") and f not in seen | {"MEMORY.md", "ARCHIVE.md"})
    if loose:
        parts = [f"Claude Code auto-memory for {repo}: files present in the memory directory but not linked "
                 "from MEMORY.md or ARCHIVE.md. Each entry is one memory file. Facts reflect when each was written."]
        parts += [f"### {f}\n\n" + open(os.path.join(memdir, f), encoding="utf-8").read() for f in loose]
        docs["claude-memory-unindexed"] = ("\n\n".join(parts), CTX_CLAUDE,
                                           iso(max(os.path.getmtime(os.path.join(memdir, f)) for f in loose)))
    return docs


def claude_bank(dirname, banks):
    """~/.claude/projects dir names encode the repo path with every non-alphanumeric char as '-'."""
    hits = [b for b in banks if dirname.endswith("-" + re.sub(r"[^A-Za-z0-9]", "-", b))]
    return max(hits, key=len) if hits else None


# ---- Codex memories ----------------------------------------------------------------------------

def codex_bank(cwd, banks):
    """cwd belongs to a bank when the bank's repo name is one of its path segments (covers worktrees, mirrors)."""
    segs = cwd.strip("/").split("/")
    hits = [b for b in banks if b in segs]
    return max(hits, key=len) if hits else None


def codex_docs(banks):
    """{bank: {doc id: (body, ctx, ts)}}, plus the titles of groups that map to no bank."""
    text = open(CODEX_MEMORY, encoding="utf-8").read()
    groups = re.split(r"(?m)^(?=# Task Group: )", text)[1:]
    out, skipped = {}, []
    for g in groups:
        title = g.splitlines()[0].removeprefix("# Task Group: ").strip()
        if any(re.search(p, title, re.I) for p in EXCLUDE_CODEX):
            skipped.append(f"{title} [excluded]")
            continue
        cwds = {c.rstrip(";,)/") for c in re.findall(r"cwd=([^\s,]+)", g)}
        targets = {b for b in (codex_bank(c, banks) for c in cwds) if b}
        if not targets:
            skipped.append(title)
            continue
        stamps = re.findall(r"updated_at=(\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d)", g)
        ts = max(stamps) + "Z" if stamps else iso(os.path.getmtime(CODEX_MEMORY))
        for b in targets:
            body = f"Codex memory for {b}, task group from ~/.codex/memories/MEMORY.md.\n\n{g.strip()}\n"
            ids = out.setdefault(b, {})
            # Titles often start with the cwd ("/path/to/my-repo Fix ..."); the bank already says which repo.
            base = "codex-memory-" + slug(re.sub(r"^/\S+\s+", "", title))[:100].rstrip("-")
            doc_id, n = base, 2
            while doc_id in ids:
                doc_id, n = f"{base}-{n}", n + 1
            ids[doc_id] = (body, CTX_CODEX, ts)
    return out, skipped, len(groups)


# ---- sync --------------------------------------------------------------------------------------

def remote_docs(bank):
    d = json.loads(hs("document", "list", bank, "-l", "5000", "-o", "json"))
    if d.get("total", len(d["items"])) != len(d["items"]):
        sys.exit(f"{bank}: document list truncated ({len(d['items'])} of {d['total']}); refusing to compute orphans")
    return {i["id"]: i["content_hash"] for i in d["items"] if i["id"].startswith(PREFIXES)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--bank", action="append", help="repo name, e.g. my-repo")
    a = ap.parse_args()

    try:
        existing = {b["bank_id"].removeprefix("coding-agent::")
                    for b in json.loads(hs("bank", "list", "-o", "json"))
                    if b["bank_id"].startswith("coding-agent::")}
    except Exception as e:
        sys.exit(f"hindsight daemon unreachable or bank list failed: {e}")
    banks = {b for b in existing if not a.bank or b in a.bank}

    # local[bank][doc id] = (body, ctx, ts); `owned` = prefixes whose source was read for that bank,
    # so orphans are only computed where a source actually exists.
    local, owned = {}, {}
    for d in sorted(os.listdir(CLAUDE_PROJECTS)):
        memdir = os.path.join(CLAUDE_PROJECTS, d, "memory")
        b = claude_bank(d, banks)
        if b and os.path.exists(os.path.join(memdir, "MEMORY.md")):
            local.setdefault(b, {}).update(claude_docs(memdir, b))
            owned.setdefault(b, set()).add("claude-memory-")
    skipped, ngroups = [], 0
    if os.path.exists(CODEX_MEMORY):
        cdocs, skipped, ngroups = codex_docs(banks)
        if ngroups:
            for b in banks:
                local.setdefault(b, {}).update(cdocs.get(b, {}))
                owned.setdefault(b, set()).add("codex-memory-")

    plan = []  # (bank, action, doc id)
    for b in sorted(owned):
        remote = remote_docs(f"coding-agent::{b}")
        for doc_id, (body, _, _) in sorted(local.get(b, {}).items()):
            if a.all or remote.get(doc_id) != sha(body):
                plan.append((b, "new" if doc_id not in remote else "changed", doc_id))
        for doc_id in sorted(remote):
            if doc_id.startswith(tuple(owned[b])) and doc_id not in local.get(b, {}):
                plan.append((b, "orphan", doc_id))

    big = max((len(v[0].encode()) for docs in local.values() for v in docs.values()), default=0)
    print(f"Codex task groups: {ngroups}, skipped (no existing bank or excluded): {len(skipped)}. Largest doc: {big // 1024} KB.")
    for t in skipped:
        print(f"  skipped codex group: {t}")
    if not plan:
        print("Up to date: nothing to retain or delete.")
        return 0
    for b, act, doc_id in plan:
        print(f"  {act:8} coding-agent::{b}  {doc_id}")
    if a.check:
        n = sum(1 for p in plan if p[1] != "orphan")
        print(f"{n} to retain, {len(plan) - n} to delete. Run without --check to apply.")
        return 0

    ops = []
    for b, act, doc_id in plan:
        bank = f"coding-agent::{b}"
        if act == "orphan":
            hs("document", "delete", bank, doc_id)
            print(f"deleted {bank} {doc_id}")
            continue
        body, ctx, ts = local[b][doc_id]
        op = json.loads(hs("memory", "retain", bank, body, "-d", doc_id, "-c", ctx, "-t", ts, "--async", "-o", "json"))
        ops.append((bank, doc_id, op["operation_id"]))

    failed = 0
    for bank, doc_id, op in ops:
        for _ in range(90):
            s = json.loads(hs("operation", "get", bank, op, "-o", "json"))["status"]
            if s not in ("pending", "processing"):
                break
            time.sleep(10)
        print(f"{s} {bank} {doc_id}")
        failed |= s != "completed"
    print(f"Retained {len(ops)} document(s); failed: {int(failed)}.")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
