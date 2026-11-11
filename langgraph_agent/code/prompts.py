# The prompts for the three LLM steps. Each one is the part of Pramukh's prompt that its step needs,
# mostly in his own words, plus the data that step is given.
import json

SYSTEM = ("You are the Investigator Agent of a bankruptcy early-warning system. "
          "Our XGBoost model scored a financial report for the risk that the company goes bankrupt within 365 days.")


def case_header(case):
    return (f"The report: {case['name']}, {case['form']} for the period ending {case['period_end']}, "
            f"filed {case['filed']}, adsh {case['adsh']}, cik {case['cik']}. Model score: {case['score']:.3f}.\n"
            "The score ranks reports, it is not a probability. Reports scored above 0.7 went bankrupt 18% of the time, "
            "0.5-0.7 4%, 0.2-0.5 2%, below 0.2 0.3%.\n"
            f"Write as if today were {case['filed']}. Use nothing filed later. If you know what happened to the company "
            "later, don't use it.")


def read_filing_prompt(case, filing_label, text):
    return f"""{case_header(case)}

Your job in this step: read the passages below from ONE filing ({filing_label}) and write down what matters for
bankruptcy risk. Do not judge the company yet; only report what this filing says.

What to look for:
- In a 10-K or 10-Q: the three statements (how much of the loss is non-cash: impairments, tax charges, stock
  compensation, depreciation), the going concern note, the auditor's report, the debt note (maturities, covenant
  breaches, waivers, amendments), subsequent events, MD&A liquidity (cash, restricted cash, revolver availability,
  the last quarter's operating cash flow), and in a 10-Q Part II Items 3 and 5.
- In an 8-K only the item text, in an NT form only why the report is late.
- Evidence both ways. Toward bankruptcy: missed payments, defaults, forbearance and short waivers, debt due that cash
  can't cover, restructuring advisors, delisting, late filings. Against: refinancing, new money, a year of cash,
  a non-cash or one-off loss, asset sales, support from a lender or owner.
Only "substantial doubt" counts as going concern doubt, not the standard "prepared assuming the company will
continue as a going concern".

Rules: copy every quote word for word from the passages (short, under 40 words). Give numbers exactly as written.

Return JSON: {{"findings": [{{"topic": "going_concern | liquidity | debt | covenant_or_waiver | default | non_cash_items |
operations | financing | restructuring | delisting | late_filing | management | other",
"direction": "toward | against | neutral", "finding": "one sentence", "numbers": "the key figures, or empty",
"quote": "word for word", "section": "where in the filing"}}]}}

Passages from {filing_label}:
{text}"""


