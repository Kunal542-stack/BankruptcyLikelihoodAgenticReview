# The code steps of the graph: everything that has one right answer.
# Each function takes plain values and returns plain values (dicts, lists, strings).
import bisect
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the langgraph_agent folder
#the team's agent folder: agent/ next to this folder in the repo, push_to_main/agent/ on my machine
TEAM_AGENT = os.path.join(ROOT, "..", "agent")
if not os.path.exists(TEAM_AGENT):
    TEAM_AGENT = os.path.join(ROOT, "..", "push_to_main", "agent")
SHARED = os.path.join(TEAM_AGENT, "shared")
sys.path.insert(0, TEAM_AGENT)
import sec_tools  # the team's SEC helper: company_filings(cik) and download(cik, adsh, folder)

INPUTS = ["total_assets", "current_assets", "current_liabilities", "total_liabilities",
          "revenue", "net_income", "operating_income", "operating_cash_flow"]

# from Pramukh's prompt: how often each score band was really followed by a bankruptcy
BANDS = [(0.7, "above 0.7", 18.0), (0.5, "0.5-0.7", 4.0), (0.2, "0.2-0.5", 2.0), (0.0, "below 0.2", 0.3)]

# 8-K items worth reading, and the ones to skip when they are the only items (from the prompt)
KEEP_8K_ITEMS = {"1.01", "1.02", "1.03", "2.01", "2.03", "2.04", "2.06", "3.01", "4.01", "4.02", "5.02"}

# words the prompt asks to look for in a 10-K or 10-Q; a passage is kept around each hit
KEYWORDS = ["substantial doubt", "going concern", "liquidity and capital resources", "covenant", "waiver",
            "forbearance", "default", "amendment", "matur", "subsequent event", "revolv", "borrowing base",
            "restricted cash", "impairment", "stock-based compensation", "share-based compensation",
            "defaults upon senior securities", "report of independent registered", "restructuring",
            "delist", "minimum bid", "listing rule", "chapter 11", "bankruptcy", "sufficient to fund", "runway"]


# ---------- setup_case ----------
def load_case(adsh):
    fin = pd.read_csv(os.path.join(SHARED, "financials.csv"))
    scores = pd.read_csv(os.path.join(SHARED, "risk_scores.csv"))
    row = fin[fin.adsh == adsh].iloc[0]
    score = float(scores.loc[scores.adsh == adsh, "probability"].iloc[0])
    band, base_rate = next((name, rate) for low, name, rate in BANDS if score >= low)
    return {"adsh": adsh, "cik": int(row.cik), "name": row["name"], "form": row.form, "fp": row.fp,
            "period_end": str(int(row.ddate)), "filed": str(int(row.filed)), "sic": int(row.sic),
            "score": round(score, 3), "band": band, "base_rate_pct": base_rate}


