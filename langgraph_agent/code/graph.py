# The investigator agent as a LangGraph graph.
# Each node does one step and returns the values it adds to the shared state.
# See docs/PROMPT_TO_GRAPH.md for how each node comes from Pramukh's prompt.
#
# Code does what has one right answer (numbers, downloads, searching, drawing, checking).
# The LLM decides wherever the prompt leaves the agent a choice: what to read next, what to chart, what to write.
import json
import os
import shutil
from typing import TypedDict

from langgraph.graph import END, StateGraph

import prompts
import steps
from llm import ask_llm, ask_llm_for_json, ask_many_for_json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the langgraph_agent folder
CASES = os.path.join(ROOT, "outputs", "cases")
MAX_READ_ROUNDS = 3   # extra reading rounds the LLM may ask for
MAX_CHART_STEPS = 8   # chart decisions (new, fix, drop) before the report is written anyway
MAX_WRITES = 3        # write_report runs at most this often


class State(TypedDict, total=False):
    adsh: str            # the report to investigate (the only input)
    folder: str          # where this case's files go
    case: dict           # company, form, dates, score, band, base rate
    numbers: dict        # the 8 inputs vs the year before and peers, ratios, cash and runway, history, peers
    filings: list        # the filings read: chosen by the rule, plus any older ones the LLM asked for
    other_filings: list  # the filings the rule left out (the LLM may ask for some)
    texts: dict          # adsh -> {"label", "passages"}; the full text of each filing is saved to disk
    findings: list       # what each filing says, with quotes
    read_rounds: int     # how many times decide_more ran
    more: dict           # the LLM's last decision: done, or what to search and which filings to add
    new_text: str        # the passages search_more found for read_more
    assessment: dict     # verdict, own risk, reasons, evidence against, timeline ...
    chart_plan: dict     # the LLM's last chart decision: new, fix, drop or done, with its code
    chart_steps: int     # how many chart decisions so far
    chart_log: list      # every chart tried: its point, caption, code, status (ok, failed, dropped)
    chart_last: dict     # what the last drawing gave: the chart number and any error
    charts: list         # (path, caption) of the charts kept for the report
    report: str          # the markdown report
    problems: list       # what check_report found wrong
    attempts: int        # how many times write_report ran


def filing_lines(state, f):
    # the filing as text lines: downloaded and converted once, then read from disk
    path = steps.download(state["case"]["cik"], f["adsh"], os.path.join(state["folder"], "filings"))
    txt = path.rsplit(".", 1)[0] + ".txt"
    if not os.path.exists(txt):
        # the full text is kept on disk for searching and for the quote check; only passages go to the model
        open(txt, "w").write("\n".join(steps.html_to_lines(path)))
    return open(txt).read().split("\n")


# ---------- the facts: code ----------
def setup_case(state):
    folder = os.path.join(CASES, state["adsh"])
    shutil.rmtree(os.path.join(folder, "charts"), ignore_errors=True)  # the charts are made fresh every run
    os.makedirs(folder, exist_ok=True)
    return {"folder": folder, "case": steps.load_case(state["adsh"]), "attempts": 0, "read_rounds": 0, "chart_steps": 0}


def compute_numbers(state):
    return {"numbers": steps.compute_numbers(state["case"])}


def choose_filings(state):
    chosen = steps.choose_filings(state["case"])
    return {"filings": chosen, "other_filings": steps.other_filings(state["case"], chosen)}


def with_url(state, f):
    # the filing's SEC link, which the report must give for every reason it cites
    path = steps.download(state["case"]["cik"], f["adsh"], os.path.join(state["folder"], "filings"))
    return {**f, "url": steps.filing_url(state["case"]["cik"], path)}


def get_passages(state):
    texts = {}
    for f in state["filings"]:
        texts[f["adsh"]] = {"label": f"{f['form']} filed {f['date']}",
                            "passages": steps.passages(filing_lines(state, f), f["form"])}
    return {"texts": texts, "filings": [with_url(state, f) for f in state["filings"]]}


