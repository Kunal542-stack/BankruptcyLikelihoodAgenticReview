# How to Evaluate the Investigator Agent

## 0. What the agent presents (corrected 2026-11-11)

**The agent does not predict or explain the reason for a bankruptcy.** It presents the evidence that supports the model's probability on the filing date:
- what the model saw
- what the filings confirm or contradict
- how strong that evidence usually is

Grading the report against later events or against the company's stated causes was considered and dropped. The causes are many, and a lot can change within the 365 days after the filing.

**What the bankruptcy 8-Ks of our 15 checked cases (10 companies) say:**

All 10 bankruptcies were financial in form:
- **Chapter 11 with lenders:** Airspan and CareMax (with a restructuring support agreement), Nogin and iRobot (debt accelerated).
- **Chapter 11 with a sale of the assets:** BowFlex and Sangamo.
- **Chapter 11 after strategic alternatives:** Infinity.
- **Chapter 7 liquidation:** Waitr, Canoo and Loop Media.

None was caused by a lawsuit or a fraud. The 8-Ks state how the company is going bankrupt, not why.

**What the 15 reports showed beforehand** (filed 19 to 320 days before the bankruptcy):
- going concern doubt in 14 of them
- a net loss in all 15
- under 8 months of cash in 14 of them
- a delisting 8-K in the year before in 11 of them

So the evidence the agent can present was visible in the reports.

## 1. What the report is really for

- **A bankruptcy has no single knowable reason.** The same facts (losses, a default, a going concern warning) end in bankruptcy for one company and in a rescue for another, so no one can prove why a company will or will not fail.
- **So the report does not find "the reason".** It justifies a probability: it shows which facts visible on the filing date are consistent with the model's probability, which facts point the other way, and how strong each fact usually is.
- **That gives the report a clear test.** A good report:
  - is true (every fact can be checked)
  - is complete (it does not miss an important fact that was available)
  - is honest about strength (it does not treat a common warning as proof)
  - makes the probability more useful than the model's number alone

## 2. What the report should contain

| Part | What it is | Who makes it |
|---|---|---|
| The probability | the model's calibrated probability and the usual rate for reports like it | code |
| What moved the model | the top features for this report and their values (SHAP), with peer ranks | code |
| The standard charts | the same 3 charts for every company: the main numbers over time, cash runway, and the company against its industry | code |
| The cue checklist | the 10 cues: for each one, present, absent or unclear, with a quote, its link and its date | the LLM finds and quotes; code checks the quote |
| Evidence against | the facts that point toward survival | the LLM, checked by code |
| The judgement | the LLM's own risk, which facts moved it away from the model, and what would change its mind | the LLM |
| Dates to watch | debt maturities, cure periods and hearings in the next 12 months | the LLM, checked by code |

**The rule: everything that can be computed is computed by code, and the LLM only reads, quotes and judges.**

**Why:**
- Numbers and charts made by code are the same every time and can be tested once.
- Numbers and charts made by an LLM can be wrong in a new way on every run, and each one would need checking.
- The LLM is still needed for what code cannot do well: reading long filings, recognising that "we entered into a forbearance agreement" is a default, and weighing facts against each other.

**On charts:** the LLM can add one extra chart only when a standard chart cannot show its point. Code then checks that the chart's numbers come from the data. This keeps reports comparable across companies, which matters for evaluation.

## 3. Why evaluating an agent is hard (the risks)

1. **There is no true answer for "why".** We only know the outcome (bankrupt or not), not the reason, so we cannot mark a reason as correct.
2. **Hindsight bias.** A reviewer who knows the company failed sees every warning as obvious and writes a gold report that fits the outcome.
3. **One gold report is only one good answer.** Two good reports can use different words, order and emphasis. Scoring by how similar a report is to the gold report punishes good reports that are written differently.
4. **The gold standard can be circular.** Our current gold reports were made with an agent's help and then checked by people, so an agent that writes like that agent scores well even if both are wrong.
5. **The LLM judge has its own biases.** It tends to:
   - prefer longer answers
   - prefer answers that sound like its own writing
   - be lenient
   - give a different score when run again
6. **The agent is not deterministic.** The same input can give a different report on each run, so one run per case says little.
7. **The LLM may already know the answer.** For a well-known bankruptcy, the LLM may remember what happened and "predict" it, which looks like good reasoning but is not.
8. **Too few cases.** Fifteen cases cannot tell a real improvement from luck.
9. **Most high scores are false alarms.** If we only check companies that did go bankrupt, an agent that always says "real risk" looks perfect.
10. **Optimising for the judge.** If we tune the agent to please the judge, it learns the judge's taste instead of getting better.

