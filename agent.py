"""
The agent loop itself. This is a ReAct-style loop under the hood: given a
question, the LLM decides whether to call a tool, observes the tool's
result, and repeats until it has enough information to answer — as opposed
to a single prompt->response call. `verbose=True` / the returned
intermediate_steps let you actually see that loop happen, which matters if
you're asked to explain this in an interview rather than just point at code.

Provider-agnostic: swap ChatAnthropic for ChatOpenAI (or another LangChain
chat model) by changing get_llm() below — the agent/tool code doesn't change.
"""
import os

from dotenv import load_dotenv

load_dotenv()  # reads .env in the current directory automatically — no shell export needed

from langgraph.prebuilt import create_react_agent

from tools import ALL_TOOLS

SYSTEM_PROMPT = """You are an insurance coverage-check assistant. You help
users understand policy coverage, exclusions, claims process, and terms by
using the tools available to you — never answer from memory about specific
policy details, always ground your answer in a tool call to
search_policy_documents. If a question involves a calculation (e.g. claim
amount after deductible), use the calculate tool rather than doing math
yourself. If the user uses jargon, consider using lookup_term. Always cite
which policy section your answer is grounded in."""


def get_llm():
    provider = os.environ.get("LLM_PROVIDER", "anthropic").lower()
    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(model="claude-sonnet-4-5", temperature=0)
    elif provider == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o", temperature=0)
    elif provider == "google":
        # Google Gemini has a persistent free tier (rate-limited, not a
        # trial credit that expires) — no credit card required to start.
        # Get a key at https://aistudio.google.com/apikey
        #
        # IMPORTANT: Google has deprecated multiple Gemini models in 2026
        # (2.0 Flash and 2.0 Flash-Lite were both shut down). If you get a
        # RESOURCE_EXHAUSTED / "limit: 0" error, it usually means the model
        # below has since been deprecated too, not that you're out of quota.
        # Check the CURRENT free-tier model list before assuming a code bug:
        # https://ai.google.dev/gemini-api/docs/pricing
        # Override without touching code: set GEMINI_MODEL in .env
        from langchain_google_genai import ChatGoogleGenerativeAI
        model_name = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")
        return ChatGoogleGenerativeAI(model=model_name, temperature=0)
    elif provider == "ollama":
        # Fully local, fully free, no API key or internet needed at
        # inference time — but needs a reasonably capable machine and
        # tool-calling support varies by model. Install: https://ollama.com
        # then: ollama pull llama3.1
        from langchain_ollama import ChatOllama
        return ChatOllama(model="llama3.1", temperature=0)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


def build_agent():
    llm = get_llm()
    # NOTE: `prompt=` is the current LangGraph parameter name for the system
    # prompt as of this writing. This has been renamed across LangGraph
    # versions before (state_modifier -> messages_modifier -> prompt). If
    # you hit a TypeError about an unexpected keyword here, that's what
    # changed — tell me the exact error and I'll fix the parameter name.
    return create_react_agent(llm, ALL_TOOLS, prompt=SYSTEM_PROMPT)


def ask(question: str) -> dict:
    """Run the agent on a question. Returns the final answer plus the
    tool-call trace, so callers (and the /ask endpoint) can show the
    planning loop, not just the final text."""
    agent = build_agent()
    result = agent.invoke({"messages": [("user", question)]})
    messages = result["messages"]

    # Tool outputs come back as separate ToolMessage entries in the
    # conversation, keyed by tool_call_id, so we join them back to the
    # AIMessage tool call that requested them.
    tool_outputs = {
        msg.tool_call_id: msg.content
        for msg in messages
        if msg.__class__.__name__ == "ToolMessage"
    }

    trace = []
    final_answer = ""
    for msg in messages:
        if msg.__class__.__name__ == "AIMessage":
            tool_calls = getattr(msg, "tool_calls", None)
            if tool_calls:
                for tc in tool_calls:
                    trace.append(
                        {
                            "tool": tc["name"],
                            "tool_input": tc["args"],
                            "observation": tool_outputs.get(tc["id"], ""),
                        }
                    )
            elif msg.content:
                final_answer = msg.content

    return {"answer": final_answer, "tool_calls": trace}
