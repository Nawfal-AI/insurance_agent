# Engineering Notes

## What broke, and how I debugged it

This project hit more real, unplanned breakage than any other project in
this portfolio — worth documenting honestly rather than smoothing over,
since debugging a moving dependency surface is a real, transferable skill.

1. **`ImportError: cannot import name 'AgentExecutor' from 'langchain.agents'`.**
   The original code used LangChain's older agent-construction API
   (`create_tool_calling_agent` + `AgentExecutor`). LangChain's 1.0 release
   restructured the package — that API was removed from the core
   `langchain` package (a compatibility shim exists in a separate
   `langchain-classic` package, but the forward-looking fix was to rebuild
   the agent using LangGraph's `create_react_agent`, which is the current
   recommended way to construct a tool-calling agent). Fixed by rewriting
   `build_agent()` around `langgraph.prebuilt.create_react_agent` and
   restructuring the result-parsing logic to walk LangGraph's message list
   instead of `AgentExecutor`'s `intermediate_steps`.

2. **Gemini model deprecation, three times in a row.** `gemini-2.0-flash`
   was fully shut down. Its replacement, `gemini-2.5-flash`, then also
   started returning `404 NOT_FOUND` for new API keys — ahead of its own
   officially published October 2026 shutdown date, confirmed by other
   developers hitting the identical issue on Google's own developer forum
   at the same time. This wasn't a one-off; Google's Gemini model lineup
   changed faster than documented multiple times during this project's
   development. Fixed properly (not just patched) by switching to Google's
   `-latest` model alias (`gemini-flash-latest`), which Google documents as
   auto-updating to their current model — the model name is no longer
   hardcoded to a specific version that can be retired out from under the
   code. Also made the model name overridable via `GEMINI_MODEL` in `.env`
   as a second layer of resilience.

3. **`ResponseValidationError` on a working answer.** The agent actually
   produced a correct, well-grounded answer, but the API still returned a
   500 error. Cause: Gemini's response came back as a list of structured
   content blocks (`[{'type': 'text', 'text': '...', 'extras': {...}}]`)
   rather than a plain string, and the FastAPI response model expected a
   plain string. Fixed with a small `_extract_text()` normalizer that
   handles both a plain string and a list-of-blocks response shape, since
   different providers (and different versions of the same provider) don't
   agree on this format.

4. **Exposed API key, twice.** During setup, a real API key ended up pasted
   into chat while debugging a `.env` formatting issue. Both times, the fix
   was immediate key rotation, not just removing it from the file — a
   credential that's been shared anywhere, even accidentally, has to be
   treated as compromised regardless of whether the sharing channel seems
   private.

## A real inefficiency worth noting, not hiding

In the verified run (`results/example_run.json`), the agent called
`search_policy_documents` twice for the same underlying question, rewording
the query the second time rather than accepting the first result outright.
This isn't a bug — the agent is allowed to retry — but it's a genuine
retrieval-efficiency question worth having an opinion on in an interview:
is this the agent correctly being thorough, or the retrieval tool's
similarity search under-serving the first query? I haven't dug into this
further; it's flagged here rather than glossed over.

## What I'd do with more time

- Add proper agent-level integration tests (mocking the LLM call) rather
  than only testing tools in isolation without the LLM — right now,
  correctness of the full loop is only verified by the one manual run in
  `results/example_run.json`, not by an automated test suite.
- Investigate the duplicate-retrieval-call pattern above with a larger,
  more varied evaluation set of questions, the way the DPO and
  manipulation-pipeline projects both used a proper eval harness instead of
  a single example.
- Deploy to Cloud Run (see README) and capture that deployment as evidence
  too, not just local `curl` output.

## Honest limitations of this project as a portfolio piece

The agent loop and tool-calling behavior are real and verified — the
transcript in `results/example_run.json` is genuine model output, not
fabricated. The domain data (`documents.py`) is synthetic, invented for
this demo, not real insurance policy text. This demonstrates the ability to
build and debug an agentic AI system through a genuinely messy dependency
surface, not domain expertise in insurance or legal text specifically.
