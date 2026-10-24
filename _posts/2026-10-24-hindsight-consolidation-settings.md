---
layout: post
title: "Hindsight Consolidation Settings: Low Reasoning, Batch 8, and Jev"
date: 2026-10-24
tags: [ai, hindsight, decision-models, performance]
description: "The configuration I kept after testing Hindsight consolidation: low reasoning, eight facts per batch, and Jev triage for one opted-in bank, with measured costs and limitations."
image: /assets/images/2026-10-24-hindsight-consolidation-settings-cover.jpg
---

![Streams of scattered memory fragments passing through a small decision gate into an organized evidence network](/assets/images/2026-10-24-hindsight-consolidation-settings-cover.jpg)

After setting up a shared Hindsight daemon for my coding agents, I ran into the next problem: the memory was being captured, but background consolidation was slow. The machine was not spending most of its time on database writes. The model calls dominated the measured processing phases.

The configuration I kept is **low reasoning for consolidation, eight facts per LLM batch, and TypeSafe Jev as a decision model for one opted-in bank**. The main LLM remains `gpt-6-luna` through Hindsight's `chatgpt` provider.

This is a follow-up to my [local daemon setup guide](/2026/10/23/hindsight-local-daemon-setup.html). It covers the settings and an operational tuning session on October 24, 2026, using Hindsight API 1.1.0 and coding-agents integration 0.8.2 on macOS. It is not a controlled model benchmark or proof that these settings are optimal for every bank.

## What consolidation gives me

