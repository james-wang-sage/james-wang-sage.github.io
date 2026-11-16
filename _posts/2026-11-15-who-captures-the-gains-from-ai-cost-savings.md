---
layout: post
title: "When AI Cuts Costs, Who Actually Gets the Money?"
date: 2026-11-15
tags: [ai, economics, startups, investing, careers, policy]
description: "A cost saving from AI ends up with shareholders, customers, AI vendors or the remaining staff. Competition in the product, labor and input markets decides the split, and the pie itself can grow. Plus the debate over AI taxes and public equity, and what it all means for long-term investors and for your career."
image: /assets/images/2026-11-15-who-captures-the-gains-from-ai-cost-savings-cover.jpg
---

![A glowing pie on a dark table, its uneven slices drifting toward a stack of coins, shopping bags, a server rack and a lone workstation](/assets/images/2026-11-15-who-captures-the-gains-from-ai-cost-savings-cover.jpg)

I recently watched a video in which the host asked a simple question: when AI lowers a company's costs, who benefits? The host gave four answers:

- If the company keeps its prices and its profit rises, **shareholders** benefit.
- If the lower cost turns into lower prices, **consumers** benefit.
- If nothing visible changes because the savings are spent on AI, **AI providers** benefit.
- If the payroll saved goes to the employees who remain, **the people running the AI** benefit.

I think this is a good framework. It asks the right question, which is not "how many jobs will AI replace" but "who captures the value AI creates". It has one important limit, though: it treats the saving as a fixed pie and asks only how the pie is cut. Below I examine the split across the product, labor and input markets, then let the pie grow, look at proposals to tax AI companies or give the public a stake in them, and finally draw out what it means for long-term investors and for careers.

## 1. The question is incidence

Economists ask a version of this question about taxes. When a tax is imposed, who pays it is not decided by who writes the check. It is decided by the markets around the transaction: the side that can least easily walk away ends up bearing more of the burden. That is called **tax incidence**.

AI-driven cost reductions raise the same question from the other side: who ultimately receives the benefit? The answer depends less on the company that adopted AI and more on how much competition and bargaining power exist in the markets it touches.

The central distinction is:

> **Value creation ≠ value capture.** The party that creates value is not necessarily the party that keeps it.

## 2. Four channels, one budget

The host's four outcomes are not alternatives. They are four channels through which a single saving can flow, and one AI rollout usually feeds all of them at once.

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

Holding sales volume, product quality and other costs constant, the year's cash-flow changes reconcile as follows:

```text
$4.0M saved = $1.0M AI vendor + $1.0M customers + $0.5M employees + $1.5M shareholders
```

This is a budget, not a welfare calculation: it ignores new customers, better products and everything else that changes when a company adopts AI. Still, it makes the point. The interesting question is not *which* group benefits but *how large each share is*. Each share is set in a different market, so the next three sections take them one market at a time.

## 3. Product market: competition decides shareholders versus customers

Whether the saving stays as profit or turns into lower prices depends first on what kind of cost AI reduced. Economists call the fraction of a cost change that reaches the price the **pass-through rate**, and it works differently for two kinds of cost:

- **Marginal cost**, the cost of serving one more customer: support tickets, document processing, per-unit labor. A profit-maximizing company sets its price with marginal cost in mind, so a cut here can show up in prices fairly directly.
- **Fixed cost**, the cost that does not grow with sales: most of the engineering in the SaaS example above. A lower fixed cost does not change the profit-maximizing price for a given set of competitors. It reaches customers indirectly, by making it cheaper for new competitors to enter, which pushes prices down over time.

How much of a marginal-cost cut reaches the price then depends on competition and on the shape of demand:

- **Strong market power.** Nothing forces a dominant company to cut prices; it cuts only as far as maximizing its own profit requires. In the simplest textbook case, a monopolist facing linear demand with constant marginal cost lowers its unit price by half of the cost reduction. That result depends on the linear demand curve: with other demand shapes, a monopolist can pass on less, or even more than the full cost change.
- **Many close competitors.** If a dozen companies sell nearly identical products and all of them adopt the same AI, the cost cut tends to become a price war. Under perfect competition, with free entry, the same technology available to everyone and industry costs that do not rise as output expands, the long-run price falls to the new cost, and the saving reaches customers.

So the split tends to move over time:

- **Short run:** early adopters and their shareholders collect the saving as profit.
- **Long run:** in markets where entry is open and the technology spreads, a large share of it ends up with customers.

## 4. Labor market: productivity gains do not automatically become raises

