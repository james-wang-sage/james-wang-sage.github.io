---
layout: post
title: "When AI Cuts Costs, Who Actually Gets the Money?"
date: 2026-11-15
tags: [ai, economics, startups]
description: "A cost saving from AI ends up with shareholders, customers, AI vendors or the remaining staff. Competition in the product, labor and input markets decides the split, and the pie itself can grow."
image: /assets/images/2026-11-15-who-captures-the-gains-from-ai-cost-savings-cover.jpg
---

![A glowing pie on a dark table, its uneven slices drifting toward a stack of coins, shopping bags, a server rack and a lone workstation](/assets/images/2026-11-15-who-captures-the-gains-from-ai-cost-savings-cover.jpg)

I recently watched a video in which the host asked a simple question: when AI lowers a company's costs, who benefits? The host gave four answers:

- If the company keeps its prices and its profit rises, **shareholders** benefit.
- If the lower cost turns into lower prices, **consumers** benefit.
- If nothing visible changes because the savings are spent on AI, **AI providers** benefit.
- If the payroll saved goes to the employees who remain, **the people running the AI** benefit.

I think this is a good framework. It asks the right question, which is not "how many jobs will AI replace" but "who captures the value AI creates". It has one important limit, though: it treats the saving as a fixed pie and asks only how the pie is cut. In this post I reorganize the argument the way an economist would: first as a question of incidence, then market by market, and finally with the pie allowed to grow.

## 1. The question is incidence

Economists ask a version of this question about taxes. When a tax is imposed, who pays it is not decided by who writes the check. It is decided by the markets around the transaction: the side that can least easily walk away ends up bearing more of the burden. That is called **tax incidence**.

An AI cost saving is the same problem in reverse: a positive cost shock instead of a negative one. Where the gain finally lands depends less on the company that adopted AI and more on how much competition and bargaining power exist in the markets it touches.

The central distinction is:

> **Value creation ≠ value capture.** The party that creates value is not necessarily the party that keeps it.

## 2. The four outcomes are one accounting identity

The host's four outcomes are not alternatives. They are the four places a single saving can go, and one AI rollout usually feeds all of them at once.

| What changes | Who benefits | Economic mechanism |
|---|---|---|
| Costs fall, prices stay | Shareholders | Higher profit margin |
| Costs fall, prices fall | Consumers | Larger consumer surplus |
| Spending shifts to AI | AI infrastructure and service providers | Revenue for an input supplier |
| Fewer staff, higher pay for those who stay | Remaining employees | Productivity gains shared with labor |

A hypothetical example. A SaaS company spends $10M a year building and maintaining its product. After adopting AI it:

- saves $4M in labor costs,
- spends $1M on AI APIs and infrastructure,
- cuts prices by $1M to win customers,
- gives its core engineers $500K in raises,
- keeps the remaining $1.5M as extra profit.

The books balance:

```text
$4.0M saved = $1.0M AI vendor + $1.0M customers + $0.5M employees + $1.5M shareholders
```

The interesting question is therefore not *which* group benefits but *how large each share is*. Each share is set in a different market, so the next three sections take them one market at a time.

## 3. Product market: competition decides shareholders versus customers

Whether the saving stays as profit or turns into lower prices depends on how much competition the company faces. Economists call the fraction of a cost change that reaches the price the **pass-through rate**.

- **Strong market power.** A company with a dominant position has little reason to cut prices, even if AI lowers its costs by 80%. In the simplest textbook case, a monopolist facing linear demand with constant marginal cost passes on only half of a cost reduction.
- **Many close competitors.** If a dozen companies sell nearly identical products and all of them adopt the same AI, the cost cut tends to become a price war. Under perfect competition, the long-run price falls to the new cost, and the saving reaches customers.

So the split moves over time:

- **Short run:** early adopters and their shareholders collect the saving as profit.
- **Long run:** in competitive markets, a large share of it ends up with customers.

## 4. Labor market: scarcity, not productivity, sets the raise

