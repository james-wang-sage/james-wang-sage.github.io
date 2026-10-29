---
layout: post
title: "Hindsight Consolidation Settings: Low Reasoning, Batch 8, and Jev"
date: 2026-10-24
tags: [ai, hindsight, decision-models, performance]
description: "The Hindsight configuration I kept after testing: low-reasoning consolidation with Jev triage for one bank, then a remote reranker and a Jev-orchestrated reflect, with measured costs and limitations."
image: /assets/images/2026-10-24-hindsight-consolidation-settings-cover.jpg
---

![Streams of scattered memory fragments passing through a small decision gate into an organized evidence network](/assets/images/2026-10-24-hindsight-consolidation-settings-cover.jpg)

After setting up a shared Hindsight daemon for my coding agents, I ran into the next problem: the memory was being captured, but background consolidation was slow. The machine was not spending most of its time on database writes. The model calls dominated the measured processing phases.

The configuration I kept is **low reasoning for consolidation, eight facts per LLM batch, and TypeSafe Jev as a decision model for one opted-in bank**. The main LLM remains `gpt-6-luna` through Hindsight's `chatgpt` provider.

This is a follow-up to my [local daemon setup guide](/2026/10/23/hindsight-local-daemon-setup.html). It covers the settings and an operational tuning session on October 24, 2026, using Hindsight API 1.1.0 and coding-agents integration 0.8.2 on macOS. It is not a controlled model benchmark or proof that these settings are optimal for every bank.