Suppose every software engineer becomes five times more productive with AI. Will engineering salaries rise fivefold?

Not necessarily. Productivity matters, but wages also depend on how much demand there is for the work, how many people can supply it, how easily AI substitutes for it, and how much bargaining power workers have. If AI lets many more people do the same work, the supply of software development effectively rises, and the gain does not have to flow to the people doing it. The returns tend to go instead to whoever controls what remains scarce: customer relationships, distribution, proprietary data and key business processes. Economists call the return above what is needed to keep a resource in its current use **economic rent**.

The framework also leaves out **displaced workers**. If 30 people can now do what 100 did, the other 70 may take a large loss of income. Even if the gains to shareholders and customers exceed that loss, a richer society is not the same as everyone being richer. Economists separate the two: an outcome where the winners *could* compensate the losers (the Kaldor–Hicks criterion) is not one where they *do*.

## 5. Input market: AI vendors need pricing power, and revenue is not profit

The host's third outcome, where all the savings go to AI spending, deserves a closer look.

Say a company saves $10M a year with AI, and its AI provider charges $8M. The company nets only $2M. Whether that bill holds up depends on two things:

- **The provider's markup.** If models are interchangeable and competing on price, competition pushes the price down toward the provider's own cost. If a model or platform has capabilities that are hard to replace, the provider can charge well above cost and capture more of the value.
- **The usage and the cost of serving it.** Even in a fully competitive market, a large bill can persist if the workload is heavy and expensive to run. Competition limits the markup, not the total.

The growth of AI usage therefore does not guarantee that AI providers' profits grow with it.

There is a second correction. Even when a company hands its whole payroll saving to an AI provider, the provider gets **revenue**, not necessarily **profit**. GPUs, energy, data centers and inference compute consume much of that revenue, and the value can keep moving upstream to whoever controls the scarce inputs there.

## 6. The pie is not fixed

The biggest limitation of the four-way split is that it only redistributes a saving inside companies that already exist. AI may also lower the cost of starting a company.

Suppose an enterprise SaaS product used to need:

- 20 engineers,
- $5M of initial capital,
- two years of development.

Now a five-person team using AI might need $500K and six months.

That is not an existing company cutting costs. It makes business models viable that were not viable before. New founders can enter the market, build products that did not exist, and take customers from incumbents. Lower entry costs also discipline the incumbents: even a company that faces few competitors today has to price as if new ones could show up. The people who benefit are still owners and customers, but these gains come from new activity rather than from splitting a saving inside an incumbent firm, which is what the four-way split cannot see.

Demand can grow too. When something gets cheaper, people often use more of it. In *The Coal Question* (1865), William Stanley Jevons argued that more efficient steam engines had increased Britain's total coal consumption rather than reducing it. Greater usage does not necessarily mean greater spending, though: total spending on AI-made software, analysis or design rises only if demand is elastic enough that usage grows proportionally more than the price falls.

## 7. Short-run rents, long-run competition

The time dimension ties the sections together. The table below is illustrative, a sketch of how the split tends to shift as a market matures, not a forecast of actual proportions. The later column assumes adoption spreads and entry stays open; neither is guaranteed.

| Who | Short run: early-adopter lead | Later, if adoption spreads and entry stays open |
|---|---|---|
| Shareholders | Large share, from temporary margin gains | Shrinks, except where a moat keeps rivals out |
| Consumers | Small share | Grows as savings turn into lower prices |
| AI providers | Depends on how differentiated the models are | Revenue may keep growing; margins shrink if models commoditize |
| Employees | Concentrated in people with hard-to-supply skills | Follows bargaining power and how hard the skill is to supply |

For investors and founders I think this is the most important judgment of all:

> Who can earn excess profit from AI in the short run, and who can keep it in the long run, are two completely different questions.

If AI cuts the cost of producing code by 90% and every software company has the same AI, code itself stops being a competitive advantage. The long-run winners are more likely to be companies with customers, brand, distribution, network effects, unique data or deep workflow integration.

That is why the AI application layer is worth watching for startups, but "AI cuts the cost of this job by 90%" is not enough to call something a good business. The question to ask is:

> When every competitor can also cut costs by 90%, why will customers still pay me?

## 8. Sharing the gains: AI taxes and public equity

Section 4 ended on a gap: the winners *could* compensate the people who lose income, but markets do not make them. If AI keeps shifting income from wages to profits, two problems follow. People who own no shares miss out on the growth, and a tax system that relies heavily on wages loses part of its base. That is why proposals to tax AI companies, or to give the public a stake in them, have moved from essays into politics. They shift the question from redistributing *income* to distributing *capital ownership*.

