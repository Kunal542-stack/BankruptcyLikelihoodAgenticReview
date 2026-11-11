# One small helper: send a prompt to Claude and get the text back.
#
# Two ways to reach Claude (set LLM_BACKEND):
#   "sdk"   (default)  the Claude Agent SDK with no tools, the same login the harness agent uses
#   "files"            the prompt is saved to outputs/llm_calls/<name>.prompt.md and the answer is read from
#                      outputs/llm_calls/<name>.answer.md. Claude in the app (the chat) writes the answers. If an answer
#                      is not there yet, the run stops with NeedAnswers; run it again once the answers are written.
#                      Steps whose answers already exist are not asked again.
import asyncio
import hashlib
import json
import os
import re

MODEL = "claude-opus-5-5"
BACKEND = os.environ.get("LLM_BACKEND", "sdk")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # the langgraph_agent folder
CALLS = os.path.join(ROOT, "outputs", "llm_calls")
JSON_ONLY = "\n\nAnswer with JSON only, no other text."


class NeedAnswers(Exception):
    pass


def ask_sdk(prompt, system):
    from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query

    async def run():
        options = ClaudeAgentOptions(system_prompt=system, model=MODEL, tools=[], allowed_tools=[],
                                     setting_sources=[], max_turns=1)
        parts = []
        async for message in query(prompt=prompt, options=options):
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        parts.append(block.text)
        return "".join(parts)

    return asyncio.run(run())


def file_names(prompt, system, name):
    key = hashlib.sha1((system + prompt).encode()).hexdigest()[:10]
    base = os.path.join(CALLS, f"{name}_{key}")
    return base + ".prompt.md", base + ".answer.md"


def ask_many(prompts, system, name):
    # asks several prompts; in "files" mode all missing prompts are saved first, then the run stops once
    if BACKEND == "sdk":
        return [ask_sdk(p, system) for p in prompts]
    os.makedirs(CALLS, exist_ok=True)
    answers, missing = [], 0
    for i, p in enumerate(prompts):
        prompt_file, answer_file = file_names(p, system, f"{name}_{i + 1}")
        if os.path.exists(answer_file):
            answers.append(open(answer_file).read())
        else:
            open(prompt_file, "w").write(f"SYSTEM: {system}\n\n{p}")
            missing += 1
    if missing:
        raise NeedAnswers(f"{missing} answers needed for {name} (see {CALLS})")
    return answers


def read_json(answer):
    match = re.search(r"\{.*\}", answer, re.S)
    if not match:
        raise ValueError("the answer has no JSON:\n" + answer[:500])
    return json.loads(match.group(0))


def ask_llm(prompt, system="You are a careful financial analyst.", name="call"):
    return ask_many([prompt], system, name)[0]


def ask_llm_for_json(prompt, system="You are a careful financial analyst.", name="call"):
    return read_json(ask_llm(prompt + JSON_ONLY, system, name))


def ask_many_for_json(prompts, system="You are a careful financial analyst.", name="call"):
    return [read_json(a) for a in ask_many([p + JSON_ONLY for p in prompts], system, name)]