def assess_prompt(case, numbers, findings):
    return f"""{case_header(case)}
The score's band is {case['band']}, where {case['base_rate_pct']}% of reports went bankrupt.

The model only sees 8 raw dollar numbers from this report: total_assets, current_assets, current_liabilities,
total_liabilities, revenue, net_income, operating_income, operating_cash_flow. Net income matters most. It doesn't see
the text, the company's history or its industry. Nobody can see how much each number moved this score, so any order
of drivers is an inference.

The numbers (computed from shared/financials.csv, rows filed on or before {case['filed']}; $M; income and cash flow
per year, 10-Qs annualized; peer_percentile = share of same-industry peers with a lower value as a share of assets):
{json.dumps(numbers['inputs'], indent=1)}
{json.dumps(numbers['extras'], indent=1)}

Cash and the cash-adjusted loss (computed from this filing's own numbers, for its period to date):
{json.dumps(numbers['cash'], indent=1)}

What each filing says (from the reading step; every quote is word for word):
{json.dumps(findings, indent=1)}

Your job in this step: connect the two. Use the text to explain the numbers, and note where they disagree, such as
healthy ratios next to alarming footnotes. Use the cash, months of cash and cash-adjusted loss computed above; don't
estimate them again from the text. Check them against the last quarter's burn and any debt due in the findings
(months_of_cash ignores debt payments). Decide whether the score reflects real distress or an artefact.
Bankruptcy means Chapter 11 or 7, receivership, or a court-supervised restructuring (including Chapter 15).
Going concern doubt alone is not bankruptcy, many companies survive it.

Start your own risk from the base rate of the score's band. Going concern doubt, losses and negative equity are common
among high scores and are already in that rate; move away from it only for specific facts such as missed payments, debt
due that cash can't cover, or new financing, and say which ones moved you. Then call it a real risk if your risk is at
or above the band's rate, a false alarm if it is well below it, and unclear if it is close.

Return JSON:
{{"answer": "two or three sentences on why the score is what it is",
"verdict": "real risk | false alarm | unclear", "own_risk": "very high | high | medium | low", "own_risk_pct": number,
"agree_with_model": "yes | no | partly", "moved_by": ["the specific facts that moved you from the base rate"],
"reasons": [{{"reason": "...", "kind": "model input | from the filings", "numbers": "...", "peer_comparison": "...",
  "quote": "word for word from the findings, or empty", "source": "form, date, section"}}],
"evidence_against": [{{"point": "...", "quote": "word for word, or empty", "source": "..."}}],
"timeline": [{{"date": "YYYY-MM-DD", "event": "..."}}],
"dates_to_watch": ["..."], "would_change_my_mind": ["..."],
"confidence": "high | moderate | low", "could_not_check": ["..."]}}"""


def write_report_prompt(case, numbers, assessment, charts, filings, problems, draft=""):
    fix = ""
    if problems:
        # on a retry, the model edits its own draft instead of starting over
        fix = ("\n\nBelow is your last draft. It had these problems; fix every one and change nothing else "
               "(drop or correct a quote that can't be matched word for word; if too long, cut the least important "
               "points until it is under 1,100 words; give a missing source link from the \"Filings used\" list):\n- " + "\n- ".join(problems) + "\n\n===== LAST DRAFT =====\n" + draft)
    chart_lines = "\n".join(f"![{caption}]({path})" for path, caption in charts)
    filing_lines = "\n".join(f"{f['form']} {f['date']}: {f.get('url', '')}" for f in filings)
    return f"""{case_header(case)}

Your job in this step: write the final report from the work already done. Do not add facts that are not below.

The numbers:
{json.dumps(numbers['inputs'], indent=1)}
{json.dumps(numbers['extras'], indent=1)}
{json.dumps(numbers['cash'], indent=1)}

The assessment:
{json.dumps(assessment, indent=1)}

Charts to embed (exactly these lines):
{chart_lines}

Filings used, with the link to each one on SEC EDGAR:
{filing_lines}

Write report.md for a reader who hasn't seen the data, at most 1,200 words in total, tables included (aim for about
1,000), with these parts:
- a title line: company (CIK), form for the period, filing date, model score
- Answer: two or three sentences on why the score is what it is
- the verdict (real risk, false alarm or unclear), your own risk (very high, high, medium or low, with a rough %),
  and whether you agree with the model
- a table of the 8 numbers, this report vs the year before, with what drives each one and how it ranks among peers
- a line with the cash on hand (exact dollars), months of cash at the current burn, and how much of the loss is
  non-cash (the cash-adjusted loss)
- the main reasons in order (3 to 6, the most important only), each marked "model input" or "from the filings",
  with numbers, peer comparison and a quote, and a clickable link to a verifiable source for every reason
- the evidence against, with a clickable link to a verifiable source for every point
- how it developed, as dated turning points, with a clickable link to a verifiable source for every point
- dates to watch in the next 12 months, and what would change your mind, with a clickable link to a verifiable
  source for every date
- the charts, each with a clickable link to the filing its numbers come from
- how sure you are and what you couldn't check
- "Filings used": the filings as form and date only
Write each item of the main reasons, evidence against, how it developed and dates to watch as one "-" or "1." line,
and end it with its source as a markdown link, for example [10-Q 2023-08-14, Note 2](link). Use only the links in
"Filings used" above, so every citation can be clicked and checked.
Copy quotes word for word from the assessment, in double quotes, with the form, filing date and section of each.
Keep what the filings say separate from what you infer. Keep it short and plain. Return only the markdown.{fix}"""


