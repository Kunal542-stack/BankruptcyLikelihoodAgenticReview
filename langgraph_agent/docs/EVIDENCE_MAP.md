# What the Investigator Agent Should Look For, and Where

The agent's job is to **justify the probability the model gave a report**:
- why it is high or low
- whether the filings agree
- what would change it

This file lists:
1. the warning cues that actually lead to bankruptcy
2. where each one shows up in SEC filings
3. how strong each one was in our data
4. what the report should look like

The rates come from `sota_push/long_dataframe_2009_to_2026.pkl`: 388,251 10-K and 10-Q reports, 2009 to 2025, with 2,698 bankruptcies within a year. The average rate is **0.74%**. "Times average" = the bankruptcy rate of reports with the sign ÷ 0.74%.

## The 8 numbers are not the reasons

- The **8 variables** (now 13, or 140 in `sota_push`) are what the model reads. They are **inputs, not reasons**.
- A company goes bankrupt for a **few real reasons**:
  - it runs out of cash
  - it can't pay or refinance its debt
  - it owes more than it owns
  - it loses access to new money
  - a shock hits the business
- The numbers point at these reasons. The filings say whether they are really happening.
- So the agent should check **10 cues**, not 8 numbers.

## The 10 cues

| # | Cue | What it means | Our data: times average (share of reports) | Where to find it |
|---|---|---|---|---|
| 1 | **Restructuring already under way** | the company is preparing a bankruptcy or a deal with lenders | restructuring support agreement **15×** (0.1%); strategic alternatives **5.3×** (4%); "chapter 11" in the report 3.8× (4%); debtor-in-possession 2.9× | MD&A liquidity, subsequent events note, 8-K Item 1.01 (the agreement), 8-K 5.02 (a chief restructuring officer is appointed) |
| 2 | **Debt default or forbearance** | it already missed a payment or broke a loan term, and lenders are holding off | forbearance **6.7×** (1.3%); 8-K Item 2.04 debt accelerated **6.2×** (1.1%); covenants not met 2.9× (7%); notice of default 2.2× | debt note (covenants, waivers, amendments), 10-Q Part II Item 3 "Defaults upon senior securities", 8-K 2.04 and 1.01 |
| 3 | **Losing the stock listing** | the exchange warns it; it gets harder to raise money | minimum bid price **5.3×** (2%); 8-K Item 3.01 notice **4.9×** (7%); reverse stock split 2.4× (11%) | 8-K 3.01, 10-K Item 5, Form 25 (delisting) |
| 4 | **Going concern doubt** | management or the auditor says "substantial doubt" the company can last a year | **2.5×** (26% of reports, but **63% of all bankruptcies**) | the auditor's report, Note 1 or 2 (going concern or liquidity), MD&A liquidity |
| 5 | **Running out of cash** | cash covers less than a year at the current burn | under 12 months of cash 1.9× (27%) | cash flow statement, MD&A liquidity and capital resources, the going concern note |
| 6 | **Debt due that cash can't cover** | a large loan falls due soon (a "maturity wall") | in the model as `debt_due_to_cash` | debt note (maturity table), MD&A contractual obligations, subsequent events |
| 7 | **Owes more than it owns** | losses have wiped out the equity | negative equity 2.4× (19%); a net loss 1.9× (47%) | balance sheet, statement of equity |
| 8 | **Reporting breakdown** | it can't produce its reports on time or correctly | restatement (8-K 4.02) 2.6×; "identified a material weakness" 2.1×; late filing notice (NT 10-K/10-Q) 1.9× (20%); filed late 1.8× | NT 10-K or NT 10-Q (Part IV: why it's late), 10-K Item 9A (controls), 8-K 4.01 (auditor change) and 4.02 |
| 9 | **A shock to the business** | big write-downs, a collapse in sales, a lawsuit | impairment (8-K 2.06) 2.6×; revenue fall and asset write-downs are in the model | 8-K 2.06, MD&A results, the contingencies note and Item 3 (legal proceedings) |
| 10 | **Evidence against** | why it may survive | — | new money (8-K 1.01, 3.02, S-1 or 424B prospectus), asset sales (8-K 2.01), waivers and extensions (debt note), owner or lender support, a loss that is mostly non-cash (cash flow statement), a business that normally looks like this (a pre-revenue biotech) |