# ---------- compute_numbers ----------
def compute_numbers(case):
    fin = pd.read_csv(os.path.join(SHARED, "financials.csv"))
    # only what was filed on or before the report (the file also has later reports)
    fin = fin[fin.filed <= int(case["filed"])].copy()
    fin["period"] = pd.to_datetime(fin.ddate.astype(str))
    company = fin[fin.cik == case["cik"]].sort_values("period")
    this = company[company.adsh == case["adsh"]].iloc[0]

    # the year before: the comparison column of this same filing (every 10-K and 10-Q reports the prior year too)
    year_before = year_before_from_filing(case)

    # peers: same industry (first 2 SIC digits), period end within 3 months, latest report of each
    peers = fin[(fin.sic // 100 == case["sic"] // 100) & (fin.cik != case["cik"])
                & ((fin.period - this.period).abs().dt.days <= 92)]
    peers = peers.sort_values("filed").groupby("cik").tail(1)

    rows = []
    for col in INPUTS:
        value = this[col]
        share = float(value / this.total_assets) if pd.notna(value) and this.total_assets else None
        if col == "total_assets":
            # size: compare dollars, since assets as a share of assets is always 100%
            pct = round(float((peers.total_assets < value).mean() * 100)) if len(peers) else None
        else:
            peer_share = (peers[col] / peers.total_assets).dropna()
            pct = round(float((peer_share < share).mean() * 100)) if share is not None and len(peer_share) else None
        rows.append({"input": col, "this_report_musd": musd(value),
                     "year_before_musd": musd(year_before.get(col)),
                     "share_of_assets_pct": round(share * 100, 1) if share is not None else None,
                     "peer_percentile": pct})
    extras = {
        "liabilities_to_assets": ratio(this.total_liabilities, this.total_assets),
        "current_ratio": ratio(this.current_assets, this.current_liabilities),
        "peer_count": int(len(peers)),
        "peer_median_liabilities_to_assets": round(float((peers.total_liabilities / peers.total_assets).median()), 2),
        "peer_median_current_ratio": round(float((peers.current_assets / peers.current_liabilities).median()), 2),
        "missing_inputs": [c for c in INPUTS if pd.isna(this[c])],
        "year_before_note": "from the prior-year column of this filing (XBRL); income and cash flow annualized",
    }
    history = company[["form", "fp", "ddate", "filed"] + INPUTS].to_dict("records")
    peer_rows = peers[["name", "sic", "ddate", "filed"] + INPUTS].to_dict("records")
    return {"inputs": rows, "extras": extras, "cash": cash_numbers(case), "history": history, "peers": peer_rows}


# the same tags (and backups) the dataframe was built with
TAGS = {"total_assets": ["Assets"], "current_assets": ["AssetsCurrent"], "current_liabilities": ["LiabilitiesCurrent"],
        "total_liabilities": ["Liabilities"],
        "revenue": ["RevenueFromContractWithCustomerExcludingAssessedTax", "Revenues",
                    "RevenueFromContractWithCustomerIncludingAssessedTax", "SalesRevenueNet"],
        "net_income": ["NetIncomeLoss", "ProfitLoss"], "operating_income": ["OperatingIncomeLoss"],
        "operating_cash_flow": ["NetCashProvidedByUsedInOperatingActivities",
                                "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"]}
BALANCE = {"total_assets", "current_assets", "current_liabilities", "total_liabilities"}


def year_before_from_filing(case):
    # SEC's companyfacts lists every number a company reported, with the filing (accn) it came from.
    # Here: the numbers THIS filing reports for the period one year earlier
    facts = company_facts(case["cik"])
    end = datetime.strptime(case["period_end"], "%Y%m%d")
    target = end - timedelta(days=365)
    quarters = {"Q1": 1, "Q2": 2, "Q3": 3}.get(case["fp"], 4) if case["form"].startswith("10-Q") else 4
    out = {}

    cutoff = datetime.strptime(case["filed"], "%Y%m%d")

    def find(tag, flow, same_filing=True):
        # same_filing=False: a 10-Q's balance sheet compares with the last year end, not a year before,
        # so that value comes from the earlier filing that reported it (filed before the cutoff)
        candidates = sorted(facts.get(tag, {}).get("units", {}).get("USD", []), key=lambda f: f.get("filed", ""), reverse=True)
        for f in candidates:
            if abs((datetime.strptime(f["end"], "%Y-%m-%d") - target).days) > 15:
                continue
            if same_filing and f.get("accn") != case["adsh"]:
                continue
            if not same_filing and datetime.strptime(f.get("filed", "2100-01-01"), "%Y-%m-%d") > cutoff:
                continue
            if not flow:
                if "start" not in f:
                    return f["val"]
            elif "start" in f:
                months = round((datetime.strptime(f["end"], "%Y-%m-%d") - datetime.strptime(f["start"], "%Y-%m-%d")).days / 30.4)
                if round(months / 3) == quarters:
                    return f["val"] * 4 / quarters  # per year, like the model's data
        return None

    for col, tags in TAGS.items():
        for same_filing in (True, False):
            for tag in tags:
                value = find(tag, col not in BALANCE, same_filing)
                if value is not None:
                    out[col] = value
                    break
            if col in out:
                break
    if "total_liabilities" not in out:
        for same_filing in (True, False):
            le = find("LiabilitiesAndStockholdersEquity", False, same_filing)
            eq = (find("StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest", False, same_filing)
                  or find("StockholdersEquity", False, same_filing))
            if le is not None and eq is not None:
                out["total_liabilities"] = le - eq
                break
    return out


# cash on hand, and the non-cash charges in the loss (stock compensation, depreciation, impairment)
CASH_TAGS = ["CashAndCashEquivalentsAtCarryingValue", "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "Cash"]
NON_CASH_TAGS = {"stock_compensation": ["ShareBasedCompensation", "AllocatedShareBasedCompensationExpense"],
                 "depreciation_amortization": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization",
                                               "DepreciationAmortizationAndAccretionNet", "Depreciation"],
                 "impairment": ["AssetImpairmentCharges", "GoodwillAndIntangibleAssetImpairment", "GoodwillImpairmentLoss",
                                "ImpairmentOfLongLivedAssetsHeldForUse"]}


def cash_numbers(case):
    # How long the cash lasts, and how much of the loss is real cash. All from THIS filing's own numbers,
    # so nobody has to guess them from the text. The prompt asks for the last quarter's burn too, and for the
    # non-cash adjustment to be done the same way every year, so the year before gets the same split.
    facts = company_facts(case["cik"])
    cash = fact(facts, case, CASH_TAGS, flow=False)
    flow = fact(facts, case, TAGS["operating_cash_flow"], flow=True)
    cash = None if cash is None else cash["val"]
    months = None if flow is None else period_months(flow)
    burn = -flow["val"] / months if flow and flow["val"] < 0 else None              # cash used per month, period to date
    last_q = None if flow is None else last_quarter_flow(facts, case, flow)
    burn_q = -last_q / 3 if last_q is not None and last_q < 0 else None              # cash used per month, last quarter

    return {
        "cash_usd": None if cash is None else int(cash),  # exact dollars: small balances matter
        "period_months": months,
        "operating_cash_flow_musd": None if flow is None else musd(flow["val"]),
        "monthly_cash_burn_musd": None if burn is None else round(burn / 1e6, 2),
        "months_of_cash": None if burn is None or cash is None else round(cash / burn, 2),
        "last_quarter_operating_cash_flow_musd": musd(last_q),
        "last_quarter_monthly_burn_musd": None if burn_q is None else round(burn_q / 1e6, 2),
        "months_of_cash_at_last_quarter_burn": None if burn_q is None or cash is None else round(cash / burn_q, 2),
        "this_period": loss_split(facts, case, months, years_back=0),
        "same_period_year_before": loss_split(facts, case, months, years_back=1),
        "note": "from this filing's XBRL (not annualized); months_of_cash = cash / monthly burn; the last quarter = "
                "this period to date minus the period to date one quarter earlier; non-cash charges counted: stock "
                "compensation, depreciation and amortization, impairment (a negative stock compensation is a "
                "reversal that makes the loss look smaller)",
    }


def loss_split(facts, case, months, years_back):
    # the loss of one period and how much of it is non-cash; the same split for every year
    if not months:
        return {}
    net = fact(facts, case, TAGS["net_income"], True, years_back, months)
    non_cash = {}
    for name, tags in NON_CASH_TAGS.items():
        f = fact(facts, case, tags, True, years_back, months)
        if f is not None:
            non_cash[name] = f["val"]
    loss, total = (None if net is None else net["val"]), sum(non_cash.values())
    return {
        "months": months,
        "net_income_musd": musd(loss),
        "non_cash_charges_musd": {name: musd(v) for name, v in non_cash.items()},
        "cash_adjusted_net_income_musd": None if loss is None else musd(loss + total),
        "non_cash_share_of_loss_pct": round(total / -loss * 100) if loss is not None and loss < 0 else None,
    }


def fact(facts, case, tags, flow, years_back=0, months=None):
    # one number THIS filing reports, at its period end or (years_back=1) the same date a year earlier, which every
    # 10-K and 10-Q reports as its comparison column. For a flow (income, cash flow): the period to date, or a
    # period of `months` months. Within a week of the date: some fiscal years end on a Saturday (Dec 28, not Dec 31).
    end = datetime.strptime(case["period_end"], "%Y%m%d") - timedelta(days=365 * years_back)
    for tag in tags:
        found = [f for f in facts.get(tag, {}).get("units", {}).get("USD", [])
                 if f.get("accn") == case["adsh"] and ("start" in f) == flow
                 and abs((datetime.strptime(f["end"], "%Y-%m-%d") - end).days) <= 7]
        if flow and months:
            found = [f for f in found if period_months(f) == months]
        if found:
            return min(found, key=lambda f: f.get("start", ""))  # for a flow, the longest period
    return None


def period_months(f):
    return round((datetime.strptime(f["end"], "%Y-%m-%d") - datetime.strptime(f["start"], "%Y-%m-%d")).days / 30.4)


def last_quarter_flow(facts, case, flow):
    # cash flow statements are year to date, so the last quarter = this period to date minus the period to date
    # one quarter earlier, which the previous 10-Q reported (filed before this report)
    months = period_months(flow)
    if months <= 3:
        return flow["val"]
    cutoff = datetime.strptime(case["filed"], "%Y%m%d")
    for tag in TAGS["operating_cash_flow"]:
        for f in facts.get(tag, {}).get("units", {}).get("USD", []):
            if (f.get("start") == flow["start"] and period_months(f) == months - 3
                    and datetime.strptime(f.get("filed", "2100-01-01"), "%Y-%m-%d") <= cutoff):
                return flow["val"] - f["val"]
    return None


FACTS = {}


def company_facts(cik):
    # every number the company reported to the SEC, with the filing (accn) it came from; fetched once per company
    if cik not in FACTS:
        url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
        FACTS[cik] = requests.get(url, headers=sec_tools.HEADERS, timeout=60).json()["facts"].get("us-gaap", {})
    return FACTS[cik]


def musd(x):
    return None if x is None or pd.isna(x) else round(float(x) / 1e6, 1)


def ratio(a, b):
    return None if pd.isna(a) or pd.isna(b) or b == 0 else round(float(a / b), 2)


# ---------- choose_filings ----------
def choose_filings(case):
    table = sec_tools.company_filings(case["cik"])
    filed = datetime.strptime(case["filed"], "%Y%m%d")
    table["day"] = pd.to_datetime(table.date)
    table = table[table.day <= filed]

    chosen = []
    # the report itself (it may be missing from the list, then it is downloaded by its adsh)
    chosen.append({"adsh": case["adsh"], "form": case["form"], "date": str(filed.date()), "why": "this report"})
    # the latest 10-K before it, and every 10-Q since
    tenks = table[(table.form == "10-K") & (table.adsh != case["adsh"])].sort_values("day")
    if len(tenks):
        k = tenks.iloc[-1]
        chosen.append({"adsh": k.adsh, "form": k.form, "date": k.date, "why": "latest 10-K before"})
        tenqs = table[(table.form == "10-Q") & (table.day > k.day) & (table.adsh != case["adsh"])]
        for q in tenqs.itertuples():
            chosen.append({"adsh": q.adsh, "form": q.form, "date": q.date, "why": "10-Q since the 10-K"})
    # 8-Ks of the last 18 months with an item worth reading, and any late-filing notice
    recent = table[table.day >= filed - timedelta(days=548)]
    for f in recent.itertuples():
        items = set(str(f.items).split(","))
        if f.form in ("8-K", "8-K/A") and items & KEEP_8K_ITEMS:
            chosen.append({"adsh": f.adsh, "form": f.form, "date": f.date, "why": "8-K items " + str(f.items)})
        if f.form in ("NT 10-K", "NT 10-Q"):
            chosen.append({"adsh": f.adsh, "form": f.form, "date": f.date, "why": "late-filing notice"})
    return chosen


def other_filings(case, chosen, limit=40):
    # the filings the rule left out (older reports, other 8-Ks), newest first. The LLM may ask for some of them,
    # since the prompt says "use older filings only to see when a problem started"
    table = sec_tools.company_filings(case["cik"])
    table = table[pd.to_datetime(table.date) <= datetime.strptime(case["filed"], "%Y%m%d")]
    forms = ["10-K", "10-Q", "10-K/A", "10-Q/A", "8-K", "8-K/A", "NT 10-K", "NT 10-Q"]
    taken = {f["adsh"] for f in chosen}
    rest = table[table.form.isin(forms) & ~table.adsh.isin(taken)].sort_values("date", ascending=False).head(limit)
    return [{"adsh": r.adsh, "form": r.form, "date": r.date, "items": str(r.items)} for r in rest.itertuples()]


# ---------- get_passages ----------
def download(cik, adsh, folder):
    # downloads the filing's main document once and returns its path
    os.makedirs(folder, exist_ok=True)
    for name in os.listdir(folder):
        if name.startswith(adsh + "_") and not name.endswith(".txt"):
            return os.path.join(folder, name)
    try:
        sec_tools.download(cik, adsh, folder)
    except Exception:
        # the report may be missing from the company's recent-filings list: find its main document on the index page
        index = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/{adsh}-index.htm"
        page = BeautifulSoup(requests.get(index, headers=sec_tools.HEADERS, timeout=60).text, "html.parser")
        link = next(a["href"] for a in page.find_all("a", href=True) if a["href"].endswith(".htm") and "/Archives/" in a["href"])
        document = link.split("/")[-1].replace("ix?doc=", "")
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/{document}"
        open(os.path.join(folder, f"{adsh}_{document}"), "wb").write(requests.get(url, headers=sec_tools.HEADERS, timeout=60).content)
    for name in os.listdir(folder):
        if name.startswith(adsh + "_") and not name.endswith(".txt"):
            return os.path.join(folder, name)


def filing_url(cik, path):
    # the filing's main document on SEC EDGAR, from the saved file name (<adsh>_<document>)
    adsh, document = os.path.basename(path).split("_", 1)
    return f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/{document}"


def html_to_lines(path):
    # text with one table row per line; words split over several <span>s are joined back
    soup = BeautifulSoup(open(path, "rb").read(), "html.parser")
    for tag in soup.find_all(["ix:header", "script", "style"]):
        tag.decompose()
    for tag in soup.find_all(["td", "th"]):
        tag.append(" ")
    for tag in soup.find_all(["p", "div", "tr", "li", "br", "table", "h1", "h2", "h3", "h4"]):
        tag.append("\n")
    lines = [re.sub(r"\s+", " ", line).strip() for line in soup.get_text("").split("\n")]
    return [line for line in lines if line]


def passages(lines, form, limit=90000):
    # 10-K / 10-Q: the lines around each keyword hit, plus the cash flow statement
    # 8-K: the item text;  NT form: the text
    if form.startswith("8-K"):
        text = "\n".join(lines)
        start = re.search(r"\bItem\s+\d\.\d\d", text)
        end = re.search(r"\bSIGNATURES?\b", text)
        return text[start.start() if start else 0: end.start() if end else None][:15000]
    if form.startswith("NT"):
        return "\n".join(lines)[:8000]
    keep = set()
    for i, line in enumerate(lines):
        low = line.lower()
        if any(k in low for k in KEYWORDS):
            keep.update(range(max(0, i - 2), min(len(lines), i + 8)))
        if "cash flows from operating activities" in low and len(line) < 80:
            keep.update(range(i, min(len(lines), i + 60)))
    return join_lines(lines, keep)[:limit]


def search(lines, terms, limit=20000):
    # the lines around each hit of the words the LLM asked for (the same windows as passages() uses)
    terms = [t.lower().strip() for t in terms if len(t.strip()) > 2]
    keep = set()
    for i, line in enumerate(lines):
        if any(t in line.lower() for t in terms):
            keep.update(range(max(0, i - 2), min(len(lines), i + 8)))
    return join_lines(lines, keep)[:limit]


def join_lines(lines, keep):
    text, last = "", -2
    for i in sorted(keep):
        if i != last + 1:
            text += "\n...\n"
        text += lines[i] + "\n"
        last = i
    return text


# ---------- draw_chart ----------
# The LLM decides which charts to make and writes the matplotlib code. This runs that code in a separate Python
# process, with only the case's data, and saves the picture. A simple guard, not a real sandbox: the code may only
# use pandas, numpy and matplotlib, can't open files or the network, and is stopped after 60 seconds.
BLOCKED = [r"\bopen\s*\(", r"\bexec\s*\(", r"\beval\s*\(", r"__import__", r"\bimport\s+(?!pandas|numpy|matplotlib)",
           r"\bfrom\s+(?!pandas|numpy|matplotlib)\w+\s+import", r"\bos\.", r"\bsys\.", r"subprocess", r"socket",
           r"requests", r"urllib", r"shutil", r"pathlib", r"pickle", r"\.to_(csv|json|excel|pickle|parquet)\s*\("]

CHART_HEADER = """import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
history = pd.read_csv("data/history.csv")  # the company's reports up to this one: the 8 inputs (per year, 10-Qs annualized)
peers = pd.read_csv("data/peers.csv")      # same-industry peers at about the same date: the same 8 inputs
facts = json.load(open("data/facts.json"))  # case, numbers, cash, assessment (verdict, reasons, timeline)
"""


def save_chart_data(state, folder):
    # the data the chart code can read
    os.makedirs(os.path.join(folder, "data"), exist_ok=True)
    # (with the column names even when a table is empty, so the chart code can always load it)
    pd.DataFrame(state["numbers"]["history"], columns=["form", "fp", "ddate", "filed"] + INPUTS).to_csv(
        os.path.join(folder, "data", "history.csv"), index=False)
    pd.DataFrame(state["numbers"]["peers"], columns=["name", "sic", "ddate", "filed"] + INPUTS).to_csv(
        os.path.join(folder, "data", "peers.csv"), index=False)
    facts = {"case": state["case"], "inputs": state["numbers"]["inputs"], "extras": state["numbers"]["extras"],
             "cash": state["numbers"]["cash"], "assessment": state["assessment"]}
    json.dump(facts, open(os.path.join(folder, "data", "facts.json"), "w"), indent=1, default=str)


def draw_chart(code, name, folder):
    # runs the LLM's chart code; returns "" if the picture was saved, else what went wrong
    for pattern in BLOCKED:
        if re.search(pattern, code):
            return f"the code was not run: it uses something that is not allowed ({pattern})"
    script = os.path.join(folder, name + ".py")
    open(script, "w").write(CHART_HEADER + "\n" + code + f"\n\nplt.savefig({name + '.png'!r}, dpi=110, bbox_inches='tight')\n")
    try:
        run = subprocess.run([sys.executable, script], cwd=folder, capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired:
        return "the code took longer than 60 seconds"
    if run.returncode != 0:
        return run.stderr.strip()[-1500:]
    return ""


# ---------- check_report ----------
def normalize(text):
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"), ("\xa0", " ")]:
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip().lower()


def check_report(report, all_text, known, filed, urls, limit_words=1200):
    # all_text: the saved filings; known: every number the agent computed or found (numbers, cash, findings);
    # urls: the SEC links of the filings that were read
    problems = missing_links(report, urls)
    corpus = normalize(all_text)
    for quote in re.findall(r"[\"“]([^\"”\n]{20,})[\"”]", report):
        pieces = [p.strip(" .,;:") for p in re.split(r"\.\.\.|…", quote) if len(p.strip()) > 12]
        if pieces and not all(normalize(p) in corpus for p in pieces):
            problems.append(f'quote not found word for word in the saved filings: "{quote[:150]}"')
    words = len(report.split())
    if words > limit_words:
        problems.append(f"the report has {words} words; the limit is {limit_words}")
    untraced = untraced_dollars(report, all_text + " " + known)
    if untraced:
        problems.append("these dollar amounts can't be traced to the filings or the computed numbers: "
                        + ", ".join(untraced[:8]) + ". Correct them, drop them, or write the calculation "
                        "inline (e.g. \"$2.49M + $2.27M = $4.76M\")")
    cutoff = datetime.strptime(filed, "%Y%m%d")
    used = report.split("Filings used")[-1] if "Filings used" in report else ""
    for d in re.findall(r"\b(20\d\d-\d\d-\d\d)\b", used):
        if datetime.strptime(d, "%Y-%m-%d") > cutoff:
            problems.append(f"a filing dated {d} is after the report date")
    return problems


# "give a clickable link for a verifiable source ... for all reasons": every item in these parts of the report must
# link to its source, and a link to SEC must be one of the filings that were read. Dates to watch are only checked for
# wrong links, since a future event (the next 10-Q) may have no filing yet
LINKED_PARTS = ["main reasons", "evidence against", "how it developed"]
CHECKED_PARTS = LINKED_PARTS + ["dates to watch"]
LINK = re.compile(r"\]\(([^)\s]+)\)")
REF_LINK = re.compile(r"\]\[([^\]]+)\]")  # [10-Q][q3], with "[q3]: https://..." on a line of its own


def missing_links(report, urls):
    problems = []
    refs = dict(re.findall(r"^\s*\[([^\]]+)\]:\s*(\S+)", report, re.M))
    for part in re.split(r"\n(?=#+ )", report):
        title = part.split("\n", 1)[0].lstrip("# ").strip().lower()
        if not any(title.startswith(p) for p in CHECKED_PARTS):
            continue
        must_link = any(title.startswith(p) for p in LINKED_PARTS)
        # one item = a "-" or "1." line plus the lines that continue it
        items, item = [], None
        for line in part.split("\n")[1:]:
            if re.match(r"\s*(?:[-*]|\d+\.)\s+", line):
                item = [line]
                items.append(item)
            elif line.strip() and item is not None:
                item.append(line)
            else:
                item = None
        for text in (" ".join(i).strip() for i in items):
            links = LINK.findall(text) + [refs.get(r, "") for r in REF_LINK.findall(text)]
            # shortcut references: a bare [10-Q] that is defined at the bottom
            links += [refs[r] for r in re.findall(r"\[([^\]]+)\](?![(\[:])", text) if r in refs]
            if not links and must_link:
                problems.append(f'no source link in "{title}": "{text[:120]}"')
            for url in links:
                if not url or (url.startswith("http") and url not in urls):
                    problems.append(f"this link is not one of the filings that were read: {url or '(undefined reference)'}")
    return problems


# "recompute every number you cite": every dollar amount in the report must be found in the filings or in the
# computed numbers (allowing for rounding and for tables in thousands or millions), or come after an "=" sign
SCALE = {"thousand": 1e3, "k": 1e3, "million": 1e6, "m": 1e6, "mm": 1e6, "billion": 1e9, "bn": 1e9, "b": 1e9}
DOLLARS = re.compile(r"(=\s*)?[-−]?\$\s?(\d[\d,]*(?:\.\d+)?)\s?(thousand|million|billion|bn|mm|[kmb])?\b", re.I)


def untraced_dollars(report, sources):
    known = set()
    for n in re.findall(r"\d[\d,]*(?:\.\d+)?", sources):
        v = float(n.replace(",", ""))
        known.update({v, v * 1e3, v * 1e6, v * 1e9})
    known = sorted(known)
    missing = []
    for m in DOLLARS.finditer(report):
        if m.group(1):  # the result of a calculation written out in the report
            continue
        digits, unit = m.group(2), (m.group(3) or "").lower()
        value = float(digits.replace(",", "")) * SCALE.get(unit, 1)
        decimals = len(digits.split(".")[1]) if "." in digits else 0
        tolerance = 0.5 * 10 ** -decimals * SCALE.get(unit, 1) + 1e-6  # rounding to the digits shown
        i = bisect.bisect_left(known, value - tolerance)
        if not (i < len(known) and known[i] <= value + tolerance):
            missing.append(m.group(0).strip())
    return missing