Consolidation turns related retained facts into **observations**: knowledge that can be updated as evidence changes. It can reconcile repetitions, incorporate corrections, and retain references to the facts supporting an observation. The underlying facts remain available. [Hindsight observations](https://hindsight.vectorize.io/developer/observations)

That distinction matters for development history. A memory bank might contain both “we tried batch four” and “we restored batch eight.” The useful result is an observation that distinguishes an experiment from the current decision, with evidence for both. Simply retrieving both statements leaves that reconciliation to every later answer.

Consolidation is useful for long-lived project memory, but it is not required before raw facts can be queried. A backlog means the derived observation layer is behind; it does not by itself mean the original material was lost.

## The settings I kept

| Setting | Effective value |
|---|---|
| Main LLM provider | `chatgpt` |
| Main LLM model | `gpt-6-luna` |
| Consolidation reasoning effort | `low` |
| Facts per consolidation LLM batch | `8` |
| Consolidation group parallelism | `4`, unchanged |
| Memories per consolidation round | `100`, unchanged |
| Consolidation decision provider | `typesafe` |
| Decision model alias | `jev-latest` |
| Jev scope | One opted-in project bank |

The alias resolved to `jev-1.14.0` in the connectivity tests. That identifies what answered then; a moving alias is not a version pin. [TypeSafe model aliases](https://docs.typesafe.ai/models#aliases)

The coding-agent configuration still uses daemon mode, an hourly page-refresh schedule, and a survey refresh after 20 commits:

```json
{
  "serverMode": "daemon",
  "pageTriggerCron": "H * * * *",
  "surveyRefreshCommits": 20
}
```

Those are selected fields from the existing configuration, not a replacement for the complete file. I left the page and survey settings unchanged during these consolidation tests. They describe separate background work. [Coding-agent configuration](https://hindsight.vectorize.io/sdks/integrations/coding-agents)

## The daemon configuration

For the `coding-agent` profile, the following is an explicit rendering of the effective consolidation configuration. Batch size, parallelism, and round size are shown even where the installation can inherit their defaults:

```dotenv
# ~/.hindsight/profiles/coding-agent.env
HINDSIGHT_API_LLM_PROVIDER=chatgpt
HINDSIGHT_API_LLM_MODEL=gpt-6-luna

# Restrict the reasoning change to consolidation.
HINDSIGHT_API_CONSOLIDATION_LLM_REASONING_EFFORT=low
HINDSIGHT_API_CONSOLIDATION_LLM_BATCH_SIZE=8
HINDSIGHT_API_CONSOLIDATION_LLM_PARALLELISM=4
HINDSIGHT_API_CONSOLIDATION_MAX_MEMORIES_PER_ROUND=100

# Give consolidation its own decision-model route.
HINDSIGHT_API_CONSOLIDATION_DECISION_MODEL_PROVIDER=typesafe
HINDSIGHT_API_CONSOLIDATION_DECISION_MODEL_MODEL=jev-latest
HINDSIGHT_API_CONSOLIDATION_DECISION_MODEL_API_KEY=YOUR_TYPESAFE_API_KEY

# Banks opt in individually below.
HINDSIGHT_API_CONSOLIDATION_USE_DECISION_MODEL=false
```

Replace the placeholder with the real TypeSafe key in the local profile and keep the file owner-readable only. I already had the key in `JEV_API_KEY`; Hindsight's configured credential is the operation-specific variable shown above. The example contains no usable credential.

The provider, model, and credential overrides are for **consolidation**. I did not set a global decision provider, so this change does not switch recall, reflect, or reranking to Jev. [Hindsight decision-model configuration](https://hindsight.vectorize.io/developer/configuration#decision-model)

After changing the profile, restart the daemon through its normal manager and verify the new process is ready. During this session, the stop command's short wait expired while a request was still finishing. I checked the old process had exited and the replacement was healthy before treating the restart as complete.

## Opt in one bank

The profile-level `false` above is deliberate. It keeps other banks from using the newly configured Jev route. The selected bank overrides it to `true` through Hindsight's hierarchical configuration API:

```bash
BANK_ID='coding-agent::example-repo'

curl --fail-with-body --silent --show-error \
  -X PATCH \
  "http://127.0.0.1:9077/v1/default/banks/${BANK_ID}/config" \
  -H 'Content-Type: application/json' \
  -d '{"updates":{"consolidation_use_decision_model":true}}'
```

These examples assume the same loopback API without authentication used in my setup; an authenticated installation needs its configured authorization header. Verify the resolved bank configuration with `GET` on that same URL. [Bank configuration API](https://hindsight.vectorize.io/api-reference)

In my verification, the selected bank had `consolidation_use_decision_model=true`, while the other three banks remained disabled for Jev. The effective batch size stayed at eight.

A bank-level setting is also subject to the operation boundary: in the observed runtime, an already-running consolidation round retained its starting configuration. Saving a new value was not proof that the current round had switched.

## Why I started with low reasoning

Before this tuning session, neither the global nor the consolidation-specific reasoning effort was explicitly set. The model service chose its default; I could not label that default as low, medium, or high from the configuration alone.

I set only `HINDSIGHT_API_CONSOLIDATION_LLM_REASONING_EFFORT=low`. Hindsight's performance guide recommends keeping reasoning budgets low for extraction and consolidation. [Performance guidance](https://hindsight.vectorize.io/developer/performance)

The first live observation improved from roughly 7.8 to 11.4 facts per minute of instrumented phase time, but the windows contained different numbers of facts and different batch distributions. I treated that as a reason to keep testing, not as a defensible claim that low reasoning alone caused a 47% speedup. The complete no-Jev baseline used below was already running with low reasoning and batch eight.

## Why batch four did not stay

Smaller batches looked promising early in the run. The apparent advantage faded once the complete 100-fact round finished:

| Per 100 facts | Batch eight | Batch four |
|---|---:|---:|
| LLM calls | 30 | 45 |
| Input tokens | 355,223 | 421,962 |
| Instrumented phase time | 583.894 s | 578.473 s |

Here, phase time is the sum of the logged recall, LLM, embedding, and database-write phases. It excludes orchestration overhead. It is a different measure from the whole-round wall time in the Jev comparison below.

Batch four changed that phase-time throughput by only about 1%, while making 50% more LLM calls and using about 19% more input tokens. The rounds processed different facts, so a difference this small was not persuasive evidence of a speed improvement. I removed the temporary bank override and restored eight.

I also kept group parallelism at four. The installed consolidation implementation serializes batches that write to the same observation scope. Raising the concurrency ceiling would not automatically make that work parallel. [Consolidation implementation](https://github.com/vectorize-io/hindsight/blob/main/hindsight-api-slim/hindsight_api/engine/consolidation/consolidator.py)

## What Jev actually does here

The built-in flow is:

```text
New facts + candidate observations + bank mission
                       |
                    Jev triage
                       |
        +--------------+----------------+
        |                               |
 Simple cases handled directly    Changes, conflicts, or
 with their supporting facts      cases needing rewriting
                                        |
                              Main consolidation LLM
```

Jev supplies typed judgments. The main LLM still writes the updates that need it. The installed code also checks the judgments against one another and applies the bank's mission before accepting a shortcut. My bank has a custom mission, so the triage is deliberately conservative. [Built-in triage implementation](https://github.com/vectorize-io/hindsight/blob/main/hindsight-api-slim/hindsight_api/engine/consolidation/triage.py)

I checked the actual requests rather than stopping at a successful configuration read. They appeared under `decision_consolidation_triage`, contained the new fact, candidate observations and mission, and returned successful TypeSafe responses. The early integration audit recorded no triage batch above 0.23 seconds. Over the complete test round, the logged triage batches totalled 3.73 seconds; individual request durations overlap because calls run concurrently.

## The complete Jev test

Both rows below used low reasoning and batch eight. Each round processed 100 facts:

| Metric | Without Jev | With Jev |
|---|---:|---:|
| Whole-round wall time | 590.273 s | 457.936 s |
| Facts per minute | 10.16 | 13.10 |
| Main LLM calls | 30 | 25 |
| Main LLM input tokens | 355,223 | 297,555 |
| Main LLM output tokens | 25,014 | 19,373 |
| Jev requests | 0 | 105 |
| Jev input tokens | 0 | 351,929 |

That is an observed **28.9% throughput increase**, or **22.4% less elapsed time**, and **16.7% fewer main LLM calls**. These are three different metrics. There were no recorded request errors, triage fallback warnings, or permanently failed facts in the Jev test.

The two rounds consumed different facts from a live backlog. This was a sequential operational comparison, not a paired A/B test. I did not run a complete semantic-quality evaluation, so the measurements do not prove that merge correctness or later answers improved. Request count is also not a unique-fact count: 105 Jev requests were recorded while processing 100 facts.

## The added cost

TypeSafe's published direct price, checked on October 24, 2026, is **$0.042 per million input tokens**, with output tokens free. [Official models and pricing](https://docs.typesafe.ai/models)

For the recorded round:

```text
351,929 / 1,000,000 * $0.042 = $0.014781
```

That is about **1.5 cents of added Jev API usage per 100 facts** in this sample. Two tiny connectivity tests added approximately $0.000027. These are estimates from returned usage and the public price, not an account invoice.

The main LLM uses my existing ChatGPT plan. Fewer calls primarily save plan quota and processing time; they do not reimburse the added Jev bill. At this workload's rate, a backlog of roughly 2,450 facts would add about $0.36 of Jev usage. Different context sizes, retries, or new incoming work change that estimate.

## How I will judge the next change

I kept **Jev, low reasoning, and batch eight** because this run showed a useful operational improvement at a small measured added cost. I kept Jev limited to the bank being tested.

For the next change, I want the same starting observations and fact corpus on both sides, repeated runs, full wall time including decision-model work, and a quality grade alongside cost. That grade should cover duplicates, corrections, temporal updates, and whether the bank's mission is still being followed.

The useful outcome is a memory bank that stays current at an acceptable cost. A shorter model response or a faster first few batches is only one part of that result.

The [measurement summary](/assets/data/2026-10-24-hindsight-consolidation-settings.json) includes the configuration, counters, timing definitions, and limitations used for the calculations in this post.
