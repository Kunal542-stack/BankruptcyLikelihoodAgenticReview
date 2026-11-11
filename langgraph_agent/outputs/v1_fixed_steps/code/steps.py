# The code steps of the graph: everything that has one right answer.
# Each function takes plain values and returns plain values (dicts, lists, strings).
import os
import re
import sys
from datetime import datetime, timedelta

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the langgraph_agent folder
SHARED = os.path.join(ROOT, "..", "push_to_main", "agent", "shared")
sys.path.insert(0, os.path.join(ROOT, "..", "push_to_main", "agent"))
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
    return {"inputs": rows, "extras": extras, "cash": cash_numbers(case), "history": history}


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
    # How long the cash lasts, and how much of the loss is real cash. Both come from THIS filing's own numbers,
    # for its period to date (e.g. 9 months for a Q3 10-Q), so nobody has to guess them from the text.
    facts = company_facts(case["cik"])
    cash, _ = this_filing_value(facts, case, CASH_TAGS, flow=False)
    cash_flow, months = this_filing_value(facts, case, TAGS["operating_cash_flow"], flow=True)
    net_income, _ = this_filing_value(facts, case, TAGS["net_income"], flow=True)

    burn = -cash_flow / months if cash_flow is not None and cash_flow < 0 else None  # cash used per month
    non_cash = {}
    for name, tags in NON_CASH_TAGS.items():
        value, _ = this_filing_value(facts, case, tags, flow=True)
        if value is not None:
            non_cash[name] = value
    total_non_cash = sum(non_cash.values())

    return {
        "cash_usd": None if cash is None else int(cash),  # exact dollars: small balances matter
        "period_months": months,
        "operating_cash_flow_musd": musd(cash_flow),
        "monthly_cash_burn_musd": None if burn is None else round(burn / 1e6, 2),
        "months_of_cash": None if burn is None or cash is None else round(cash / burn, 2),
        "net_income_musd": musd(net_income),
        "non_cash_charges_musd": {name: musd(v) for name, v in non_cash.items()},
        "cash_adjusted_net_income_musd": None if net_income is None else musd(net_income + total_non_cash),
        "non_cash_share_of_loss_pct": (round(total_non_cash / -net_income * 100)
                                       if net_income is not None and net_income < 0 else None),
        "note": "from this filing's XBRL, for its period to date (not annualized); months_of_cash = cash / monthly "
                "burn over that period; non-cash charges counted: stock compensation, depreciation and amortization, "
                "impairment (a negative stock compensation is a reversal that makes the loss look smaller)",
    }


def this_filing_value(facts, case, tags, flow):
    # the value THIS filing reports at its period end; for a flow (income, cash flow) the longest period,
    # which is the year to date. Returns (value, months of the period).
    # (within a week of the period end: some fiscal years end on a Saturday, e.g. Dec 28 instead of Dec 31)
    end = datetime.strptime(case["period_end"], "%Y%m%d")
    for tag in tags:
        found = [f for f in facts.get(tag, {}).get("units", {}).get("USD", [])
                 if f.get("accn") == case["adsh"] and ("start" in f) == flow
                 and abs((datetime.strptime(f["end"], "%Y-%m-%d") - end).days) <= 7]
        if not found:
            continue
        if not flow:
            return found[0]["val"], None
        f = min(found, key=lambda f: f["start"])
        months = round((datetime.strptime(f["end"], "%Y-%m-%d") - datetime.strptime(f["start"], "%Y-%m-%d")).days / 30.4)
        return f["val"], months
    return None, None


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


# ---------- get_passages ----------
def download(cik, adsh, folder):
    # downloads the filing's main document once and returns its path
    os.makedirs(folder, exist_ok=True)
    for name in os.listdir(folder):
        if name.startswith(adsh + "_"):
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
        if name.startswith(adsh + "_"):
            return os.path.join(folder, name)


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
    text, last = "", -2
    for i in sorted(keep):
        if i != last + 1:
            text += "\n...\n"
        text += lines[i] + "\n"
        last = i
    return text[:limit]


# ---------- make_charts ----------
def make_charts(numbers, folder):
    os.makedirs(folder, exist_ok=True)
    h = pd.DataFrame(numbers["history"])
    h["label"] = h.fp + " " + (h.ddate // 10000).astype(str)
    made = []

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(h.label, h.revenue / 1e6, marker="o", label="Revenue")
    ax.plot(h.label, h.net_income / 1e6, marker="o", label="Net income")
    ax.axhline(0, color="black", linewidth=0.7)
    ax.set_ylabel("$M per year (10-Qs annualized)")
    ax.set_title("Revenue and net income")
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(folder, "1_revenue_net_income.png"), dpi=110)
    plt.close()
    made.append(("charts/1_revenue_net_income.png", "Revenue and net income over time"))

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.bar(h.label, h.operating_cash_flow / 1e6, color=["tab:red" if v < 0 else "tab:green" for v in h.operating_cash_flow.fillna(0)])
    ax.axhline(0, color="black", linewidth=0.7)
    ax.set_ylabel("$M per year (10-Qs annualized)")
    ax.set_title("Operating cash flow")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(folder, "2_operating_cash_flow.png"), dpi=110)
    plt.close()
    made.append(("charts/2_operating_cash_flow.png", "Operating cash flow over time"))

    fig, ax = plt.subplots(figsize=(7, 3.5))
    ax.plot(h.label, h.total_assets / 1e6, marker="o", label="Total assets")
    ax.plot(h.label, h.total_liabilities / 1e6, marker="o", label="Total liabilities")
    ax.set_ylabel("$M")
    ax.set_title("Liabilities against assets")
    ax.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(os.path.join(folder, "3_liabilities_vs_assets.png"), dpi=110)
    plt.close()
    made.append(("charts/3_liabilities_vs_assets.png", "Total liabilities against total assets"))
    return made


# ---------- check_report ----------
def normalize(text):
    for a, b in [("’", "'"), ("‘", "'"), ("“", '"'), ("”", '"'), ("–", "-"), ("—", "-"), ("\xa0", " ")]:
        text = text.replace(a, b)
    return re.sub(r"\s+", " ", text).strip().lower()


def check_report(report, all_text, filed, limit_words=1200):
    problems = []
    corpus = normalize(all_text)
    for quote in re.findall(r"[\"“]([^\"”\n]{20,})[\"”]", report):
        pieces = [p.strip(" .,;:") for p in re.split(r"\.\.\.|…", quote) if len(p.strip()) > 12]
        if pieces and not all(normalize(p) in corpus for p in pieces):
            problems.append(f'quote not found word for word in the saved filings: "{quote[:150]}"')
    words = len(report.split())
    if words > limit_words:
        problems.append(f"the report has {words} words; the limit is {limit_words}")
    cutoff = datetime.strptime(filed, "%Y%m%d")
    used = report.split("Filings used")[-1] if "Filings used" in report else ""
    for d in re.findall(r"\b(20\d\d-\d\d-\d\d)\b", used):
        if datetime.strptime(d, "%Y-%m-%d") > cutoff:
            problems.append(f"a filing dated {d} is after the report date")
    return problems
