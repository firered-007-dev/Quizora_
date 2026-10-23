# Implementation Plan: Quizora (Issue-to-First-PR Mentor)

Status: written before any build work, 2026-10-23. Source of truth for scope: context/project-overview.md.
Source of truth for rules: CLAUDE.md, context/architecture.md (12 invariants), context/code-standards.md,
context/ai-workflow-rules.md. Where this plan and those files disagree, the files win and this plan is corrected.

## 1. What is being built

Quizora is the Issue-to-First-PR Mentor. A beginner pastes a public GitHub issue link. The app fetches the issue
through the GitHub REST API, sends the issue text to Gemma 4 through the Gemini API, and shows a five-section
plan. It is a single-file Streamlit app (app.py, ADR-001), with the FlexiQuiz-based design tokens in design/.

Decisions made for this build (recorded in context/progress-tracker.md):
- D1. The product name is Quizora. The page title and the README use "Quizora". The five plan section headings
  do not change (they are a public contract).
- D2. The design files were renamed to quizora-* and the tokens are unchanged.
- D3. The LICENSE copyright holder is "Quizora contributors" as a placeholder. Replace with the real name before
  submission.
- D4. Model name stays gemma-4-26b-a4b-it, overridable with GEMMA_MODEL. Still unverified (Open Question Q1).

## 2. Current state (what already exists)

Present in the folder: app.py (hardened in Phase 1), requirements.txt (52 pinned packages, pip-audit clean on
2026-10-23), context/ (six files), CLAUDE.md, SECURITY-AUDIT.md, design/ (three token files).

Missing: .streamlit/config.toml, .env.example, .gitignore, LICENSE, README.md, tests/, and the progress-tracker
entries for this build.

## 3. Gaps found in app.py during review (these become work units)

| # | Gap | Why it matters | Rule it breaks |
|---|---|---|---|
| G-A | build_prompt only strips `</title>`, `</body>`, `<issue>`, `</issue>`. It does not strip `<title>` or `<body>`. | Issue text can open fake tags inside the data block. | code-standards.md "Prompts": strip all six strings. |
| G-B | Title and model output are shown with markdown. An image such as `![x](https://third-party/...)` loads from a third-party host. | ui-context.md forbids third-party images. The model can emit these even when told not to. | Invariant 12 and ui-context "never do": no third-party images. |
| G-C | An empty model reply shows its own sentence, "The model returned no text...", which is not in the fixed copy list. | Copy rule: fixed messages only, changes recorded. | ui-context.md "Copy". |
| G-D | The page does not say the plan must be checked against the repository. | architecture.md "Known limitations" says the UI should say this. | Known-limitations commitment. |
| G-E | The title is still "Issue-to-First-PR Mentor" in app.py and the copy. | Decision D1. | D1 |
| G-F | Mock tests for fetch_issue and build_plan do not exist yet. | code-standards.md "Tests". | Tests minimum |

## 4. Work units (in order; one unit at a time, verify before the next)

Each unit ends with: py_compile, pytest, a progress-tracker entry, and a commit-ready state.

U1. Repository files. Create .gitignore (ignores .env and .env.*, allows .env.example), .env.example (placeholders
    only: GEMINI_API_KEY=your_gemini_key_here, GITHUB_TOKEN=your_github_token_here, GEMMA_MODEL, DAILY_PLAN_CAP),
    and .streamlit/config.toml.
    Acceptance: .env is ignored by git; the config sets enableCORS=true (the SECURITY-AUDIT revision 2 correction),
    enableXsrfProtection=true, client.showErrorDetails=false, browser.gatherUsageStats=false, and the theme
    colors from design/quizora-design-tokens.json "streamlit" section.
    Open: the Poppins font setting. Streamlit's font option is not verified offline here. Left out; recorded as Q7.

U2. Prompt safety (G-A). Strip the six tag strings case-insensitively from title and body before insertion.
    Acceptance tests: a title "<title>x" and a body "<body>" and "</ISSUE>" are all removed; the output contains
    exactly one <issue>, <title>, <body> block.
    Security re-check: build_prompt is on the SECURITY-AUDIT list. Re-run its checks and record the result.

