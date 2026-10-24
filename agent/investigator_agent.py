

# %%
import asyncio
import os

import pandas as pd
from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, ResultMessage, ToolUseBlock, query

AGENT_FOLDER = os.path.abspath(".")
PYTHON = os.path.abspath("../../.venv-agent/bin/python")  # has pandas, matplotlib, requests and BeautifulSoup

financials = pd.read_csv("shared/financials.csv")
scores = pd.read_csv("shared/risk_scores.csv")


# %%
def instructions(report, probability):
    # what the agent has and what to find out, but not how to analyze it
    cik, filed, out = int(report["cik"]), int(report["filed"]), f"cases/{report['adsh']}"
    return f"""You are the Investigator Agent of a bankruptcy early-warning system.
Our XGBoost model gave a financial report a probability that the company files for bankruptcy
within 365 days. Find out why, using both the numbers and the text, and tell the story of how the company got here.

The report: {report['name']}, {report['form']} for the period ending {report['ddate']}, filed {filed},
adsh {report['adsh']}, cik {cik}. Model probability: {probability:.3f} (about 1% of reports are followed by a bankruptcy).

What you can use:
- shared/financials.csv: every report of every company (one row per report). Income and cash flow columns
  are per year. Find this company by its cik, and its industry peers by the first 2 digits of sic.
- sec_tools.py, to get the company's filings from SEC EDGAR as they are (it doesn't read them for you):
    {PYTHON} sec_tools.py filings {cik} {filed}          lists its filings made before {filed} (10-K, 10-Q, 8-K, ...)
    {PYTHON} sec_tools.py download {cik} <adsh> {out}/filings      saves one filing's main document
  The documents are long HTML files. Read them your own way (Python, BeautifulSoup, search) and look for
  what matters: footnotes, going concern, debt and covenants, liquidity, risk factors, events in the 8-Ks.
- Python with pandas, matplotlib, requests and BeautifulSoup: {PYTHON}

Rules:
- Only use information filed on or before {filed}. Nothing later, and nothing you know about
  what happened to the company afterwards.
- Use only shared/financials.csv and sec_tools.py. Keep your files in {out}/, save your charts in
  {out}/charts/ and look at them.

Finish by writing {out}/report.md: why the probability is what it is, the main reasons in order with the numbers
and quotes behind each one, how the situation developed over time, the charts, and how sure you are.
Keep it short and plain."""


# %%
async def investigate(adsh):
    report = financials[financials["adsh"] == adsh].iloc[0]
    probability = float(scores.loc[scores["adsh"] == adsh, "probability"].iloc[0])
    os.makedirs(f"cases/{adsh}/charts", exist_ok=True)
    options = ClaudeAgentOptions(
        system_prompt=instructions(report, probability),
        model="claude-opus-5-5",
        cwd=AGENT_FOLDER,                                # the agent folder (shared/, sec_tools.py, cases/)
        tools=["Read", "Glob", "Grep", "Bash", "Write"],   # read files, run Python and sec_tools.py, write the report
        allowed_tools=["Read", "Glob", "Grep", "Bash", "Write"],
        setting_sources=[],                               # don't load my own Claude Code settings
        max_turns=80,
    )
    print(f"investigating {report['name']} ({adsh}), probability {probability:.3f}")
    async for message in query(prompt="Start the investigation.", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):  # print what the agent does as it goes
                    print("  ", block.name, str(block.input).replace("\n", " ")[:100])
        if isinstance(message, ResultMessage):
            print(f"  done in {message.num_turns} turns, {message.duration_ms / 1000:.0f}s")


# %%
# which reports to investigate: reports labeled 1 (a bankruptcy 8-K within 365 days after them).

if __name__ == "__main__":
    labels = pd.read_csv("../model_dataframe_2023_Q1_to_2026_Q3.txt", sep="\t", low_memory=False)
    labeled_1 = labels.loc[(labels["Bankruptcy"] == 1) & (labels["already_bankrupt"] == False), "adsh"]
    picked = scores[scores["adsh"].isin(labeled_1)].sort_values("probability", ascending=False)
    for adsh in picked["adsh"].head(3):
        if not os.path.exists(f"cases/{adsh}/report.md"):
            asyncio.run(investigate(adsh))
