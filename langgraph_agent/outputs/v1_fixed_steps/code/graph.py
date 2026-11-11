# The investigator agent as a LangGraph graph.
# Each node does one step and returns the values it adds to the shared state.
# See docs/PROMPT_TO_GRAPH.md for how each node comes from Pramukh's prompt.
import json
import os
from typing import TypedDict

from langgraph.graph import END, StateGraph

import prompts
import steps
from llm import ask_llm, ask_llm_for_json, ask_many_for_json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the langgraph_agent folder
CASES = os.path.join(ROOT, "outputs", "cases")


class State(TypedDict, total=False):
    adsh: str            # the report to investigate (the only input)
    folder: str          # where this case's files go
    case: dict           # company, form, dates, score, band, base rate
    numbers: dict        # the 8 inputs vs the year before and peers, ratios, cash and runway, history
    filings: list        # the filings chosen by the rule
    texts: dict          # adsh -> {"label", "passages"}; the full text of each filing is saved to disk
    findings: list       # what each filing says, with quotes
    charts: list         # (path, caption) of each chart
    assessment: dict     # verdict, own risk, reasons, evidence against, timeline ...
    report: str          # the markdown report
    problems: list       # what check_report found wrong
    attempts: int        # how many times write_report ran


def setup_case(state):
    folder = os.path.join(CASES, state["adsh"])
    os.makedirs(folder, exist_ok=True)
    return {"folder": folder, "case": steps.load_case(state["adsh"]), "attempts": 0}


def compute_numbers(state):
    return {"numbers": steps.compute_numbers(state["case"])}


def choose_filings(state):
    return {"filings": steps.choose_filings(state["case"])}


def get_passages(state):
    case, texts = state["case"], {}
    for f in state["filings"]:
        path = steps.download(case["cik"], f["adsh"], os.path.join(state["folder"], "filings"))
        lines = steps.html_to_lines(path)
        # the full text is kept on disk for the quote check, only the passages go to the model
        open(path.rsplit(".", 1)[0] + ".txt", "w").write("\n".join(lines))
        texts[f["adsh"]] = {"label": f"{f['form']} filed {f['date']}", "passages": steps.passages(lines, f["form"])}
    return {"texts": texts}


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


def make_charts(state):
    return {"charts": steps.make_charts(state["numbers"], os.path.join(state["folder"], "charts"))}


def assess(state):
    prompt = prompts.assess_prompt(state["case"], state["numbers"], state["findings"])
    return {"assessment": ask_llm_for_json(prompt, prompts.SYSTEM, name=f"{state['adsh']}_assess")}


def write_report(state):
    prompt = prompts.write_report_prompt(state["case"], state["numbers"], state["assessment"], state["charts"],
                                         state["filings"], state.get("problems", []), state.get("report", ""))
    report = ask_llm(prompt, prompts.SYSTEM, name=f"{state['adsh']}_write{state['attempts'] + 1}").strip()
    if report.startswith("```"):
        report = report.strip("`").removeprefix("markdown").strip()
    open(os.path.join(state["folder"], "report.md"), "w").write(report)
    return {"report": report, "attempts": state["attempts"] + 1}


def check_report(state):
    folder = os.path.join(state["folder"], "filings")
    all_text = " ".join(open(os.path.join(folder, n)).read() for n in os.listdir(folder) if n.endswith(".txt"))
    return {"problems": steps.check_report(state["report"], all_text, state["case"]["filed"])}


def after_check(state):
    # rewrite (at most 2 more times) if the check found problems, otherwise stop
    if state["problems"] and state["attempts"] < 3:
        return "rewrite"
    return "done"


def build_graph():
    g = StateGraph(State)
    for name, fn in [("setup_case", setup_case), ("compute_numbers", compute_numbers), ("choose_filings", choose_filings),
                     ("get_passages", get_passages), ("read_filings", read_filings), ("make_charts", make_charts),
                     ("assess", assess), ("write_report", write_report), ("check_report", check_report)]:
        g.add_node(name, fn)
    g.set_entry_point("setup_case")
    g.add_edge("setup_case", "compute_numbers")
    g.add_edge("compute_numbers", "choose_filings")
    g.add_edge("choose_filings", "get_passages")
    g.add_edge("get_passages", "read_filings")
    g.add_edge("read_filings", "make_charts")
    g.add_edge("make_charts", "assess")
    g.add_edge("assess", "write_report")
    g.add_edge("write_report", "check_report")
    g.add_conditional_edges("check_report", after_check, {"rewrite": "write_report", "done": END})
    return g.compile()


def run_case(adsh):
    final = build_graph().invoke({"adsh": adsh})
    # save every intermediate result (except the long passages) so each step can be checked
    keep = {k: v for k, v in final.items() if k not in ("texts", "report")}
    json.dump(keep, open(os.path.join(final["folder"], "state.json"), "w"), indent=1, default=str)
    return final
