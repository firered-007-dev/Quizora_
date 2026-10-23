# Code Standards: Issue-to-First-PR Mentor

These rules are concrete on purpose. Two sessions given the same kind of task must produce
the same pattern. If a rule blocks a real need, change this file first, then the code.

## General principles
- Simple beats clever. The app is small and must be explainable to judges in one minute.
- One responsibility per function. A function that calls GitHub must not also build prompts.
- No dead code, no commented-out code, no unused imports, no speculative helpers.
- Prefer the standard library and the pinned packages already listed. Do not add a new
  package without following the dependency rule below.
- Every function that touches the network or a secret has a one-line docstring saying what
  it sends and where.

## Python conventions
- Target Python 3.12. Use f-strings. Use walrus only where it removes a repeated call.
- Follow PEP 8. Maximum line length 110. Format with black if available.
- Module-level constants are UPPER_SNAKE_CASE and live at the top of the file, after imports.
- Functions and variables are snake_case. Classes are PascalCase.
- Imports are grouped: standard library, third party, local. One import per line.
- Type hints are optional for v1. If added, add them to the public functions only.

## Error handling
- Expected failures raise UserFacingError with a message safe to show a beginner.
- Unexpected failures are logged with log.exception and show the fixed generic message
  "Something went wrong. Please try again in a few minutes." in the UI.
- Never use a bare `except:` and never use `except Exception: pass`.
- Never render str(e) or any exception text in the UI. This is an invariant.
- Never convert an error into a success. If a step fails, stop and show the error.

## Logging
- Use the logging module with the logger named "issue-mentor". Do not use print().
- Allowed in logs: status codes, the words "GitHub request failed", owner and repo names,
  issue numbers, and exception types.
- Forbidden in logs: the API keys, the GITHUB_TOKEN, request headers, the full prompt,
  the full issue body, the model's full response, and any Authorization value.
- Log level INFO by default. Use WARNING for expected user errors only if useful. Use
  ERROR for unexpected failures.

## Secrets and configuration
- Read secrets only with os.getenv inside the function that needs them, at call time.
- Never hardcode a key, token, or example value that looks real. Placeholders are obviously
  fake, for example your_gemini_key_here.
- .env.example lists variable names and placeholders only. Never put a real value in it.
- Non-secret settings (MODEL, caps, timeouts) live as constants or as optional environment
  overrides with safe defaults.

## Network calls
- Build URLs from validated parts only. Never concatenate raw user text into a URL.
- Always pass timeout= to requests calls. The GitHub timeout is 10 seconds.
- Always pass allow_redirects=False on GitHub calls and treat any non-200 status as a
  failure.
- Check the status code before calling .json(). A 404 maps to "not found". Any other
  non-200 maps to the generic GitHub message.
- Reject pull request responses explicitly (the issues endpoint also returns PRs).

## Input validation
- Validate with an allowlist regex. Do not use blocklists.
- Cap lengths before any processing. The input box uses max_chars=200.
- Strip whitespace once, at the start of the button handler, and use that value everywhere.
- Owner and repo names allow letters, digits, dot, underscore and hyphen only.
- Issue numbers are digits only, at most 10 digits, converted with int() after the regex.

## Prompts
- Prompt templates are defined only in build_prompt. No other code builds prompts.
- Instructions come first. Untrusted text comes last, inside <issue> tags.
- Before inserting untrusted text, remove the strings "<issue>", "</issue>", "<title>",
  "</title>", "<body>" and "</body>" from it.
- The plan format is fixed by the prompt. If you change a section name, change it in the
  prompt and in the README in the same commit.

## Streamlit conventions
- st.set_page_config is the first Streamlit call in the file.
- Use @st.cache_data only for public data and only with an explicit ttl.
- Use @st.cache_resource for clients and shared objects that hold no user data.
- Use st.stop() to end a branch. Never use sys.exit().
- Never pass unsafe_allow_html=True. Never write custom HTML, CSS or JavaScript.
- Show model text with st.markdown. Show titles with st.subheader or st.caption.
- Use st.warning for user mistakes, st.error for failures, st.spinner for waiting.

## Naming and file organisation
- Files: lowercase with hyphens for docs, lowercase with underscores for Python.
- Context files: the six names in context/ are fixed. Do not rename them.
- Test files go in tests/ and are named test_<module>.py.

## Tests (minimum for v1)
- tests/test_validation.py must cover: a valid issue URL, a URL with a trailing slash, a
  pull request URL pattern, a non-GitHub host, a path traversal attempt in the owner
  segment, an overlong input, and a URL with extra path segments.
- The tests must not call GitHub or Gemini. Mock or avoid network calls.
- Run with: python -m pytest tests/ -q. All tests must pass before a commit to main.

## Git and commits
- Branch names: feat/<short-name>, fix/<short-name>, sec/<short-name>, docs/<short-name>.
- Commit messages use a prefix: feat:, fix:, sec:, docs:, test:, chore:. One sentence.
- Commit and push at least every 30 minutes during the hackathon.
- Never commit .env, a real key, or a generated plan that contains issue text from a
  private source.

## Dependencies
- To add a dependency: state why in progress-tracker.md, pin the exact version, add it to
  requirements.txt by regenerating the runtime pin list in a clean venv, run pip-audit, and
  record the result in SECURITY-AUDIT.md.
- Remove any dependency that is no longer imported.
