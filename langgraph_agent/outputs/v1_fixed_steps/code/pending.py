# Files mode helper: which cases can move forward (every saved prompt has its answer), and which prompts still need one.
# Usage: python code/pending.py
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the langgraph_agent folder
CALLS = os.path.join(ROOT, "outputs", "llm_calls")
prompts = [f for f in os.listdir(CALLS) if f.endswith(".prompt.md")]
waiting = {}
for p in prompts:
    adsh = p.split("_")[0]
    waiting.setdefault(adsh, [])
    if not os.path.exists(os.path.join(CALLS, p.replace(".prompt.md", ".answer.md"))):
        waiting[adsh].append(p)
print("READY", " ".join(sorted(a for a, w in waiting.items() if not w)))
for a, w in sorted(waiting.items()):
    for p in w:
        print("NEEDS", p)