Suppose every software engineer becomes five times more productive with AI. Will engineering salaries rise fivefold?

Not necessarily. Wages depend on how scarce a skill is, not only on how productive it is. If AI lets many more people do the same work, software development becomes less scarce, and the gain does not have to flow to the people doing it. The returns tend to go instead to whoever controls what remains scarce: customer relationships, distribution, proprietary data and key business processes. Economists call the extra return on a scarce asset **economic rent**.

The labor market also holds the group the host's framework leaves out: **displaced workers**. If 30 people can now do what 100 did, the other 70 may take a large loss of income. Even if the gains to shareholders and customers exceed that loss, a richer society is not the same as everyone being richer. Economists separate the two: an outcome where the winners *could* compensate the losers (the Kaldor–Hicks criterion) is not one where they *do*.

## 5. Input market: AI vendors need pricing power, and revenue is not profit

The host's third outcome, where all the savings go to AI spending, deserves a closer look.

Say a company saves $10M a year with AI, and its AI provider charges $8M. The company nets only $2M. How long the provider can charge that much depends on the same forces as in Section 3:

- If models are interchangeable and competing on price, the provider cannot sustain an $8M bill for long.
- If a model or platform has capabilities that are hard to replace, the provider can capture more of the value.

The growth of AI usage therefore does not guarantee that AI providers' profits grow with it.

There is a second correction. Even when a company hands its whole payroll saving to an AI provider, the provider gets **revenue**, not necessarily **profit**. GPUs, energy, data centers and inference compute consume much of that revenue, and the value can keep moving upstream to whoever controls the scarce inputs there.

## 6. The pie is not fixed

The biggest limitation of the four-way split is that it only redistributes a saving inside companies that already exist. AI also lowers the cost of starting a company.

Suppose an enterprise SaaS product used to need:

- 20 engineers,
- $5M of initial capital,
- two years of development.

Now a five-person team using AI might need $500K and six months.

That is not an existing company cutting costs. It makes business models viable that were not viable before. New founders can enter the market, build products that did not exist, and take customers from incumbents. Lower entry costs also discipline the incumbents: even a company that faces few competitors today has to price as if new ones could show up. These gains belong to entrepreneurs and their customers, and they do not fit any of the four boxes.

Demand can grow too. When something gets cheaper, people often use more of it. William Stanley Jevons observed in *The Coal Question* (1865) that more efficient steam engines increased Britain's total coal consumption rather than reducing it. If AI makes software, analysis or design far cheaper, the market for them may expand enough that total spending rises.

## 7. Short-run rents, long-run competition

The time dimension ties the sections together. The table below is illustrative, a sketch of how the split tends to shift as a market matures, not a forecast of actual proportions.

| Who | Short run: early-adopter lead | Long run: full competition |
|---|---|---|
| Shareholders | Large share, from temporary margin gains | Shrinks unless protected by a moat |
| Consumers | Small share | Grows as savings turn into lower prices |
| AI providers | Depends on how differentiated the models are | Shrinks if models commoditize |
| Employees | Concentrated in people with scarce skills | Follows scarcity, not productivity |

For investors and founders I think this is the most important judgment of all:

> Who can earn excess profit from AI in the short run, and who can keep it in the long run, are two completely different questions.

If AI cuts the cost of producing code by 90% and every software company has the same AI, code itself stops being a competitive advantage. The long-run winners are more likely to be companies with customers, brand, distribution, network effects, unique data or deep workflow integration.

That is why the AI application layer is worth watching for startups, but "AI cuts the cost of this job by 90%" is not enough to call something a good business. The question to ask is:

> When every competitor can also cut costs by 90%, why will customers still pay me?

## 8. Conclusion

The host's four-way split is a good start. Reorganized as economics, it says:

- AI determines **how much extra value** the economy can create.
- **Competition, scarcity and bargaining power** determine **who gets it**, market by market.
- Lower entry costs and expanding demand can **make the pie larger** in ways the four-way split cannot see.

That is closer to the core of the AI economic shift than the usual debate about how many jobs AI will replace.