**How to read the table:**
- **Rare but strong** signs move the risk a lot when present: a restructuring support agreement, forbearance, a debt acceleration 8-K, a delisting notice.
- **Common** signs are already in the base rate and should move it only a little: going concern doubt, a net loss, negative equity.
- This is the rule the prompt already has ("start from the base rate… move away only for specific facts"). The table gives the agent numbers for it.
- **Weak alone:**
  - An officer leaving (8-K 5.02) is only 1.2×, because it's very common.
  - The plain phrase "material weakness" is only 1.3×, because it also finds "we did not identify any material weakness".
  - In both cases the agent has to read the sentence, not just find the words.

## Which sections to read

| Filing | Read | Skip |
|---|---|---|
| **10-K** | auditor's report (going concern paragraph, critical audit matters); Note 1 or 2 (going concern, liquidity); debt note (maturities, covenants, waivers, amendments); subsequent events note; contingencies note and Item 3 (legal proceedings, only big claims); MD&A **Liquidity and Capital Resources**; Item 9A (only if a material weakness is reported); Item 5 (only for listing problems); the three statements (how much of the loss is cash) | business description, boilerplate risk factors, directors and pay, accounting policies, forward-looking statements, most exhibits |
| **10-Q** | the same notes and MD&A liquidity; Part II Item 1 (legal), Item 1A (only new risk factors), **Item 3 (defaults)**, Item 5 (other information) | the rest |
| **8-K** | the text of items 1.01, 1.02, **1.03**, 2.01, 2.03, **2.04**, 2.05, 2.06, **3.01**, 3.02, 4.01, **4.02**, 5.02 | 2.02, 5.07, 7.01, 8.01 and 9.01 alone |
| **NT 10-K / NT 10-Q** | Part IV (why the report is late, and any expected loss) | — |
| **Others worth a look** | Form 25 (delisting), Form 15 (stops reporting), S-1 or 424B (new money, and at what price) | proxy statements |

The current prompt already covers most of this. The additions are:
- the auditor's critical audit matters
- Item 9A
- Item 5
- 8-K Items 2.05 and 3.02
- Forms 25 and 15
- reading "strategic alternatives" and restructuring support agreements as their own cue

## What the report should justify

The report has to back up one number: **the probability that the company files for bankruptcy within 12 months**. Every claim comes from one of two places, dated on or before the report's filing date:
- **the numbers**: the rows in `financials.csv`, and the model's own breakdown of the score
- **the filings**: word-for-word quotes, with form, date, section and a link

Suggested shape (short, at most about 1,200 words):

1. **The probability and what it means:**
   - The calibrated probability (not the raw score). The raw score above 0.7 means about 9% in our data, not 70%.
   - The base rate of reports like it.
   - One or two sentences on why.
2. **What moved the model:** the top 5 features for this report from SHAP, each with its value and peer rank.
   - The model can now give this breakdown per report, so the order of drivers no longer has to be guessed.
   - This replaces the table of the 8 numbers.
3. **The 10 cues, as a checklist:** for each cue, one line:
   - present, not present or unclear
   - the evidence: a quote with its link, or the number
   - whether it moves the risk up or down
4. **Evidence against** (cue 10), with links.
5. **Own view:** start from the calibrated probability, then move it for specific facts only, and say which ones. Give the verdict (real risk, false alarm or unclear).
6. **How it developed:** dated turning points, with links.
7. **Dates to watch** (debt maturities, cure periods, hearings) and what would change the view.
8. **How sure, and what couldn't be checked.**

## What has to change in the agent for this

1. **The prompt:**
   - It describes the old 8-variable model and the old band rates (above 0.7 → 18%).
   - It should give the calibrated probability and the base rate from the new model.
   - It should drop "you can't see how much each number moved this score".
2. **The model's breakdown:** pass the per-report SHAP values (top features) to the agent, from the model that scored the report.
3. **The cue checklist:** add the 10 cues and the times-average numbers above, so the "move away from the base rate" step uses measured strengths.
4. **The extra sections and forms:** add the sections and forms listed in "Which sections to read".
5. **The checker (`check_report`):** also check that every cue line has a link or says "not found in the filings read".
6. **Test it:** rerun on the 15 checked cases and compare with the checked reports (LLM judge plus manual review).
