# From one prompt to a graph

## The two designs

**Harness agent (Claude Agent SDK).** Claude gets Pramukh's whole prompt and a set of tools (Bash, Python, `sec_tools.py`). It decides for itself what to download, what to read, which scripts to write, and when to stop. Everything happens inside one long conversation.

**Graph agent (LangGraph).** The same prompt is cut into steps. Each step is a **node** that does one job and writes its result into a shared **state** (a Python dict). The next node reads that state.

The rule for cutting: **follow the prompt**. Where the prompt gives an exact rule, that step is code. Where it leaves the agent a choice, the LLM decides.

- **Code nodes** do the work that has one right answer: loading numbers, applying the filing rule, downloading, searching, running the chart code, checking the report.
- **LLM nodes** do the work that needs judgement or a choice: reading filings, deciding what to read next and when to stop, weighing the evidence, deciding what to chart (and looking at each chart), writing the report.

Each LLM node gets only the part of Pramukh's prompt that its job needs, plus the state it needs.

The outcome:
- The graph fixes the structure: which kinds of steps happen, in which order, and where the loops are. Inside that structure, the LLM makes the same choices the harness agent makes.
- You can see every intermediate result, because each node saves what it produced, and every prompt and answer is saved in `outputs/llm_calls/` (a rerun reuses them).

## How each part of the prompt maps to a node

| Prompt section (Pramukh) | Node | Type | What it does |
|---|---|---|---|
| "The report: ... Model score ... The score ranks reports, it is not a probability. Reports above 0.7 went bankrupt 18% of the time ..." | `setup_case` | code | Loads the report row and its score, then finds the score's band and that band's base rate (18% / 4% / 2% / 0.3%). |
| "Numbers first: compare each of the 8 with the company's own history and with peers ... leverage, current ratio, cash burn and how many months of cash are left, using the last quarter's burn too ... adjust every year the same way" | `compute_numbers` | code | Works with rows filed on or before the report date only. Builds the 8 inputs for this report and the year before, each as a share of assets, with its peer rank. Adds leverage and current ratio. From the filing's own XBRL numbers: cash on hand (exact dollars), monthly burn and months of cash, the same for the last quarter alone, and the loss split into cash and non-cash charges for this period and for the same period a year earlier. Arithmetic has one right answer, so it is code. |
| "Which filings to get: this report, the latest 10-K before it and every 10-Q since, the 8-Ks of the last 18 months with items 1.01 ... 5.02, and any NT 10-K or NT 10-Q. Skip 8-Ks with only 2.02, 5.07, 7.01, 8.01 or 9.01." | `choose_filings` | code | Applies that rule exactly to the company's filing list from `sec_tools.py`, and keeps the list of the filings it left out for `decide_more`. |
| "Convert them to text with table rows kept on one line, search them, and read the passages around each hit" | `get_passages` | code | Downloads each filing and turns it into text, one table row per line. For a 10-K or 10-Q it keeps the passages around the words the prompt names: going concern, substantial doubt, auditor's report, debt note, covenants, waivers, amendments, maturities, subsequent events, liquidity, Part II Items 3 and 5, the cash flow statement and non-cash items. For an 8-K it keeps the item text; for an NT form, the reason the report is late. |
| "search them, and read the passages around each hit ... Use older filings only to see when a problem started. Stop when new filings no longer change your view." | `decide_more` → `search_more` → `read_more` (a loop) | **LLM** decides, code searches, **LLM** reads | After the first reading, the LLM decides whether more reading would change its view. If so, it names words to search for (a lender, a note, "restricted cash") and up to 3 older filings. Code downloads them and cuts the lines around each hit; the LLM reads them and adds findings. It stops when it says more reading would not change its view, or after 3 rounds. |
| "What to read ... Only 'substantial doubt' counts as going concern doubt ... Copy quotes word for word" | `read_filings` | **LLM**, once per filing | Reads one filing's passages and writes down the findings, each with a word-for-word quote, form, date and section. |
| "2 to 4 charts embedded with relative paths, each making one point; look at each and fix anything misleading" | `plan_chart` ⇄ `draw_chart` (a loop) | **LLM** decides and looks, code draws | The LLM decides what to chart (not a fixed set) and writes the matplotlib code. Code runs it in a separate process with only the case's data and saves the PNG. The LLM then sees the picture and decides: keep it and make another, fix it, drop it, or stop with 2 to 4 charts. At most 8 chart decisions. |
| "Connect the two ... Look for evidence both ways ... Start your own risk from the base rate of the score's band ... real risk / false alarm / unclear" | `assess` | **LLM** | Combines the numbers with all findings and lists evidence toward and against. Starts from the band's base rate, moves only for specific facts, and gives the verdict, its own risk and whether it agrees with the model. |
| "Finish by writing report.md ... at most 1,200 words ... answer, verdict, table of the 8 numbers, main reasons, evidence against, how it developed, dates to watch, charts, how sure, filings used" and (Kunal's update) "give a clickable link for a verifiable source ... for all reasons" | `write_report` | **LLM** | Writes `report.md` in that exact structure from the state. It doesn't read the filings again. It gets each filing's SEC EDGAR link (`get_passages` adds it) and ends every reason, point against, turning point, date to watch and chart with a link to its source. |
| "Before finishing, use a script to check that every quote appears word for word in the saved filings, recompute every number you cite, and confirm that no source is dated after {filed}" | `check_report` | code | Checks that each quote appears verbatim in the saved filing text, that every dollar amount can be traced to the filings or the computed numbers (or is written as a calculation, "… = $X"), that the report is at most 1,200 words, that every listed filing is dated on or before the report, and (Kunal's update, "give a clickable link for everything you cited") that every item under main reasons, evidence against and how it developed has a source link, and that every SEC link is one of the filings that were read. If something fails, the problems go back to `write_report`, at most 3 writes in total. |

## The flow

```
setup_case → compute_numbers → choose_filings → get_passages → read_filings → decide_more ──enough──→ assess → plan_chart ──done──→ write_report → check_report ──ok──→ END
                                                                                 │    ↑                          │    ↑                       ↑              │
                                                                         read more    └ read_more ← search_more   draw └── draw_chart             └── problems ──┘
```

Three loops, each a conditional edge with a cap:
- **read more** (`after_decide`): the LLM asks for more reading, at most 3 rounds.
- **charts** (`after_plan`): the LLM makes, looks at and fixes charts, at most 8 decisions.
- **rewrite** (`after_check`): the check found problems, at most 3 writes.

## What changes, and why

| In the harness | In the graph | Why |
|---|---|---|
| Claude decides which filings to download and when to stop | The prompt's rule picks the filings (code); then the LLM decides whether to read more, what to search and which older filings to add, and when to stop | The rule is exact in the prompt, so it is code; the rest is a choice, so the LLM makes it |
| Claude writes its own scripts for peers and ratios | `compute_numbers` is written once, in plain pandas | Arithmetic has one right answer; the numbers are the same every time and can be checked by reading one function |
| Claude searches the filings as it likes | Fixed keywords for the first pass, then the LLM's own search words | The first pass covers what the prompt names; the loop lets the LLM follow leads |
| Claude draws 2 to 4 charts it picks itself | The LLM picks, writes and looks at its charts; code only runs the code | Same as the harness, but the code runs in a guarded process |
| One long conversation | Short LLM calls with focused prompts | Each step sees only what it needs, and its output is saved in the state |
| Claude checks its own quotes and numbers | `check_report` checks them in code and sends failures back | The check cannot be skipped |

The judgement and the choices stay with the LLM. Only the mechanical parts became code.