## 4. The plan: a gold evidence key instead of a gold report

The fix is to stop comparing prose with prose. Instead, people build a **gold evidence key** for each case: the list of facts that were available on the filing date. The agent fills in the **same checklist**, so the two can be compared field by field, mostly without an LLM judge.

### 4.1 How people build the evidence key (the manual verification)

1. **Choose the cases in four groups**, so the test is fair to both kinds of mistakes. Aim for 30 to 40 cases, 8 to 10 per group:

   | Group | Score | Outcome | Count |
   |---|---|---|---|
   | true alarms | high | went bankrupt | 8 to 10 |
   | false alarms | high | did not go bankrupt | 8 to 10 |
   | misses | low | went bankrupt | 8 to 10 |
   | quiet cases | low | did not go bankrupt | 8 to 10 |

2. **Hide the outcome from the reviewers.** Give them only the filings dated on or before the report date. Do not tell them what happened afterwards, and record whether they already knew the company.
3. **Use a fixed form.** For each of the 10 cues, the reviewer records:
   - present, absent or unclear
   - the exact quote
   - the filing, section and date
   - whether it is a key fact, meaning a fact any good report must mention
   - "Absent" means the reviewer looked in the listed sections and did not find it.
4. **Two reviewers per case, working separately.** Then:
   - Measure how often they agree (Cohen's kappa). Agreement above about 0.7 means the form is clear enough to trust.
   - Settle each disagreement by talking it through, and write down why.
5. **Freeze the key.** Once a case is agreed, it does not change, so later agent versions are compared fairly.

### 4.2 How a report is scored: five numbers instead of one

| Score | Question | How it is measured | Needs a human? |
|---|---|---|---|
| **1. Truth** | Is every fact real? | code checks every quote word for word in the saved filing, recomputes every number, opens every link, and checks that no source is dated after the report | no |
| **2. Coverage** | Did it find what was there? | the share of the key's key facts that the agent's checklist also has (recall), and the share of the agent's "present" cues that the key also has (precision) | no, the checklists are compared field by field |
| **3. Judgement** | Does its risk add anything? | on all cases, does the agent's own risk predict the real outcome better than the model's probability alone (Brier score, and how often it calls false alarms false alarms)? | no, the outcomes are known |
| **4. Stability** | Does it say the same thing each time? | run every case 3 times and measure how often the checklist and the verdict agree | no |
| **5. Usefulness** | Can a reader use it? | people compare two versions side by side, without knowing which version is which, on a short rubric: clear, separates facts from guesses, gives dates to act on | yes, on a sample |

- **Hard failures override the score.** A made-up quote, a wrong number or a source dated after the report fails the report, whatever its other scores are.
- **The LLM judge is used only where code cannot compare**, for example deciding whether the agent's sentence states the same fact as the key. Before we trust it, it is checked against human labels on about 50 examples and must agree with the humans most of the time.
- **Against the LLM already knowing the answer:**
  - Hide the company name and ticker where possible.
  - Test separately on reports filed after the LLM's training cutoff (2025 and 2026), which it cannot remember.
- **Against optimising for the judge:** keep about a third of the cases as a hidden test set that is used only for the final number.

## 5. What this answers about the gold standard

- **Is a gold standard the right approach?** A gold *report* is the wrong target, because there are many good reports and the reason cannot be known. A gold *evidence key* is the right target, because whether a fact was in the filings on a date can be checked and agreed.
- **How do we "manually tell this is the reason"?** We don't. People check only things that can be verified:
  - Was the fact there?
  - Is the quote right?
  - Is it a key fact?
  - The outcome check (score 3) then shows whether the agent's weighing of those facts is better than the model alone.
- **How do we quantify any agent against the gold?** With the five scores above. Every agent (LangGraph, Claude Agent SDK or another) fills in the same checklist, so they are all scored the same way.

## 6. Steps, in order

1. Change the report format so the agent also writes the cue checklist as structured data (JSON) next to the prose.
2. Move all numbers and the 3 standard charts into code.
3. Build the review form, and turn our 15 checked cases into evidence keys with two reviewers each.
4. Add cases until each of the four groups has about 8 to 10.
5. Write the scoring script (truth, coverage, stability, judgement) and test the LLM judge against human labels.
6. Score the current agent to get a baseline, and only then change the agent.