> **Update, October 25, 2026:** I later gave `reflect` its own LLM and Jev decision route and replaced the local reranker with a remote one. Unlike consolidation, the reflect decision model is on for every bank by default. Those changes, and two routing experiments I dropped, are in the [October 25 update](#update-october-25-reflect-and-recall).

> **Update, October 29, 2026:** The current reranker is `cohere/rerank-4-fast` through OpenRouter, replacing Voyage after upstream rate-limit failures. The configuration example below is updated; the October 25 measurements remain historical. See the [October 29 update](#update-october-29-replace-the-rate-limited-reranker).

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
| Jev scope for consolidation | One opted-in project bank |

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

The provider, model, and credential overrides above are for **consolidation** only. I did not set a global decision provider, so this block by itself does not switch recall or reflect to Jev. [Hindsight decision-model configuration](https://hindsight.vectorize.io/developer/configuration#decision-model) Reflect later got its own decision-model route; see the [October 25 update](#update-october-25-reflect-and-recall).

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

## Update, October 25: reflect and recall

The consolidation settings above did not change. Late on October 24, running into the early hours of October 25, I turned to the interactive side, because `reflect` answers felt slow. One logged reflect spent 28.7 seconds in model calls and 0.22 seconds in its retrieval tools. The time was going to the remote model, not to the laptop.

These settings were added to the same profile. The reranker entry now shows the October 29 replacement; the other entries are unchanged:

| Setting | Effective value |
|---|---|
| Reflect LLM provider | `openrouter`, automatic upstream routing |
| Reflect LLM model | `openai/gpt-oss-120b` |
| Reflect reasoning effort | `low` |
| Reflect decision provider | `typesafe` |
| Reflect decision model alias | `jev-latest` |
| Reranker provider | `openrouter` |
| Reranker model | `cohere/rerank-4-fast` |

```dotenv
# ~/.hindsight/profiles/coding-agent.env (additions)

# Reflect gets its own LLM route. Retain and consolidation keep the main chatgpt route.
HINDSIGHT_API_REFLECT_LLM_PROVIDER=openrouter
HINDSIGHT_API_REFLECT_LLM_MODEL=openai/gpt-oss-120b
HINDSIGHT_API_REFLECT_LLM_REASONING_EFFORT=low
HINDSIGHT_API_REFLECT_LLM_API_KEY=YOUR_OPENROUTER_API_KEY

# Reflect decision model. On for every bank unless a bank opts out.
HINDSIGHT_API_REFLECT_DECISION_MODEL_PROVIDER=typesafe
HINDSIGHT_API_REFLECT_DECISION_MODEL_MODEL=jev-latest
HINDSIGHT_API_REFLECT_DECISION_MODEL_BASE_URL=https://api.typesafe.ai
HINDSIGHT_API_REFLECT_DECISION_MODEL_API_KEY=YOUR_TYPESAFE_API_KEY

# Remote reranker through OpenRouter's rerank endpoint (updated October 29).
HINDSIGHT_API_RERANKER_PROVIDER=openrouter
HINDSIGHT_API_RERANKER_OPENROUTER_MODEL=cohere/rerank-4-fast
HINDSIGHT_API_RERANKER_OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/rerank
HINDSIGHT_API_RERANKER_OPENROUTER_API_KEY=YOUR_OPENROUTER_API_KEY
```

The biggest operational change is not a number: reflect answers are now written by `gpt-oss-120b` on a pay-per-token route, not by the `gpt-6-luna` model on my ChatGPT plan. The reranker also sends each query and its candidate memory text to OpenRouter and the upstream reranking provider. Embeddings stay local.

### Moving the reflect LLM alone was not faster

I picked `gpt-oss-120b` after a published leaderboard listed the Groq-served model at an average of 2.2 seconds of total reflect time. I had no Groq key, so I routed it through my existing OpenRouter key. Three complete reflects took 23.4, 30.4, and 34.0 seconds, no better than the 28.7-second example. OpenRouter was choosing the upstream provider automatically.

Pinning OpenRouter to Groq passed an authentication check, but complete reflects then failed repeatedly with tool-call validation errors. I reverted to automatic routing. The model route stayed because the next two changes were measured on it; it is not a speed improvement by itself.

### Remote reranking

Recall was the other slow step. With the default local reranker, `cross-encoder/ms-marco-MiniLM-L-6-v2` on CPU, one recall over 300 candidates had a median of 4.56 seconds, and reranking alone took 4.39 of them. With OpenRouter's `cohere/rerank-v3.5`, the recall median fell to 0.90 seconds and reranking to 0.72 seconds: an **80.2% reduction** in recall time. That test used three repository queries, two repetitions each per provider, on the live bank. [Hindsight reranker configuration](https://hindsight.vectorize.io/developer/configuration)

Cohere v3.5 bills by search unit, and one 300-candidate call cost four units: $0.004. I then compared reranker models alone, on a fixed set of 300 documents for each of three repository queries, two repetitions each:

| Model | Median time | Median API-reported cost per call | Successful calls |
|---|---:|---:|---:|
| Local MiniLM-L6 on CPU | 4.19 s | $0 | 6/6 |
| `voyageai/rerank-3-lite` | 0.72 s | $0.00105 | 6/6 |
| `cohere/rerank-v3.5` | 0.77 s | $0.00400 | 6/6 |
| `cohere/rerank-4-fast` | 0.79 s | $0.00800 | 6/6 |
| `qwen/qwen3-reranker-8b` | 2.37 s | $0.01626 | 1/6, others HTTP 503 |

Voyage matched Cohere's speed at about a quarter of the cost, so I switched to it. The costs are what OpenRouter reported for these calls, not list prices. Local model load time is excluded; remote times include network setup.

This is not a quality ranking. The repository queries have no labelled answers, and the models ordered the candidates differently. On a small synthetic probe with one known answer, every model that returned a result put that answer first. A recall in the live log later that day scored 300 candidates in 1.27 seconds.

### The reflect decision model

The same TypeSafe Jev model can orchestrate reflect. When it is enabled, the retrieval layers run together in one round, the decision model prunes the evidence, and it judges whether that evidence already answers the question. If it does, reflect skips the main LLM's layer-by-layer tool turns. The main LLM still writes the answer, and a decision-model error falls back to the normal agent turns. [Reflect agent implementation](https://github.com/vectorize-io/hindsight/blob/main/hindsight-api-slim/hindsight_api/engine/reflect/agent.py)

I compared it with the bank setting switched off and on, interleaved, at the high reflect budget: two fixed questions with two repetitions each, so four requests per side.

| Per reflect | Decision model off | Decision model on |
|---|---:|---:|
| Median time | 14.0 s | 5.78 s |
| Median main LLM calls | 5 | 2 |
| Answers passing a basic check | 4/4 | 4/4 |

The median fell by about 59%. One request with the decision model still took 14.8 seconds. Four requests per side is a small sample, the basic check is not a quality grade, and I did not measure the added Jev cost for reflect.

**The scope differs from consolidation.** Consolidation needed a bank to opt in. For reflect, the installed configuration defaults `reflect_use_decision_model` to true: setting up a reflect decision provider turns it on for every bank, and a bank opts out. Knowledge-page refreshes have their own switches, also on by default, and use the same reflect decision route. [Configuration defaults](https://github.com/vectorize-io/hindsight/blob/main/hindsight-api-slim/hindsight_api/config.py) To keep a bank off the Jev route for reflect:

```bash
BANK_ID='coding-agent::example-repo'

curl --fail-with-body --silent --show-error \
  -X PATCH \
  "http://127.0.0.1:9077/v1/default/banks/${BANK_ID}/config" \
  -H 'Content-Type: application/json' \
  -d '{"updates":{"reflect_use_decision_model":false}}'
```

I left it on for all banks. In the daemon log covering the trials and the following day, 19 reflects completed through the decision model with no logged decision-model failure; two of them are the empty Cerebras answers described below. OpenRouter's automatic routing did surface intermittent upstream provider errors. Hindsight retried them; one query-rewrite call still failed after its fourth attempt, and that reflect fell back to searching the question as written and completed.

### Why Cerebras did not stay

Cerebras serves `gpt-oss-120b` quickly, so I also pinned the reflect route to it, with fallbacks off, keeping the Jev and Voyage settings. Three questions, two repetitions each:

| Median reflect time | Automatic routing | Cerebras only |
|---|---:|---:|
| Short factual question A | 13.0 s | 2.97 s |
| Short factual question B | 7.07 s | 2.00 s |
| Broad summary question | 36.1 s | Empty answer, both runs |

On a fixed prompt, Cerebras answered in 0.57 seconds against 3.74 seconds, but its mean API-reported cost per call was about 9.3 times higher: $0.00139 against $0.000148.

The empty answers decided it. The query-rewrite stage classified the summary question as needing no retrieval, and the request returned HTTP 200 with no text. A faster route that silently returns nothing for broad questions is a regression.

One operational trap: the daemon manager wrote the trial routing override into the profile, so it survived the trial. I removed it by hand and restarted. After any temporary trial, read the effective profile before trusting it.

## Update, October 29: replace the rate-limited reranker

Voyage's reranking route began returning HTTP 429. Those retrieval failures caused complete reflect requests to return HTTP 500, even though the daemon and database were healthy. I replaced `voyageai/rerank-3-lite` with **`cohere/rerank-4-fast`**, still using the same OpenRouter endpoint and key. OpenRouter reports Cohere as the upstream provider for the replacement. [Cohere 4 Fast on OpenRouter](https://openrouter.ai/cohere/rerank-4-fast)

Before switching, I tested two fixed synthetic queries, each against 300 documents, with three repetitions per model. Each query had one independently specified correct document:

| Model | Successful calls | Mean successful-call time | API-reported cost per successful call |
|---|---:|---:|---:|
| `cohere/rerank-4-fast` | 6/6 | 0.72 s | $0.006 |
| `cohere/rerank-v3.5` | 6/6 | 1.10 s | $0.003 |
| `qwen/qwen3-reranker-8b` | 4/6; two HTTP 503s | 1.86 s | About $0.0078 |

Every successful response ranked its query's correct document first. Both Cohere models reported three search units per call in this fixture. These costs differ from the October 25 measurements because the documents differ; 300 documents do not guarantee the same billable workload. This is a small availability and ranking check, not a general quality comparison or a sustained-load test.

I kept 4 Fast for its lower latency in this sample. After updating the profile and restarting the daemon, three simple reflect probes all returned the expected answers: **10.84, 8.88, and 6.49 seconds**, averaging **8.74 seconds**. Those are complete reflect times, distinct from the reranker-only times in the table. They verify recovery, not a controlled speedup against the earlier failed requests. An explicit refresh also restored a previously paused knowledge page.

## How I will judge the next change

I kept **Jev, low reasoning, and batch eight** because this run showed a useful operational improvement at a small measured added cost. I kept Jev limited to the bank being tested.

For the next change, I want the same starting observations and fact corpus on both sides, repeated runs, full wall time including decision-model work, and a quality grade alongside cost. That grade should cover duplicates, corrections, temporal updates, and whether the bank's mission is still being followed.

The useful outcome is a memory bank that stays current at an acceptable cost. A shorter model response or a faster first few batches is only one part of that result.

The [measurement summary](/assets/data/2026-10-24-hindsight-consolidation-settings.json) includes the configuration, counters, timing definitions, and limitations used for the calculations in this post, including the October 25 comparisons and the October 29 reranker replacement.