# ---------- reading: LLM, with a loop it controls ----------
def read_filings(state):
    # one call for each 10-K / 10-Q, and one call for all the 8-Ks and NT forms together (they are short)
    case, labels, asks, short = state["case"], [], [], []
    for f in state["filings"]:
        t = state["texts"][f["adsh"]]
        if f["form"].startswith(("10-K", "10-Q")):
            labels.append(t["label"])
            asks.append(prompts.read_filing_prompt(case, t["label"], t["passages"]))
        else:
            short.append(f"===== {t['label']} =====\n{t['passages']}")
    if short:
        labels.append("8-K / NT")
        asks.append(prompts.read_filing_prompt(case, "the 8-Ks and late-filing notices", "\n\n".join(short)))
    answers = ask_many_for_json(asks, prompts.SYSTEM, name=f"{case['adsh']}_read")
    findings = []
    for label, answer in zip(labels, answers):
        for item in answer.get("findings", []):
            findings.append({"filing": label, **item})
    return {"findings": findings}


def decide_more(state):
    # the LLM decides: read more (search for words, add older filings), or stop
    rounds = state["read_rounds"] + 1
    prompt = prompts.decide_more_prompt(state["case"], state["findings"], state["filings"], state["other_filings"], rounds)
    return {"more": ask_llm_for_json(prompt, prompts.SYSTEM, name=f"{state['adsh']}_decide{rounds}"), "read_rounds": rounds}


def after_decide(state):
    more = state["more"]
    wants = more.get("searches") or more.get("older_filings")
    if not more.get("done") and wants and state["read_rounds"] <= MAX_READ_ROUNDS:
        return "read more"
    return "enough"


def search_more(state):
    # code: get the older filings the LLM asked for, and search every filing for its words
    more, others = state["more"], {f["adsh"]: f for f in state["other_filings"]}
    added = [with_url(state, {**others[a], "why": "asked for by the LLM"}) for a in more.get("older_filings", [])[:3] if a in others]
    parts = [f"===== {f['form']} filed {f['date']} (older filing) =====\n" + steps.passages(filing_lines(state, f), f["form"], 30000)
             for f in added]
    terms = more.get("searches", [])[:6]
    if terms:
        for f in state["filings"] + added:
            hits = steps.search(filing_lines(state, f), terms, limit=8000)
            if hits.strip():
                parts.append(f"===== {f['form']} filed {f['date']}: lines around {', '.join(terms)} =====\n{hits}")
    return {"filings": state["filings"] + added,
            "other_filings": [f for f in state["other_filings"] if f["adsh"] not in {a["adsh"] for a in added}],
            "new_text": "\n\n".join(parts)[:60000]}


def read_more(state):
    if not state["new_text"].strip():
        return {}
    what = f"new passages (round {state['read_rounds']})"
    prompt = prompts.read_more_prompt(state["case"], what, state["new_text"], state["findings"])
    answer = ask_llm_for_json(prompt, prompts.SYSTEM, name=f"{state['adsh']}_readmore{state['read_rounds']}")
    new = [{"filing": f"extra reading, round {state['read_rounds']}", **item} for item in answer.get("findings", [])]
    return {"findings": state["findings"] + new}


# ---------- judging: LLM ----------
def assess(state):
    prompt = prompts.assess_prompt(state["case"], state["numbers"], state["findings"])
    return {"assessment": ask_llm_for_json(prompt, prompts.SYSTEM, name=f"{state['adsh']}_assess")}


# ---------- charts: the LLM decides and looks, code draws ----------
def plan_chart(state):
    log, last, images, note = state.get("chart_log", []), state.get("chart_last"), [], ""
    if last and last["error"]:
        note = f"Your code for chart {last['chart']} failed:\n{last['error']}"
    elif last:
        images = [os.path.join(state["folder"], "charts", log[last["chart"] - 1]["file"])]
        note = (f"The image is chart {last['chart']} as you drew it. Look at it: does it make its point clearly, "
                "and is anything misleading (axes, units, scale, labels)?")
    step = state["chart_steps"] + 1
    prompt = prompts.plan_chart_prompt(state["case"], state["assessment"], log, note)
    plan = ask_llm_for_json(prompt, prompts.SYSTEM, name=f"{state['adsh']}_chart{step}", images=images)
    return {"chart_plan": plan, "chart_steps": step}


def after_plan(state):
    if state["chart_plan"].get("action") in ("new", "fix", "drop") and state["chart_steps"] < MAX_CHART_STEPS:
        return "draw"
    return "write"


