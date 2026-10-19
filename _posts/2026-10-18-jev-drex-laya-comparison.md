---
layout: post
title: "Jev, Drex, and Laya: Three System One Decision Models Compared"
date: 2026-10-18
tags: [ai, llm, decision-models]
image: /assets/images/2026-10-18-jev-drex-laya-cover.jpg
---

![One input split across three decision engines, converging on typed answers](/assets/images/2026-10-18-jev-drex-laya-cover.jpg)

A new kind of model showed up in 2026: the **System One decision model**. Instead of writing an
answer token by token, it reads a piece of text (the *state*) plus a set of typed questions, and
returns a probability for each option in a single pass. There is nothing to parse and no free-form
output to go wrong.

Three of them are worth knowing about: **Jev** from TypeSafe, **Drex** from Nace, and **Laya**
from ConvAI. This post compares them as of October 2026.

## One protocol, three models

All three speak the same API: `POST /v1/systemone` with a `state` and a map of questions. It is
TypeSafe's API, and Jev was the first model on it; Drex and Laya both ship as wire-compatible
replacements, so switching between them is mostly a base-URL change.

They also share the three question types:

| Type | Asks | Returns |
|---|---|---|
| `choice` | Pick one of these named options | The pick, a confidence, and a distribution |
| `noul` | Is this proposition true? | P(true) |
| `score` | Where does this sit on an ordered scale? | Expected level and a distribution |

Typical uses: routing a ticket, classifying an email, checking an extracted field, gating an
action behind a guardrail. Code keeps the workflow, permissions, and arithmetic; the model supplies
the judgment.

## Side by side

| | **Jev 1.13** (TypeSafe) | **Drex 2.0** (Nace) | **Laya** (ConvAI) |
|---|---|---|---|
| Weights | Closed | Open, under Open RAIL-M (use restrictions; not OSI open source) | Open, Apache 2.0 |
| Hosted API | Yes (`api.typesafe.ai`; also via OpenRouter) | Yes (`console.nace.ai`) | No; self-host only (`laya-serve`), plus a free demo Space |
| Model | Not disclosed | Qwen3.6-35B-A3B MoE (35B total, ~3B active) | Encoders: ModernBERT-large 421M, mmBERT-base 322M |
| Hardware to self-host | n/a | Large GPU: ~70 GB bf16, ~37 GB Q8 GGUF | Small: a T4, or CPU (193–464 ms) |
| Context | 64K per request / 32K per question; 262K with the long-context header | 128K state (hosted); self-host defaults to 16K, up to 128K | 512 (English) / 1,024; up to 8K multilingual |
| Latency | 236–316 ms p50 (independently measured) | ~25 req/s per H100 (vendor) | 33–40 ms on a T4 (vendor) |
| Zero-shot quality | The reference point | Vendor reports ahead of Jev on its Decision Index (61.25 vs 57.96), slightly behind on JevBench (85.7% vs 86.6%) | Weak: 0.362 on typed-decisions, below a 0.461 majority-class baseline |
| After fine-tuning | Not offered; you steer it through state and instructions | Offered as a vendor service | 0.766 vs a third-party-published Jev 0.727 on the same benchmark |
| Many options | Up to 255; 79.2% on the full Banking77 test (77 labels) | Up to 255 | Drops past ~20 options at default settings: 0.425 on Banking77 |
| Calibration | No vendor figure; independent ECE 0.02–0.35 depending on the task | No figures published | Over-confident until temperature-fitted (0.466 → 0.081) |
| Languages | English primary; others, including CJK, handled less accurately | No list published | 100+ (45 of 51 measured languages usable), with a built-in language router |
| Price | $0.042 per 1M input tokens, output free | Hosted: $0.06 per 1M input tokens (v2.0), output free, $25 signup credit. Self-host: royalty-free for personal or research use, or organizations under $1M revenue and funding; others need a commercial license | Free (self-host) |

Jev 1.14 shipped as a preview (`jev-preview`) on October 14; `jev-latest` still points to 1.13.

## Which one when

- **Jev** if you want it to work zero-shot today with the most mature SDKs and docs, and a
  hosted-only service is fine.
- **Drex** if you want both doors open: a hosted API priced close to Jev today, and open weights you
  can move in-house later if data has to stay in your own environment (check the license if your
  organization is above its $1M thresholds). It also has the largest default context (128K).
  Self-hosting it takes a large GPU.
- **Laya** if the task is narrow and high-volume, latency matters, and you have labeled examples to
  fine-tune on. It is the only one that runs comfortably on CPU or at the edge, and the only one
  that publishes multilingual results.

In one line: Jev is the hosted default, Drex offers the same idea both hosted and as open weights,
and Laya is a very small model you train and run yourself.

## Read the benchmarks carefully

Almost none of these numbers are directly comparable:

- **Drex's** figures are self-reported by Nace.
- **Laya's** comparisons against Jev use Jev numbers published by third parties; the model card
  says they were never measured by the Laya team. The widely quoted "beats Jev" result is for a
  checkpoint fine-tuned on that benchmark's own training split; the base checkpoint scores below
  majority-class guessing on it.
- **Jev's** latency, Banking77 and calibration figures come from two independent benchmark repos;
  TypeSafe itself publishes no accuracy or calibration numbers.

Because the three share a protocol, the honest way to choose is cheap: take 50–100 real decisions
from your own workload, run all three, and compare. Each model also has documented weak spots worth
testing for: injected text shifting Jev's probabilities, Laya's `score` questions and its `noul`
following option labels instead of the state.

## Sources

- [Jev models, context and pricing](https://docs.typesafe.ai/models) and
  [API reference](https://docs.typesafe.ai/api)
- [Drex](https://www.nace.ai/drex), its [pricing](https://console.nace.ai/docs/drex/reference/pricing),
  [limits](https://console.nace.ai/docs/drex/reference/limits) and
  [repo](https://github.com/nace-ai/drex-decision-models)
- [Laya model card](https://huggingface.co/convaiinnovations/laya) and
  [laya-typed-decisions](https://huggingface.co/convaiinnovations/laya-typed-decisions)
- [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) and
  [decision-model-benchmark](https://github.com/nibzard/decision-model-benchmark)
