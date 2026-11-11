# LLM as a judge: compares each graph report with the harness report for the same case.
# The harness report (Pramukh's run of the Claude Agent SDK agent) is the gold standard.
# Usage: python code/judge.py            (judges every case that has both reports)
# Writes outputs/judge/<adsh>.json for each case and outputs/JUDGE_SUMMARY.md with the table.
import json
import os

import pandas as pd

from llm import NeedAnswers, ask_llm_for_json

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the langgraph_agent folder
GOLD = os.path.join(ROOT, "inputs", "gold_cases")
GRAPH = os.path.join(ROOT, "outputs", "cases")
OUT = os.path.join(ROOT, "outputs", "judge")

RUBRIC = """You are judging two bankruptcy-risk reports about the same company filing.
GOLD is the reference report. CANDIDATE is a new report made by a different agent from the same data.
Judge how well CANDIDATE matches GOLD in its conclusions and content. Do not judge writing style.

Steps:
1. Read GOLD and list its key points: its verdict, its own risk level and %, whether it agrees with the model,
   each main reason, and each piece of evidence against (at most 10 points in total, most important first).
   Mark each point "critical" if missing it would give a reader the wrong picture of the case, else "supporting".
2. For each key point, say if CANDIDATE covers it: "covered", "partly" or "missing".
3. List facts or numbers in CANDIDATE that contradict GOLD (same thing, different value or meaning).
   Do not count small rounding differences.
4. List important points in CANDIDATE that GOLD does not have (they may still be right).
5. Score from 1 to 5:
   - verdict_agreement: 5 = same verdict and same risk level; 4 = same verdict, risk one step apart;
     3 = verdict one step apart (e.g. real risk vs unclear); 1 = opposite verdicts
   - coverage: how much of GOLD's key points CANDIDATE covers (5 = all critical points and most supporting points)
   - consistency: 5 = no contradictions; lower for each contradiction that matters
   - overall: how close CANDIDATE is to GOLD as an answer to "why this score, and is it a real risk?"

Return JSON:
{"gold_verdict": "...", "gold_own_risk": "...", "candidate_verdict": "...", "candidate_own_risk": "...",
 "key_points": [{"point": "...", "importance": "critical | supporting", "candidate": "covered | partly | missing"}],
 "contradictions": ["..."], "extra_points_in_candidate": ["..."],
 "scores": {"verdict_agreement": n, "coverage": n, "consistency": n, "overall": n},
 "summary": "two sentences"}"""


def judge_case(adsh):
    gold = open(os.path.join(GOLD, adsh, "report.md")).read()
    candidate = open(os.path.join(GRAPH, adsh, "report.md")).read()
    prompt = f"{RUBRIC}\n\n===== GOLD =====\n{gold}\n\n===== CANDIDATE =====\n{candidate}"
    result = ask_llm_for_json(prompt, "You are a strict, fair evaluator of financial analysis reports.", name=f"{adsh}_judge")
    points = result.get("key_points", [])
    critical = [p for p in points if p.get("importance") == "critical"]
    result["critical_recall"] = round(sum(p["candidate"] == "covered" for p in critical) / max(len(critical), 1), 2)
    result["all_recall"] = round(sum({"covered": 1, "partly": 0.5}.get(p["candidate"], 0) for p in points) / max(len(points), 1), 2)
    state = json.load(open(os.path.join(GRAPH, adsh, "state.json")))
    result["candidate_check_problems"] = len(state.get("problems", []))
    result["gold_words"], result["candidate_words"] = len(gold.split()), len(candidate.split())
    return result


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for adsh in sorted(os.listdir(GRAPH)):
        if not os.path.exists(os.path.join(GRAPH, adsh, "report.md")) or not os.path.isdir(os.path.join(GOLD, adsh)):
            continue
        path = os.path.join(OUT, adsh + ".json")
        if os.path.exists(path):
            r = json.load(open(path))
        else:
            try:
                r = judge_case(adsh)
            except NeedAnswers as e:
                print(adsh, "WAITING", e)
                continue
            json.dump(r, open(path, "w"), indent=1)
        name = json.load(open(os.path.join(GRAPH, adsh, "state.json")))["case"]["name"]
        rows.append({"case": name, "gold verdict": f"{r['gold_verdict']} ({r['gold_own_risk']})",
                     "graph verdict": f"{r['candidate_verdict']} ({r['candidate_own_risk']})",
                     **r["scores"], "critical recall": r["critical_recall"], "all recall": r["all_recall"],
                     "contradictions": len(r["contradictions"]), "quote problems": r["candidate_check_problems"]})
        print(rows[-1], flush=True)
    table = pd.DataFrame(rows)
    means = table.select_dtypes("number").mean().round(2)
    with open(os.path.join(ROOT, "outputs", "JUDGE_SUMMARY.md"), "w") as f:
        f.write("# Graph agent vs harness agent (gold)\n\n")
        f.write(table.to_markdown(index=False) + "\n\n**Averages:** " +
                ", ".join(f"{k} {v}" for k, v in means.items()) + "\n")
    print(means)