U3. Output safety (G-B). Add a pure function `strip_images(text)` that replaces markdown image syntax
    `![alt](url)` with the alt text and removes raw `<img` tags, applied to the plan before display. Apply
    st.markdown to the plan only. Show the title with st.subheader after escaping markdown control characters
    in the title (it is untrusted). Tests: image syntax is removed; a title with `![a](http://x)` shows no image.

U4. Copy and branding (G-C, G-D, G-E). Page title, st.title and the description become Quizora. Empty model reply
    raises an internal error that shows the generic message "Something went wrong. Please try again in a few
    minutes." Add a caption under the plan: "This plan is a starting point. Check it against the repository."
    Record each copy change in progress-tracker.md with the reason (ui-context.md rule).

U5. Validation tests (code-standards.md minimum). tests/test_validation.py covers: valid URL, trailing slash,
    pull-request URL pattern (it matches the regex; the PR check is in fetch_issue, so the test asserts the regex
    accepts it and fetch_issue rejects it in U6), non-GitHub host, path traversal in owner
    (`https://github.com/../x/issues/1`), overlong input (over 200 characters), extra path segments.
    No network calls.

U6. Client tests with mocks (tests/test_app.py). Mock requests.get and the Gemini client; no network.
    Cover: 200 with issue returns title/body/state; 404 maps to the "not found" message; a PR payload maps to the
    PR message; 500 maps to the generic GitHub message; a RequestException maps to "Could not reach GitHub";
    the Authorization header appears only when GITHUB_TOKEN is set; redirects are disabled; a timeout is passed.
    Cooldown returns a wait time within 15 seconds and 0 after it; the daily cap blocks at the limit.
    Use st.session_state only through the function calls in tests that need it, or skip with a clear reason.

U7. Streamlit smoke test. Use streamlit.testing.v1.AppTest to run app.py: the empty button shows the warning;
    a bad link shows the format error without calling GitHub (requests.get is patched and asserted not called);
    the title "Quizora" appears.

U8. Documentation. README.md (what it is, run steps, model name with the note that the model card is unverified,
    Gemini logging note from SECURITY-AUDIT, "check the plan against the repository"). LICENSE (MIT, placeholder
    holder per D3). Update context/architecture.md file layout to match the real files. Update
    SECURITY-AUDIT.md for every check whose state changed (U2, U3, U6 evidence).

U9. Verification (ai-workflow-rules.md section 6). Run and record: py_compile; pytest -q; streamlit starts
    headless without errors; secret scan (grep for AIza, ghp_, github_pat_, sk-; no .env tracked); pip-audit on
    requirements.txt (record the result). Check that no third-party host is referenced in app.py except
    api.github.com and the Gemini client.

Not in this build (needs the user, recorded as open items):
- Live Gemini call and the 3 to 5 real good-first-issue timing runs (G1). Needs a real key and a human run.
  The manual-test cap is 20 plan requests per session. Count recorded in progress-tracker Session Notes.
- Creating the public GitHub repo, the first commit and push, deployment, and the provider spending limit
  (SECURITY-AUDIT FAIL 28 and FAIL 64). These need the user's accounts and cannot be done in code.
- Confirming the Gemma model name and license on the model card (Q1, Q2).

## 5. Open questions carried into this build
- Q1: Exact Gemma model identifier. Unverified. Keep the default and the GEMMA_MODEL override.
- Q2: Gemma 4 license. Unverified. The README must link the model card before submission.
- Q3: Hosting. Undecided.
- Q7: Poppins font loading through Streamlit config. Not verified offline. Use only if confirmed.

## 6. Done means
- All units U1 to U9 complete, with the tests in tests/ passing.
- progress-tracker.md has an entry for each unit, and its Next Up list is accurate.
- The live steps above are listed as the next actions for the user.