def draw_chart(state):
    folder = os.path.join(state["folder"], "charts")
    steps.save_chart_data(state, folder)
    plan, log = state["chart_plan"], list(state.get("chart_log", []))
    n = int(plan.get("chart") or 0)
    if plan["action"] == "drop":
        if 1 <= n <= len(log):
            log[n - 1] = {**log[n - 1], "status": "dropped"}
        return {"chart_log": log, "chart_last": None, "charts": kept(log)}
    if not (plan["action"] == "fix" and 1 <= n <= len(log)):
        log.append({})
        n = len(log)
    name = f"chart_{n}"
    error = steps.draw_chart(plan.get("code", ""), name, folder)
    log[n - 1] = {"point": plan.get("point") or log[n - 1].get("point", ""),
                  "caption": plan.get("caption") or log[n - 1].get("caption", ""),
                  "code": plan.get("code", ""), "file": name + ".png", "status": "failed" if error else "ok", "error": error}
    return {"chart_log": log, "chart_last": {"chart": n, "error": error}, "charts": kept(log)}


def kept(log):
    return [(f"charts/{c['file']}", c["caption"]) for c in log if c["status"] == "ok"]


# ---------- the report: LLM writes, code checks ----------
def write_report(state):
    prompt = prompts.write_report_prompt(state["case"], state["numbers"], state["assessment"], state.get("charts", []),
                                         state["filings"], state.get("problems", []), state.get("report", ""))
    report = ask_llm(prompt, prompts.SYSTEM, name=f"{state['adsh']}_write{state['attempts'] + 1}").strip()
    if report.startswith("```"):
        report = report.strip("`").removeprefix("markdown").strip()
    open(os.path.join(state["folder"], "report.md"), "w").write(report)
    return {"report": report, "attempts": state["attempts"] + 1}


def check_report(state):
    folder = os.path.join(state["folder"], "filings")
    all_text = " ".join(open(os.path.join(folder, n)).read() for n in os.listdir(folder) if n.endswith(".txt"))
    known = json.dumps([state["numbers"], state["findings"]], default=str)
    urls = {f["url"] for f in state["filings"] if f.get("url")}
    return {"problems": steps.check_report(state["report"], all_text, known, state["case"]["filed"], urls)}


def after_check(state):
    # rewrite if the check found problems, otherwise stop
    if state["problems"] and state["attempts"] < MAX_WRITES:
        return "rewrite"
    return "done"


def build_graph():
    g = StateGraph(State)
    for name, fn in [("setup_case", setup_case), ("compute_numbers", compute_numbers), ("choose_filings", choose_filings),
                     ("get_passages", get_passages), ("read_filings", read_filings), ("decide_more", decide_more),
                     ("search_more", search_more), ("read_more", read_more), ("assess", assess),
                     ("plan_chart", plan_chart), ("draw_chart", draw_chart),
                     ("write_report", write_report), ("check_report", check_report)]:
        g.add_node(name, fn)
    g.set_entry_point("setup_case")
    g.add_edge("setup_case", "compute_numbers")
    g.add_edge("compute_numbers", "choose_filings")
    g.add_edge("choose_filings", "get_passages")
    g.add_edge("get_passages", "read_filings")
    g.add_edge("read_filings", "decide_more")
    # loop 1: the LLM keeps reading until more reading would not change its view
    g.add_conditional_edges("decide_more", after_decide, {"read more": "search_more", "enough": "assess"})
    g.add_edge("search_more", "read_more")
    g.add_edge("read_more", "decide_more")
    g.add_edge("assess", "plan_chart")
    # loop 2: the LLM makes a chart, looks at it, and fixes, drops or adds charts until it is done
    g.add_conditional_edges("plan_chart", after_plan, {"draw": "draw_chart", "write": "write_report"})
    g.add_edge("draw_chart", "plan_chart")
    g.add_edge("write_report", "check_report")
    # loop 3: rewrite until the check passes (at most MAX_WRITES writes)
    g.add_conditional_edges("check_report", after_check, {"rewrite": "write_report", "done": END})
    return g.compile()


def run_case(adsh):
    final = build_graph().invoke({"adsh": adsh}, {"recursion_limit": 100})
    # save every intermediate result (except the long texts) so each step can be checked
    keep = {k: v for k, v in final.items() if k not in ("texts", "report", "new_text")}
    json.dump(keep, open(os.path.join(final["folder"], "state.json"), "w"), indent=1, default=str)
    return final
