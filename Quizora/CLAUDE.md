# CLAUDE.md: Entry point for coding agents

This is the Issue-to-First-PR Mentor, a small Streamlit app that turns a public GitHub issue
into a beginner's contribution plan using Gemma 4 through the Gemini API.

## Read these first, in this order, before any action
1. context/progress-tracker.md: current phase, goal, next steps, open questions.
2. context/project-overview.md: what is in and out of scope.
3. context/architecture.md: stack, boundaries, trust model, and the twelve invariants.
4. context/code-standards.md: naming, error handling, logging, network and prompt rules.
5. context/ai-workflow-rules.md: how to work here, security rules, verification checklist.
6. context/ui-context.md: theme tokens, page structure, fixed copy.

## Hard rules (summary; the full rules are in the context files)
- Never write, print, log, or commit a real API key or token. Secrets live only in .env,
  which is git-ignored.
- Work one unit at a time. Do not build anything in the out-of-scope list.
- The server talks only to api.github.com and the Gemini API. Never take a host or path from
  user input or issue text.
- Treat GitHub issue text and model output as untrusted data. Never execute, evaluate, or
  render them as HTML.
- Show users only the fixed messages in ui-context.md. Never show exception text or tracebacks.
- Before changing fetch_issue, build_prompt, build_plan, ISSUE_URL_RE, check_cooldown,
  within_daily_cap, the error handling, or .streamlit/config.toml, re-check the affected
  items in SECURITY-AUDIT.md.
- Do not add dependencies without pinning them, running pip-audit, and recording the result.

## After every meaningful change
1. Update context/progress-tracker.md (what changed, why, and what is next).
2. Update any context file whose facts changed (architecture, standards, scope, UI).
3. Update SECURITY-AUDIT.md if a security-relevant check changed state.
4. Run the verification checklist in context/ai-workflow-rules.md section 6.

## Commands
- Install (exact pins): pip install -r requirements.txt
- Run locally: streamlit run app.py
- Syntax check: python -m py_compile app.py
- Tests (once tests/ exists): python -m pytest tests/ -q
- Dependency audit: pip-audit -r requirements.txt
- Secret check before a push: git diff --cached | grep -E "AIza|ghp_|github_pat_|sk-"
  (expect no output)

## When unsure
Record the question in context/progress-tracker.md under Open Questions, choose the more
conservative option, state the choice in one line, and continue. Do not guess the Gemma model
name or its license.
