# Investigator agent as a LangGraph graph

This is the same job as the Claude Agent SDK ("harness") agent: explain why our XGBoost model scored a filing the way it did, and decide whether it is a real risk. It follows Pramukh's final prompt, cut into fixed steps. [docs/PROMPT_TO_GRAPH.md](docs/PROMPT_TO_GRAPH.md) shows which part of the prompt each step comes from.

## Folders

```
langgraph_agent/
├── README.md            ← you are here
├── code/                ← all the Python (start with graph.py)
├── docs/                ← how the prompt became a graph, and how Claude in the app answers prompts
├── inputs/              ← what we were given: Pramukh's prompt and his 15 gold reports
└── outputs/             ← what the agent made: reports, judge scores, saved LLM calls
```

| Path | What it is |
|---|---|
| `code/graph.py` | The graph: 9 nodes, the edges between them, and the retry loop. Start reading here. |
| `code/steps.py` | The code steps: load the case, compute the numbers (with cash and runway), choose filings, cut out passages, draw charts, check quotes. |
| `code/prompts.py` | The prompts for the 3 LLM steps (read a filing, assess, write the report), taken from Pramukh's prompt. |
| `code/llm.py` | `ask_llm(prompt)`: sends a prompt to Claude (Opus 5.5) through the Claude Agent SDK, with no tools, or saves it to a file (files mode). |
| `code/run.py` | Runs the graph on one or more reports. |
| `code/judge.py` | LLM as a judge: compares each graph report with the harness report, which is the gold standard. |
| `code/pending.py` | Files mode helper: which cases are ready to move on, and which prompts still need an answer. |
| `docs/PROMPT_TO_GRAPH.md` | Which part of Pramukh's prompt each node comes from, and why. |
| `docs/HOW_TO_ANSWER.md` | The instructions Claude in the app follows when it answers a saved prompt. |
| `inputs/pramukh_prompt.txt` | Pramukh's final prompt (the `.rtf` is the original from Teams). |
| `inputs/prompt_with_sources.txt` | Kunal's update of that prompt (Nov 4): a clickable source link for every reason, point against, turning point, date to watch and chart. The graph follows this one. |
| `inputs/evaluation_cases/` | Kunal and Pramukh's 15 checked reports (Nov 5), the gold standard to test the graph against. Not used yet. |
| `inputs/gold_cases/<adsh>/` | Pramukh's 15 harness runs: `report.md` is the gold standard. |
| `outputs/cases/<adsh>/` | Graph output per case: `report.md`, `charts/`, `filings/`, and `state.json` (every step's result). |
| `outputs/judge/<adsh>.json` | The judge's result per case (`before_cash/` holds the results from before the cash step). |
| `outputs/JUDGE_SUMMARY.md` | The summary table of all 15 cases. |
| `outputs/llm_calls/` | Every saved prompt and answer from files mode. |

## The graph

```
setup_case → compute_numbers → choose_filings → get_passages → read_filings → make_charts → assess → write_report → check_report
                                                                                                         ↑               │
                                                                                                         └── problems ───┘
```

- **Code nodes** (no model): `setup_case`, `compute_numbers`, `choose_filings`, `get_passages`, `make_charts`, `check_report`.
- **LLM nodes**: `read_filings` (one call per 10-K/10-Q, plus one call for all the 8-Ks), `assess`, `write_report`.
- **The state** is one dict that every node adds to. `state.json` saves it, so you can see exactly what each step produced.

## How to run

Uses the `.venv-agent` environment: pandas, matplotlib, BeautifulSoup, requests, `langgraph`, `claude-agent-sdk`. Claude Code must be signed in.

```bash
cd langgraph_agent
../.venv-agent/bin/python code/run.py 0001078207-23-000108      # one case (about 4 minutes)
../.venv-agent/bin/python code/judge.py                          # compare every finished case with the harness report
```

**Using Claude in the app instead of the SDK:** run with `LLM_BACKEND=files`. Each LLM step then saves its prompt as `outputs/llm_calls/<adsh>_<step>_<id>.prompt.md` and stops. Claude in the app writes each answer to the matching `.answer.md`, and you run the same command again. Steps that already have answers are not asked again, so each run moves the graph forward: read → assess → write → (rewrite) → done. Answers stay on disk, so a rerun gives the same result.

```bash
LLM_BACKEND=files ../.venv-agent/bin/python code/run.py <adsh> ...   # run, write the answers, run again
```

## Results (15 cases, judged against the harness reports)

The full table is in [outputs/JUDGE_SUMMARY.md](outputs/JUDGE_SUMMARY.md). Averages, on a 1 to 5 scale: verdict agreement 4.60, coverage 3.93, consistency 3.60, overall 3.93. Critical-point recall is 0.72. Before the cash step, overall was 3.80.

- **Same verdict in 13 of 15 cases.** Surf Air (gold "unclear", graph "real risk") and TeraWulf (gold "false alarm", graph "unclear") are one step apart. With the cash step, TeraWulf now gives gold's own argument (93% of the loss is non-cash) and a low risk of about 3% against gold's 2%. It still says "unclear", because 3% is close to the band's 4% base rate.
- **Cash and runway are now computed in code.** The first run left the exact cash balance to the model, which guessed it from the text, so `compute_numbers` now takes cash, months of cash and the cash-adjusted loss from the filing's own XBRL numbers (`cash_numbers` in `code/steps.py`). After rerunning the 7 affected cases, critical-point recall rose for Creatd (0.50 to 0.67), Aerwins (0.25 to 0.75) and Loop Media (0.50 to 0.83). The first-run results are kept in `outputs/judge/before_cash/` and `outputs/cases/<adsh>/report_before_cash.md`.
- **Still missing:** Surf Air's $32.3M stock-comp reversal is a fourth-quarter item. The XBRL only gives the full-year net stock compensation (-$6.0M), so the graph still misses it. For iRobot, the graph doesn't net restricted cash or give the underlying loss.
- **Quote checks work.** 14 of the 15 graph reports pass every check. TeraWulf is still over the word limit (1,280 words) after 3 attempts.
- **Some change is run-to-run noise.** Canoo's rerun covers fewer of gold's points (coverage 4 to 3), although nothing in its numbers got worse.

Nogin, TeraWulf and Canoo ran through the Claude Agent SDK. The other 12 ran in files mode, answered by Claude in the app. Seven cases were rerun with the cash step: Creatd, Aerwins, Loop Media, iRobot, Surf Air, TeraWulf and Canoo. The other eight still have their first-run reports, since the judge didn't flag cash for them.

The numbers come from `agent/shared/financials.csv` and `risk_scores.csv` in this repo. The filings come from SEC EDGAR through the team's `sec_tools.py`.
