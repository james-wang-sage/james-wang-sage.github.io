---
layout: post
title: "Choosing Long-Term Memory for Hermes: 10 Options, Trade-offs, and Cloud Pricing"
date: 2026-10-23
tags: [ai, agents, opensource, programming]
description: "Compare 10 Hermes memory options across local storage, user modeling, knowledge graphs, self-hosting, and cloud pricing."
image: /assets/images/2026-10-23-choosing-long-term-memory-for-hermes-cover.jpg
---

![Local files, a knowledge graph, and a cloud memory archive connected by shared context](/assets/images/2026-10-23-choosing-long-term-memory-for-hermes-cover.jpg)

Choosing Long-Term Memory for an AI agent starts with a practical question: what should the agent remember, and how will you know that it remembered correctly?

Hermes offers several approaches: curated Markdown files, a local fact database, user-modeling services, knowledge graphs, and directory-based context stores. They solve different problems and charge for different units of work.

This guide compares **10 options**, including Hermes's built-in memory, with their strengths, trade-offs, integration paths, and cloud pricing. **The pricing snapshot is dated October 23, 2026. All amounts are in US dollars.** Annual commitments and annualized monthly prices are labeled explicitly.

This is a documentation-based comparison, not a hands-on benchmark using identical tasks. Vendor accuracy scores use different models, datasets, and cost assumptions, so they are not treated as a common leaderboard.

## Start with the memory you actually need

Persistent memory can mean several things:

- **Personal facts and preferences:** time zone, communication style, and long-term goals.
- **Project decisions and lessons:** architectural choices, debugging findings, and working conventions.
- **History and change:** when a preference changed or why a decision was revised.
- **External knowledge:** documents, websites, email, and shared team material.

A small preference store and a traceable engineering knowledge base need different systems. Write down the questions you want the agent to answer before choosing the backend.

## The 10 options at a glance

| Option | Main use | Deployment | Cloud entry point |
|---|---|---|---|
| Hermes built-in memory | Curated facts, preferences, conversation lookup | Local | No separate memory-service fee |
| Honcho | User modeling and reasoning-based recall | Cloud or open-source self-hosting | $2 per million ingestion tokens; reasoning extra |
| OpenViking | Directory-based knowledge and tiered loading | Cloud or self-hosted | Managed service advertises the first 50 files free; exact usage rates require confirmation |
| Mem0 | Automatic fact extraction and maintenance | Cloud, self-hosted server, or OSS | Free; Starter $19/month |
| Hindsight | Relationships, time, and synthesis across memories | Cloud or open-source self-hosting | Prepaid usage |
| Holographic | Lightweight local fact storage | Local | No additional model calls by default |
| RetainDB | Managed memory, hybrid search, and files | Cloud | Free; Builder $9/month |
| ByteRover | Project knowledge and team synchronization; distinguish legacy provider from V4 skill | Local-first, optional cloud sync | Current cloud plans: free; Pro $15/month billed annually |
| Supermemory | User memory, document retrieval, and connectors | Cloud or licensed local server | Free; Pro $19/month |
| Memori | Tool-aware memory and production governance | OSS or managed deployments | Free allowance; production Team from $60,000/year |

Hermes allows **one active external memory provider at a time**, while built-in memory remains active. Additional MCP tools can coexist, but that does not automatically give them another provider's background synchronization and recall lifecycle. [Hermes integration documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers/)

## 1. Hermes built-in memory

Hermes stores curated facts and preferences in MEMORY.md and USER.md. Its session_search tool can retrieve earlier conversations. [Official documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory/)

**Pros**

- Human-readable files are easy to inspect, edit, back up, and migrate.
- No additional memory account, API key, or service dependency is required.
- It provides a straightforward baseline for stable project conventions and personal facts.
- It remains available alongside an external provider.

**Cons**

- Resident memory is bounded and needs curation as information accumulates.
- Files alone do not provide sophisticated relationship modeling or fact reconciliation.
- Sharing memory with other coding tools requires an additional integration.
- Historical recall still depends on the agent choosing useful queries.

**Pricing:** There is no separate SaaS fee. Injected memories still occupy the main model's context and incur its normal token costs.

**Best fit:** Start here when a small set of stable facts and searchable conversation history may already solve the problem.

## 2. Honcho

