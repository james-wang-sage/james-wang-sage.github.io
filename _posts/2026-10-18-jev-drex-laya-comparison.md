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

All three speak the same API: `POST /v1/systemone` with a `state` and a map of questions. Jev
defined it; Drex and Laya both ship as wire-compatible replacements, so switching between them is
mostly a base-URL change.

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
| Weights | Closed, hosted API only | Open | Open, Apache 2.0 |
| Model | Not disclosed | Qwen3.6-35B-A3B MoE (35B total, ~3B active) | Encoders: ModernBERT-large 421M, mmBERT-base 322M |
| Hardware to self-host | n/a | Large GPU: ~70 GB bf16, ~37 GB Q8 GGUF | Small: a T4, or CPU (193–464 ms) |
| Context | Not published | 128K tokens | 512 (English) / 1,024; up to 8K multilingual |
| Latency | 236–276 ms p50 (independently measured) | ~25 req/s per H100 (vendor) | 33–40 ms on a T4 (vendor) |
| Zero-shot quality | The reference point | Vendor reports ahead of Jev on its Decision Index (61.25 vs 57.96), slightly behind on JevBench (85.7% vs 86.6%) | Weak: 0.362 on typed-decisions, below a 0.461 majority-class baseline |
| After fine-tuning | Not offered | Supported | 0.766 vs Jev's published 0.727 on the same benchmark |
| Many options | Up to 255; 0.870 on Banking77 | Not published | Drops past ~20 options: 0.425 on Banking77 |
| Calibration | Raw ECE 0.144 | Not published | Over-confident until temperature-fitted (0.466 → 0.081) |
| Languages | Not published | Not published | 100+, with a built-in language router |
| Price | ~$0.04–0.06 per 1M input tokens, output free | Hosted pricing not public; self-host free | Free (self-host) |

## Which one when

- **Jev** if you want it to work zero-shot today, hosted, with the most mature SDKs and support for
  large option sets.
- **Drex** if data has to stay in your own environment, you need long documents (128K), and you
  still want good zero-shot answers. Budget for a large GPU.
- **Laya** if the task is narrow and high-volume, latency matters, and you have labeled examples to
  fine-tune on. It is the only one that runs comfortably on CPU or at the edge, and the only one
  with strong multilingual numbers.

In one line: Jev is the hosted default, Drex is a self-hostable large-model take on the same idea,
and Laya is a very small model you train for your own task.

## Read the benchmarks carefully

Almost none of these numbers are directly comparable:

- **Drex's** figures are self-reported by Nace.
- **Laya's** comparisons against Jev use Jev numbers published by third parties; the model card
  says they were never measured by the Laya team. The widely quoted "beats Jev" result is for a
  checkpoint fine-tuned on that benchmark's own training split; the base checkpoint scores below
  majority-class guessing on it.
- The one independently measured figure in the table is **Jev's latency**.

Because the three share a protocol, the honest way to choose is cheap: take 50–100 real decisions
from your own workload, run all three, and compare. Each model also has documented weak spots worth
testing for: injected text shifting Jev's probabilities, Laya's `score` questions and its `noul`
following option labels instead of the state.

## Sources

- [Drex](https://www.nace.ai/drex)
- [Laya model card](https://huggingface.co/convaiinnovations/laya) and
  [laya-typed-decisions](https://huggingface.co/convaiinnovations/laya-typed-decisions)
- [TypeSafe Jev explained (Requesty)](https://www.requesty.ai/blog/typesafe-jev-explained)
- [Jev API listing (AI/ML API)](https://aimlapi.com/models/typesafe-jev-latest)
- [jev-benchmarks](https://github.com/AbdelStark/jev-benchmarks) and
  [decision-model-benchmark](https://github.com/nibzard/decision-model-benchmark)
