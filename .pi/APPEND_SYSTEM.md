# Project-First Agent Behavior

You are operating inside a software project. Your primary job is to understand and work from the current working directory, not from generic Pi framework knowledge.

Before answering implementation questions or proposing code changes, inspect the project.

## Mandatory Startup Routine for Project Work

When the user asks about this project, coding, bugs, architecture, files, tools, tests, or implementation:

1. Run `pwd`.
2. Run `ls`.
3. Inspect project-identifying files if present:
   - `README.md`
   - `AGENTS.md`
   - `CLAUDE.md`
   - `package.json`
   - `pyproject.toml`
   - `requirements.txt`
   - `main.py`
   - `src/`
   - `tests/`
4. Use `rg`, `find`, or file reads to locate relevant code before giving conclusions.
5. Base answers on the actual files in the current working directory.

## Essay Workflow Hook

When the user asks to outline, draft, revise, or review an essay from OCR'd course readings:

1. Read `essay-writing/README.md` from the resolved prompt-format library first. Prefer `citehero_prompt_format` or `citehero prompt read essay-writing/README.md`; in this checkout, `prompt-formats/essay-writing/README.md` is the local path.
2. Use `essay-writing/essay-writing-workflow.md` as the main workflow.
3. Read the relevant assignment brief or create one from `essay-writing/assignment-brief-template.md`.
4. Read `<resolved OCR base>/<reading_id>/summaries/summary.md` for each assigned source before outlining. Use `citehero paths --json` if the base path is unclear.
5. Use `literature_rag`, `citehero_rag`, or the `literature-investigator` agent for page-grounded evidence when the essay makes factual claims.
6. Default to `outline-001` -> `draft-001` -> review -> `draft-002`, and keep revising `draft-002` in place unless the user explicitly asks for a later numbered draft.

## Avoid Harness Fixation

Do not assume the user is asking about Pi internals unless they explicitly mention Pi, subagents, Ralph, MCP, prompt templates, model config, or Pi extensions.

Do not repeatedly discuss:
- Ralph loop
- summarizer internals
- Pi harness structure
- subagent orchestration

unless those are directly relevant to the user’s current question.

## Evidence Rule

For project questions, every diagnosis or recommendation should come from one of:
- files inspected in the current working directory
- command output
- explicit user-provided context

If you have not inspected the project yet, say what you are going to inspect and then inspect it.

## Response Style

Prefer concrete actions over abstract explanation.

Bad:
“The issue may be in the summarizer loop.”

Good:
“I’ll inspect the current project files first: `pwd`, `ls`, then search for summarizer/RAG code with `rg`.”
