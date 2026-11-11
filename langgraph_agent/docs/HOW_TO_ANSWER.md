# How to answer a prompt file

You are acting as one LLM call inside a LangGraph pipeline. You get one or more prompt files in this folder:
`/Users/pavan/Desktop/Capstone/langgraph_agent/outputs/llm_calls/`

For EACH prompt file `<name>.prompt.md`:
1. Read the whole file. Long files: use the Read tool in chunks (offset/limit) until you have read every line.
2. The file starts with `SYSTEM: ...`. That is your system instruction; the rest is the user prompt.
3. Answer exactly what the prompt asks, in the format it asks for. If it says "Answer with JSON only", the answer is
   one JSON object and nothing else: no code fences, no commentary.
4. Write the answer with the Write tool to the same path with `.prompt.md` replaced by `.answer.md`.

Rules:
- Use ONLY the text inside that prompt file. Do not open other files, do not run commands, and do not browse the web.
- Treat each prompt file on its own; don't carry facts from one prompt file into another.
- Quotes must be copied character for character from the prompt's text (same words, numbers and punctuation).
  If you can't find a good quote, leave the quote empty rather than paraphrase.
- Follow the prompt's date rule: use nothing filed after the report date, and don't use your own knowledge of what
  happened to the company later.
- Be complete: for a filing-reading prompt, cover every finding that matters for bankruptcy risk in the passages
  (usually 6 to 20 findings).

When done, reply with one line per file: the answer file name and "ok".