[Honcho](https://honcho.dev/) focuses on understanding users over time. It maintains representations of users and agents and offers reasoning at several depths. It has a dedicated [Hermes integration](https://honcho.dev/hermes) and an [open-source core](https://github.com/plastic-labs/honcho).

**Pros**

- A good architectural match for persistent preferences, goals, and user modeling.
- Ordinary context retrieval is separate from deeper reasoning.
- Multiple tools can connect to a shared memory layer.
- Self-hosting gives control over the infrastructure and stored memory.

**Cons**

- Inferred user attributes require review; they are not equivalent to explicitly confirmed facts.
- Frequent deep reasoning can dominate the bill.
- Refresh frequency and reasoning depth need deliberate configuration.
- Self-hosting transfers model provisioning and operations to you.

### Cloud pricing

| Operation | Published rate |
|---|---:|
| Ingestion and processing | $2 per million input tokens |
| Context retrieval | Listed as unlimited |
| Background Dreaming | Included |
| Minimal reasoning | $0.001/query |
| Low reasoning | $0.01/query |
| Medium reasoning | $0.05/query |
| High reasoning | $0.10/query |
| Max reasoning | $0.50/query |

The current personal-memory page states that new accounts receive $5 in credits, with another $5 each billing period after adding a payment method. Recurring credits do not accumulate. This uses the live page rather than older cached signup offers. [Rates](https://honcho.dev/), [credit terms](https://honcho.dev/ai-memory)

Unlimited context retrieval does not eliminate the main agent's cost of reading that context.

**Best fit:** A personal assistant that should maintain a coherent understanding of the same user across sessions and tools.

## 3. OpenViking

[OpenViking](https://github.com/volcengine/OpenViking) organizes context as a virtual filesystem under viking://. Agents can browse directories and load L0 abstracts, L1 overviews, and L2 source content progressively.

**Pros**

- The knowledge structure is visible and navigable.
- Project or directory scope can narrow retrieval.
- Summary-first loading helps control how much material reaches the agent.
- Archived sessions and extracted Markdown memories can be inspected.

**Cons**

- Self-hosting requires running a service and configuring its models, adding operational work.
- Generated summaries and retrieval planning can introduce errors.
- Directory design may be unnecessary overhead for a small preference store.
- Product capabilities and the subset exposed by the Hermes integration should be evaluated separately.

**Cloud pricing:** OpenViking offers a managed service on Volcengine alongside self-hosting. Its enterprise page advertises the first 50 files free and hourly pay-as-you-go; exact usage rates should be checked in the service console. Self-managed enterprise deployment is custom-priced. Self-hosting costs depend on compute, storage, embeddings, and the configured language or multimodal models. [Deployment options](https://docs.openviking.ai/en/guides/03-deployment), [enterprise offering](https://openviking.ai/enterprise)

**Best fit:** Larger, clearly structured knowledge collections where inspecting and maintaining the organization matters. [Website](https://www.openviking.ai/), [Hermes integration](https://docs.openviking.ai/en/agent-integrations/05-hermes)

## 4. Mem0

[Mem0](https://mem0.ai/) offers automatic fact extraction and memory CRUD operations, with a managed platform and an [open-source implementation](https://github.com/mem0ai/mem0).

**Pros**

- A direct API for adding user-level memory to an existing agent.
- Cloud, self-hosted, and in-process OSS deployment choices.
- Explicit free and entry-level quotas make an initial trial easier to budget.
- Pro adds graph memory and Dream consolidation.

**Cons**

- Extraction can omit context or preserve inaccurate or outdated information, so extracted memories still need review.
- Lower tiers provide substantially fewer retrieval requests than add requests.
- Per-turn retrieval can exhaust the retrieval quota first.
- Pro represents a substantial price increase; its capabilities should not be assumed to exist in Starter.
- OSS deployments leave you responsible for the configured models and storage; defaults are provided and can be overridden.

### Cloud pricing

| Plan | Monthly price | Add requests/month | Retrieval requests/month | Projects |
|---|---:|---:|---:|---|
| Hobby | $0 | 10,000 | 1,000 | 1 |
| Starter | $19 | 50,000 | 5,000 | 1 |
| Pro | $249 | 500,000 | 50,000 | Unlimited |
| Enterprise | Custom | Listed as unlimited | Listed as unlimited | Unlimited |

Pro includes graph memory, Dream, analytics, and private Slack support. Enterprise adds features such as SLA support, on-premises deployment, audit logs, and SSO. [Current pricing](https://mem0.ai/pricing)

**Best fit:** Managed fact extraction with a simple API, provided that the retrieval quota matches the intended agent loop.

## 5. Hindsight

[Hindsight](https://hindsight.vectorize.io/) separates retain, recall, and reflect: storing information, retrieving it, and synthesizing answers across memories. It also models entities, relationships, temporal changes, and mental models. [Open-source project](https://github.com/vectorize-io/hindsight)

**Pros**

- A strong architectural match for questions about how a project or decision evolved.
- Explicit operations distinguish retrieval from synthesis.
- Cloud includes memory-side LLM, embedding, and reranking models.
- An [upstream-maintained Hermes integration](https://hindsight.vectorize.io/sdks/integrations/hermes) is available.

**Cons**

- Capturing full conversations and tool calls can increase ingestion volume.
- Reflection, model refreshes, and long-term storage have separate meters.
- Automatically refreshed knowledge pages can generate charges without a manual refresh.
- Self-hosting requires operating databases, models, and upgrades.
- Synthesized conclusions still need supporting evidence.

### Cloud pricing

| Operation | Rate |
|---|---:|
| Retain | $10 per million input tokens |
| Import or restore from an export archive | $5 per million input tokens; no new fact extraction |
| Recall | $0.75 per million output tokens |
| Reflect | $0.05/call |
| Retrieve Model or read a knowledge page | $0.25 per million output tokens |
| Refresh Model or create/update a knowledge page | $0.05/call |
| Iris enhanced file extraction | $7.50 per million output tokens, plus normal retain |
| Memory storage after 30 days | $0.25 per million tokens/month, accrued daily |

Cloud uses prepaid credits at $1 per credit. The homepage advertises $5 in initial credits for GitHub signup; this is not a recurring monthly allowance. Standard text extraction avoids the additional Iris charge, but retaining extracted content still costs money. [Billing details](https://docs.hindsight.vectorize.io/cloud/billing/), [what Cloud includes](https://hindsight.vectorize.io/cloud-enterprise/hindsight-cloud)

**Best fit:** Projects that need temporal context, entity relationships, and synthesis across multiple memories.

## 6. Holographic

[Holographic](https://github.com/itpartypattaya/hermes-plugin-holographic) is a local SQLite fact store combining FTS5, entity resolution, trust scoring, and holographic reduced representation retrieval. The current plugin is maintained by a community maintainer.

**Pros**

- No API key, network access, or additional model calls by default.
- Fact versions, provenance, and correction operations support inspection.
- Hermes backup integration and SQLite-aware backups support local recovery.
- Optional embedding-based semantic search can use a remote API or a local OpenAI-compatible endpoint.

**Cons**

- Keyword and HRR retrieval should not be equated with general language-model semantic understanding.
- Large paraphrases, implicit relationships, and complex synthesis need practical evaluation.
- Fact organization and keywords affect recall quality.
- Remote embeddings change the data flow and may add provider charges; local embedding endpoints can keep the processing local.
- Community-maintained compatibility is worth monitoring.

**Pricing:** The default local path has no separate memory-model service bill. Optional remote embeddings follow the chosen provider's pricing; local embedding endpoints need not incur an API fee. Main-agent tokens remain separate. No managed-service quote was confirmed in this review. [Current capabilities](https://github.com/itpartypattaya/hermes-plugin-holographic), [Hermes catalog](https://hermes-agent.nousresearch.com/docs/plugins/holographic)

**Best fit:** A modest local store of preferences, facts, and explicit decisions with minimal additional infrastructure.

## 7. RetainDB

[RetainDB](https://www.retaindb.com/) combines managed memory, hybrid retrieval, file operations, and project features.

**Pros**

- Writes and context reads have separate, visible quotas.
- The entry paid tier is inexpensive.
- Memory, file knowledge, and collaboration can live in one service.
- Higher plans add delta compression and larger team limits.

**Cons**

- The standard route depends on a hosted service.
- Delta Compression is not included in every tier.
- The Hermes documentation identifies its standalone provider repository as needing a maintainer. That is an integration-maintenance issue, not a claim that the RetainDB service is unmaintained.
- Older documentation and current pricing can differ.

### Cloud pricing

| Plan | Monthly price | Writes/month | Context reads/month | Scope |
|---|---:|---:|---:|---|
| Starter Free | $0 | 20,000 | 5,000 | 1 project, 1 API key |
| Builder | $9 | 75,000 | 15,000 | 3 projects, 5 keys, 3 seats, Knowledge Graph |
| Pro | $29 | 250,000 | 75,000 | 10 projects, 20 keys, 10 seats, Delta Compression |
| Scale | $99 | 1,000,000 | 300,000 | Unlimited projects and keys, 50 seats |
| Enterprise | Custom | Listed as unlimited | Listed as unlimited | Contract-specific |

The pricing page also advertises 20% off annual billing. Older Hermes material lists $20/month; this table uses the current vendor pricing page. Overage behavior should be checked at checkout. [Pricing](https://www.retaindb.com/pricing), [Hermes maintenance note](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory-providers.md#providers-moving-to-the-plugin-catalog)

**Best fit:** Budget-conscious managed workloads with substantial read/write quotas, after checking Hermes integration compatibility.

## 8. ByteRover

Hermes's documented [ByteRover](https://www.byterover.dev/) provider uses the legacy brv CLI and a local hierarchical knowledge tree. Current ByteRover V4 documentation instead describes Desktop, spaces, and a published agent skill; its setup guide removes the old Hermes provider before V4 setup. Both routes target project decisions, debugging lessons, and reusable engineering knowledge, but their integration details should be evaluated separately. [V4 overview](https://docs.byterover.dev/v4/overview.md), [agent setup and migration](https://docs.byterover.dev/v4/agents/overview.md)

**Pros**

- Knowledge is readable and maintainable.
- Selected material can be shared across devices and teams.
- Recall sources can be inspected.
- The legacy Hermes provider documents extraction before context compression discards insights.

**Cons**

- Duplicate and outdated knowledge still needs curation.
- The legacy provider's LLM-driven search adds processing and can add model cost, depending on configuration.
- The legacy CLI and the current Desktop/skill route each require client setup and synchronization management.
- Hermes lists the standalone provider repository as needing a maintainer; the product and integration have distinct maintenance considerations.

### Cloud pricing

| Plan | Price | Main scope |
|---|---|---|
| Legacy local provider | Listed as free in Hermes documentation | Local tree; model costs depend on configuration |
| Free cloud sync | $0 | 100 context files, device sync, team sharing |
| Pro | **$15/month billed annually** | Unlimited context files, priority support |
| Enterprise | Custom | SSO/SAML, RBAC, on-premises options |

The cloud rows describe the current ByteRover offering, not an entitlement guarantee for the legacy Hermes provider. The accessible current page explicitly labels $15 as billed yearly. This review did not reliably confirm Pro's monthly-billing price or the seat-billing basis. Older retrieval-based price tables should not be substituted for the current file-based plans. [Current pricing](https://www.byterover.dev/pricing), [Hermes documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory-providers/)

**Best fit:** Coding agents that should share inspectable project knowledge with selective team synchronization.

## 9. Supermemory

[Supermemory](https://supermemory.ai/) combines personal memory with SuperRAG document retrieval and connectors for external sources. Its [Hermes plugin](https://github.com/supermemoryai/hermes-supermemory) is maintained by the vendor.

**Pros**

- One integration ecosystem can cover personal memory and external knowledge.
- Supported updates under the same customId within the same organization bill only newly added content on the token-ingestion meter.
- Connectors can reduce the work of ingesting documents and cloud sources.
- A local server is available for single-machine workflows.

**Cons**

- Credits, Memory tokens, SuperRAG tokens, queries, and operations are separate meters.
- Document identity changes or full replacements can incur fresh ingestion charges.
- Advanced PDF extraction and some connectors require higher plans.
- The current local server binary comes from a non-public codebase and is free only within its lite license limit. Open-source SDKs do not make the complete server open source.
- Local extraction models and available integrations differ from the hosted service.

### Cloud plans

| Plan | Monthly subscription | Monthly included credits | Main differences |
|---|---:|---:|---|
| Free | $0 | $5 | APIs, plugins, 1 seat |
| Pro | $19 | $20 | Auto top-up, 3 seats |
| Max | $100 | $130 | More credits, Gmail connector |
| Scale | $399 | $600 | Advanced PDF, S3, crawler, unlimited seats |
| Enterprise | Custom | Contract-specific | Dedicated support and deployment options |

### Usage rates

| Meter | Rate |
|---|---:|
| Memory plain text | $5 per million SM tokens |
| Memory rich content | $10 per million SM tokens |
| SuperRAG text | $1 per million SM tokens |
| SuperRAG images, PDFs, audio, and video | $2 per million SM tokens |
| Search and traversal | $5 per million queries |
| Operations | $100 per million operations |

Subscription credits reset monthly; purchased top-up credits do not expire. An auto-top-up purchase limit is not a hard cap on the total invoice. Workflows can use multiple meters, so budget against the endpoints actually called. [Plans and rates](https://supermemory.ai/pricing.md)

The local server needs your extraction model. Its default embedding model is English-oriented, so multilingual workloads should evaluate alternatives. The reviewed licensing pages did not specify a numerical lite limit; it should not be described as unlimited free usage. [Local deployment](https://supermemory.ai/docs/self-hosting/overview), [Local versus Enterprise](https://supermemory.ai/docs/self-hosting/local-vs-enterprise)

**Best fit:** Workloads combining memory with documents, websites, or cloud connectors, with room for more detailed usage accounting.

## 10. Memori

[Memori](https://memorilabs.ai/) emphasizes execution traces, structured recall, and production governance. Hermes uses an externally supplied hermes-memori CLI/provider integration.

**Pros**

- Tool-aware memory fits production agent workflows.
- Production plans include access control, audit logging, observability, and memory pooling.
- Deployment choices cover managed multi-tenant, managed single-tenant, customer VPC, and on-premises arrangements.
- Free Cloud and OSS routes allow smaller initial experiments.

**Cons**

- Paid production plans are priced primarily for enterprises.
- OSS, free Cloud, and production contracts are different offers.
- Counts of memories created or recalled are not directly comparable to another provider's API-request quotas.
- Free Cloud has monthly creation and recall limits; production plans are a separate purchase.

### Cloud pricing

| Plan | Published price | Scope |
|---|---|---|
| OSS | Software free | Bring your database, models, and infrastructure |
| Cloud Free | $0 | 5,000 memories created/month; 15,000 memories recalled/month |
| Team | **From $60,000/year** | One production agent, managed multi-tenant |
| Business | **From $150,000/year** | Multiple production agents, managed single-tenant |
| Enterprise | Custom | Customer VPC or on-premises, dedicated infrastructure |

Team and Business annualize to $5,000 and $12,500 per month respectively. **Those are annual-contract equivalents, not published monthly purchase prices.** Production plans list unlimited memories, but agent and deployment scope still differ. The Cloud FAQ and dashboard document the free allowances as monthly. [Pricing](https://memorilabs.ai/pricing), [Cloud FAQ](https://memorilabs.ai/docs/memori-cloud/support/faq/), [Hermes integration](https://github.com/NousResearch/hermes-agent/blob/main/website/docs/user-guide/features/memory-providers.md#memori)

**Best fit:** Organizations buying production governance and vendor support rather than a low-cost personal memory subscription.

## Budget for the whole memory loop

The memory provider's price is only part of the bill.

**Main-agent tokens:** A free or inexpensive recall operation can still return a large context that the main model must process.

**Background work:** Extraction, reconciliation, reasoning, refreshes, and consolidation may run behind a simple interaction.

**Operations and migration:** Self-hosting requires backups, upgrades, model configuration, and troubleshooting. Changing a service URL does not necessarily migrate stored memories.

A useful budget is:

    Total cost = memory subscription or metered usage
               + extraction, retrieval, and embedding costs not included
               + main-agent tokens used to read recalled context
               + self-hosted infrastructure and maintenance

Requests, tokens, synchronized files, and generated memories measure different things. One conversation is not necessarily one billable operation.

## A practical shortlist

These are architectural matches, not measured performance rankings.

| Primary requirement | Start by comparing |
|---|---|
| Minimal maintenance | Hermes built-in memory |
| Lightweight local facts | Holographic |
| Inspectable project knowledge shared across tools | ByteRover |
| Simple managed fact API | Mem0 |
| Long-term user understanding | Honcho |
| Temporal context and synthesis across memories | Hindsight |
| Navigable, directory-based knowledge | OpenViking |
| Memory plus documents and connectors | Supermemory |
| Low entry price with substantial hosted quotas | RetainDB, with integration validation |
| Production governance and vendor delivery | Memori and relevant enterprise offerings |

Keep built-in memory as a common baseline. Ask each candidate the same questions: did an old preference update correctly, can a decision be traced to its source, does information leak between projects, and does a deleted memory reappear?

Record ingestion, retrieval, background operations, and main-model tokens for a complete session. That connects recall behavior to cost and gives a more useful decision than a cross-vendor accuracy chart.

---

**Snapshot limitations:** Pricing and features were checked on October 23, 2026. ByteRover's monthly-billing price, Supermemory's numerical lite limit, and OpenViking's exact managed-service usage rates were not confirmed. Check the linked official documentation and checkout pages before purchasing or deploying.
