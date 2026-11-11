# Run the graph agent on one or more reports:  python code/run.py <adsh> [<adsh> ...]
# Each case is saved in outputs/cases/<adsh>/: report.md, charts/, filings/ and state.json (every step's result).
import sys
import time

from graph import run_case
from llm import NeedAnswers

for adsh in sys.argv[1:]:
    start = time.time()
    try:
        final = run_case(adsh)
        status = "ok" if not final["problems"] else f"{len(final['problems'])} problems left"
        print(f"{adsh}: {final['case']['name']}  {len(final['filings'])} filings, {len(final['findings'])} findings, "
              f"verdict {final['assessment'].get('verdict')}, {status}, {time.time() - start:.0f}s", flush=True)
    except NeedAnswers as e:
        # "files" mode: the prompts are saved, run again after the answers are written
        print(f"{adsh}: WAITING {e}", flush=True)
    except Exception as e:
        print(f"{adsh}: FAILED {type(e).__name__}: {e}", flush=True)