def decide_more_prompt(case, findings, filings, others, round_no):
    read = "\n".join(f"{f['form']} {f['date']}" for f in filings)
    rest = "\n".join(f"{f['adsh']}  {f['form']} {f['date']}  items {f['items']}" for f in others) or "(none)"
    found = "\n".join(f"- [{x.get('direction')}] {x.get('finding')} ({x.get('filing')})" for x in findings)
    return f"""{case_header(case)}

Your job in this step: decide whether to read more before judging the company. This is round {round_no} of at most 3.
From the prompt: "search them, and read the passages around each hit", "use older filings only to see when a problem
started", and "stop when new filings no longer change your view".

Filings already read (the passages around fixed keywords such as going concern, default, covenant, liquidity):
{read}

What they say so far:
{found}

Filings not read yet (filed before the report; only these can be added):
{rest}

You can ask for two things:
- searches: words or short phrases to look up in the filings already read, to follow a lead (a lender's name, a note
  number, "restricted cash", a debt instrument, an event you need the details of). Up to 6 terms.
- older_filings: up to 3 filings from the "not read yet" list (by adsh), only to see when a problem started or to read
  an 8-K you need.
Stop (done = true) when more reading would not change your view of the risk.

Return JSON: {{"done": true | false, "why": "one sentence", "searches": ["..."], "older_filings": ["adsh", ...]}}"""


def read_more_prompt(case, what, text, findings):
    known = "\n".join(f"- {x.get('finding')}" for x in findings)
    return read_filing_prompt(case, what, text) + f"""

Findings you already have (don't repeat them; only add what is new):
{known}

These passages come from several filings: add "filing": "form and filing date" to each finding."""


def plan_chart_prompt(case, assessment, charts, last):
    made = "\n".join(f"chart {i + 1} [{c['status']}]: {c['point']}" for i, c in enumerate(charts)) or "(none yet)"
    return f"""{case_header(case)}

Your job in this step: make the charts for the report, one decision at a time. From the prompt: "2 to 4 charts ...,
each making one point; look at each and fix anything misleading".

You decide what to chart. Choose what shows the reader the most about this case, not a standard set. You can
chart anything in the data below: the company's history, how it ranks among peers, the cash runway, the loss with
and without non-cash charges, the timeline or the maturities from the assessment. If a chart shows something more
interesting than you planned, follow it.

The assessment so far:
{json.dumps(assessment, indent=1)}

Data your code can use (already loaded; don't load anything else):
- history: pandas DataFrame, the company's reports up to this one. Columns: form, fp, ddate (YYYYMMDD), filed, and
  total_assets, current_assets, current_liabilities, total_liabilities, revenue, net_income, operating_income,
  operating_cash_flow in dollars (income and cash flow per year; 10-Qs annualized).
- peers: pandas DataFrame, same-industry peers at about the same date, columns name, sic, ddate, filed + the same 8.
- facts: dict with "case", "inputs" (the 8 numbers vs the year before and peers), "extras" (ratios), "cash" (cash,
  burn, months of cash, last quarter, the loss split for this period and the year before) and "assessment".
- pd, np and plt are imported. Make ONE figure (about 7 x 3.5 inches) with a title that states its point, labelled
  axes and units. Don't call plt.savefig or plt.show, and don't import anything else.

Charts so far:
{made}

{last}

Decide the next step:
- "new": make a new chart (give its one point and the code)
- "fix": redo chart n (give the fixed code), for example if it is misleading, unreadable, or the code failed
- "drop": drop chart n if it doesn't make a clear point
- "done": you have 2 to 4 good charts
Return JSON: {{"action": "new | fix | drop | done", "chart": n (for fix or drop), "point": "the one point it makes",
"caption": "a short caption for the report", "code": "python code"}}"""