As of November 15, 2026, these are the main proposals on the table, and none of them is settled policy:

| Who | What | Status |
|---|---|---|
| OpenAI | Sam Altman suggested a 5% stake in OpenAI for a government-run fund, according to the Financial Times ([TechCrunch](https://techcrunch.com/2026/07/02/openai-proposed-donating-5-of-its-equity-to-a-us-sovereign-wealth-fund/), [CNBC](https://www.cnbc.com/2026/07/02/openai-proposes-us-government-own-5percent-stake-to-address-political-blowback.html)) | Reported in July 2026 as early-stage talks; no binding terms |
| Anthropic | Contributed 846,840,960 shares, 5% of its fully diluted shares as of June 30, 2026, to the Anthropic Public Benefit Fund, a wholly owned subsidiary, with room for further contributions as the share price rises ([SEC prospectus](https://www.sec.gov/Archives/edgar/data/2130357/000162828026073040/anthropicpbc-fwpxeeaprospea.htm)) | Disclosed in its October 2026 IPO filing; the shares go to the company's own fund, not to the government |
| Sen. Bernie Sanders | The American AI Sovereign Wealth Fund Act: a one-time 50% tax, paid in stock, on companies with at least $200 million a year in AI revenue, funding annual payments to Americans ([press release](https://www.sanders.senate.gov/press-releases/news-sanders-introduces-legislation-to-create-7-trillion-ai-sovereign-wealth-fund/), [Fortune](https://fortune.com/2026/06/18/bernie-sanders-ai-fund-bill-sam-altman-1000-payments/)) | Introduced in June 2026; not law |

[Lawfare](https://lawfaremedia.org/article/scaling-sovereign-wealth--evaluating-mechanisms-for-the-u.s.-government-to-own-parts-of-ai-companies) has a useful survey of the mechanisms, from revenue sharing to golden shares. The framework from the earlier sections raises four questions about all of them.

**Who actually bears an AI tax?** Section 1 applies directly. A tax on AI providers is not necessarily paid by AI providers. In a competitive model market, much of it would be passed on to the businesses that buy AI, and through them to their customers. A tax on *usage*, such as a per-token or "robot" tax, also taxes the very productivity gain everyone is hoping for and discourages adoption. A tax on *economic rent*, the profit above what is needed to keep a company investing, distorts behavior far less. The hard part is measuring that rent.

**Taxing the right base.** Sections 5 and 7 suggest that model providers may not end up with most of the profit. If models commoditize, the largest gains may land with banks, insurers, software companies and retailers that use cheap AI to cut costs. A policy aimed only at the leading labs could miss much of the AI dividend. The alternative is to tax profits or capital income broadly, wherever AI raises them. That base is harder to attribute to AI, but harder to escape.

**Equity versus cash.** A stake in shares does not require a company to be profitable today, and it lets the public share in growth that has not happened yet. But stock received in kind is hard to sell without moving the price. It concentrates the fund in a few companies, which is the opposite of the diversification advice in Section 9. And voting shares raise awkward questions about the government's role in corporate governance.

**How much money is it?** Sanders's office puts the 50% stake at about $7 trillion, which implies roughly $14 trillion of AI equity in scope. Assuming a 5% annual payout and about 340 million Americans:

| Public stake | Fund size | Payout at 5% a year | Per person per year |
|---|---|---|---|
| 5% (the size discussed with OpenAI) | $700B | $35B | about $100 |
| 50% (the Sanders bill) | $7T | $350B | about $1,000 |

This is a hypothetical model, not a forecast. Real payouts depend on the fund's returns, whether it can sell shares, costs and legal limits. The arithmetic still makes one point clear: a voluntary 5% stake is large in absolute terms but small per person. Even the 50% version pays about $1,000 a year, far less than a lost salary. Public equity and AI taxes can complement wages, but on their own they would not replace the income of people whose jobs disappear.

My own read: sharing AI gains through public ownership and taxation is likely to remain a major policy debate, but nothing yet suggests a standard where every leading AI company hands the government 5%. Where AI profits finally settle, and how courts and Congress respond, will decide which form, if any, wins.

## 9. What this means for a long-term investor

The same framework turns into a checklist. None of this is a recommendation to buy or sell anything; it is a way to ask better questions about where AI value ends up.

**Follow the scarcity, not the usage.** AI usage can keep growing while profits move between layers. In each layer of the stack (chips, energy, data centers, models, applications) ask what is scarce today and how fast new supply can arrive. A bottleneck earns rents only until capacity catches up. As supply expands, those rents may erode into lower prices for everyone downstream, and other bottlenecks may or may not emerge.

**Separate temporary margins from durable ones.** When a company reports better margins after adopting AI, ask whether its competitors can adopt the same tools. If they can and entry is open, Section 3 suggests the margin gain drifts to customers over time. Durable gains come from companies whose moat (distribution, data, network effects, switching costs) lets them keep the saving after everyone else has it too.

**Compare returns with the cost of capital, not revenue with spending.** For AI providers and infrastructure builders, the important number is not how fast revenue grows but whether the return on the capital invested exceeds what that capital costs. Heavy capital spending in a market heading toward commodity pricing can produce large revenue and weak returns at the same time.

**Ask what the price already assumes.** A company that will capture AI value is not automatically a good investment. If the market already expects that outcome, the share price reflects it, and the investor earns a good return only if reality turns out better than what was priced in. The question is not only "who wins?" but "how much winning is already in the price?"

**Remember who wins in competitive markets.** In industries with fierce price competition, AI savings mostly reach customers. As a consumer you collect that benefit anyway. As an investor, a company in a commodity business that adopts AI well may still not reward its shareholders.

**Think about how your career and your portfolio move together.** Your career is usually your largest asset, and it is exposed to AI in a specific way. It is tempting to treat AI-linked assets as a hedge: if the gain shifts from labor to capital, you own part of the capital. Whether that actually works depends on how those assets' returns move with the shocks to your income. A recession, or a fall in AI valuations, can hurt your job prospects and those assets at the same time, and holdings spread across several AI layers can still move together. Check that correlation before counting on the hedge.

## 10. What this means for your career

Section 4 is the uncomfortable one for anyone who works for a salary: productivity gains do not automatically become pay gains. Demand for the work, the supply of people who can do it, and bargaining power decide the outcome. That suggests a few directions, each worth testing against your own situation.

**Lean toward work that AI complements rather than replaces.** Work that AI does well gets cheaper for everyone, including the people who used to be paid for it. Work that AI makes *more* valuable has a better chance of commanding a premium, especially if demand for it grows faster than the number of people who can do it: judging whether an output is right, owning the outcome and the accountability, understanding a business well enough to know which problem is worth solving, and earning the trust of customers and colleagues.

**Build skills that stay scarce and travel with you.** Section 4 named the assets that collect the rent: customer relationships, distribution, proprietary data and key business processes. Knowing a customer is not the same as owning that relationship, and the employer usually owns the data. What you can carry is deep domain knowledge, judgment about workflows and a reputation people will follow. Skills that become commodities once everyone has AI, such as writing routine code or first drafts, are the ones to move away from.

**Move early, and make sure it shows.** Section 7 applies to people as well as companies: the short-run rent goes to early adopters, and the window closes as adoption spreads. But early adoption can mainly benefit your employer if the extra output is simply absorbed. Make sure it turns into scope, responsibility or pay.

**Look at your employer's market and your own bargaining power.** Where a company keeps its AI savings, part of that surplus can be shared with the employees who remain, but only if they have the bargaining power to claim it; a profitable company can still cut staff. Where the industry is a price war, the saving goes to customers and the pressure often lands on headcount, though a company that grows by cutting prices may also hire. Ask both questions: how resilient is the business, and how replaceable am I in it?

**Consider becoming the new entrant.** Section 6 is the most hopeful part of the post for individuals: AI may lower the cost of testing some product ideas enough that a small team, or a single person, can try what used to need a funded startup. Even if you stay employed, a small side project is a low-cost way to learn where new value is being created.

**Build a buffer.** The 70 people in Section 4 are a hypothetical example, but the displacement risk behind them deserves practical preparation. Savings, an up-to-date network and a habit of learning make a transition survivable if your role is one that disappears.

## 11. Conclusion

The host's four-way split is a good start. Reorganized as economics, it says:

- AI can expand what the economy is able to produce; adoption costs, organizational change and market conditions shape **how much of that value is realized**.
- **Competition, scarcity and bargaining power** determine **who gets it**, market by market.
- Lower entry costs and expanding demand can **make the pie larger** in ways the four-way split cannot see.
- Whether people without AI shares or AI jobs share in the gains is a **policy choice**, and the tax base matters as much as the tax rate.

That is closer to the core of the AI economic shift than the usual debate about how many jobs AI will replace.
