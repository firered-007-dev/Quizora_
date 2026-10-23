# Architecture: Issue-to-First-PR Mentor

## Stack
| Layer | Technology | Version (tested) | Role |
|---|---|---|---|
| Language | Python | 3.12 (tested on 3.12.3) | All server logic |
| Web UI framework | Streamlit | 1.66.1 | Renders the page, holds per-session state, runs the Python on the server |
| Model client | google-genai | 2.33.0 | Calls Gemma 4 through the Gemini API |
| Model | Gemma 4 (open-weight), name set by GEMMA_MODEL | gemma-4-26b-a4b-it (to confirm) | Writes the plan |
| Issue source | GitHub REST API v3 | X-GitHub-Api-Version 2022-11-28 | Reads public issue title, body and state |
| HTTP client | requests | 2.34.2 | Calls the GitHub API with timeouts |
| Config loader | python-dotenv | 1.2.4 | Loads .env into environment variables for local runs |
| Dependency audit | pip-audit | latest at time of run | Checks pinned dependencies for known vulnerabilities |
| Hosting | To confirm (Streamlit Community Cloud planned) | n/a | Serves the live demo |

Only the four runtime packages above are pinned in requirements.txt. The full runtime set
(52 packages) is pinned as well, so installs are reproducible.

## Repository layout
```
quizora/
├── app.py                  # the whole application (single file for v1)
├── requirements.txt        # pinned runtime set
├── .env.example            # placeholder variable names only, safe to commit
├── .env                    # real secrets, local only, NEVER committed
├── .gitignore              # contains .env, .env.*, and a !.env.example exception
├── .streamlit/config.toml  # server, client, and theme settings
├── LICENSE                 # MIT
├── README.md               # project description, run steps, model and license
├── Procfile                # Railway process definition
├── railway.json            # Railway deployment configuration
├── Dockerfile              # Container deployment definition
├── vercel.json             # Vercel configuration
├── IMPLEMENTATION_PLAN.md  # Implementation roadmap and units
├── SECURITY-AUDIT.md       # 70-check security audit log and revision history
├── design/                 # Quizora design tokens and visual references
├── tests/                  # Pytest automated test suite (validation, app, ui)
├── context/                # The six context files
└── CLAUDE.md               # Entry point for coding agents
```

## System boundaries inside app.py
app.py is one file for v1. Its sections are separate responsibilities, and code must not
cross them:
1. Configuration: reads environment variables and sets constants. No network calls.
2. Input validation: ISSUE_URL_RE and the length limit. Pure functions, no network calls.
3. Rate and cost controls: check_cooldown (per session) and within_daily_cap (per process).
   These run before any network call.
4. GitHub client: fetch_issue only. The only place that talks to api.github.com. The only
   place that reads GITHUB_TOKEN.
5. Model client: get_client, build_prompt, build_plan. The only place that talks to Gemini
   and the only place that reads GEMINI_API_KEY.
6. User interface: the Streamlit page at the bottom of the file. It calls the sections
   above and shows results. It must not call requests or the Gemini client directly.

If app.py grows beyond about 300 lines, split it into validators.py, github_client.py,
model_client.py and ui.py along the same boundaries. Do not split before that.

## Trust boundaries
```
[Browser: untrusted]  --HTTPS-->  [Streamlit server: trusted, holds secrets]
                                        |                        |
                                        | HTTPS, fixed host      | HTTPS, fixed host
                                        v                        v
                          [api.github.com: public data,   [Gemini API: Gemma 4,
                           issue text is UNTRUSTED]        receives issue text]
```
- Anything from the browser is untrusted: the URL text, and any value in session state the
  browser could influence.
- Issue titles and bodies are written by strangers. They are untrusted even though they are
  public.
- Model output is untrusted text. It is displayed, never executed.
- Secrets exist only on the Streamlit server, in environment variables.

## Request flow (one plan)
1. Browser sends the URL text.
2. Server validates length and the regex. Failure returns an error. Stop.
3. Server checks cooldown for this session. Blocked returns a wait message. Stop.
4. Server checks the daily cap. Blocked returns a limit message. Stop.
5. Server calls GitHub for the issue (cached for 10 minutes). Failure returns a mapped
   message. Stop.
6. Server builds the prompt with the issue inside <issue> tags.
7. Server calls Gemini once with max_output_tokens of 1200. Failure returns a generic
   message. Stop.
8. Server returns the title, state and plan to the browser.

## Data storage model
- Persistent storage: none. v1 writes nothing to disk, a database, or a file. Logs go to
  the server's standard error only.
- Session state (server memory, per browser session): last_request timestamp only.
- Cache (server memory, shared across sessions, 10 minute TTL): fetched issue title, body
  and state for a given owner, repo and number. This data is public. The GitHub token is
  never stored in the cache, because it is not a function argument.
- Demo counter (server memory, shared across sessions, resets at midnight local date or
  restart): number of plan generations today. Protected by a lock.
- Prompts and model responses are not stored by the app. The Gemini API may log requests
  under Google's own terms. This must be stated in the README.

## Auth and access model
- v1 has no user accounts and no login. The app is public by design.
- Abuse is limited by controls, not identity: input validation, a 15 second cooldown per
  session, a daily process-wide cap, and a provider-side spending limit on the Gemini
  project (set in Google AI Studio or Google Cloud, not in code).
- The GitHub token is optional. If set, it is a fine-grained personal access token with no
  repository permissions. It grants read access to public data only.
- Nothing in v1 performs a privileged action, so there is no authorization layer to bypass.

## Outbound network allowlist (invariant, not a firewall)
The app connects to exactly two hosts:
- api.github.com, over HTTPS, with a 10 second timeout, redirects disabled.
- The Gemini API endpoint used by google-genai, over HTTPS.
Any other destination is a defect.

## AI task model
- One synchronous call to Gemma per plan request.
- Inputs are capped: title 300 characters, body 6000 characters.
- Output is capped at 1200 tokens.
- The model has no tools, no memory between requests, and no access to anything except the
  prompt it is sent.
- Prompt structure: fixed instructions first, then the untrusted issue inside <issue> tags.
  Tag strings inside the issue are removed before insertion.

## Invariants (hard rules; never violate without an approved change to this file)
1. The server connects only to api.github.com and the Gemini API. No URL, host, path or
   port is ever taken from user input or issue content.
2. GEMINI_API_KEY and GITHUB_TOKEN are read only from environment variables, only inside
   get_client and fetch_issue. They never appear in code, prompts, logs, UI, error messages,
   the browser, cache entries, or the repository.
3. Every user-supplied URL is matched against ISSUE_URL_RE and capped at 200 characters
   before any other processing.
4. Errors shown to users are UserFacingError messages or the fixed generic text. Exception
   messages, stack traces and status bodies are never shown to users. Showing a traceback
   is a defect.
5. Untrusted issue text is only placed inside <issue> tags in the prompt. It is never used
   as an instruction, a URL, a file path, a shell command, or a query.
6. Model output is displayed with st.markdown and HTML is not allowed (the default). The app
   never executes, evaluates, or interpolates model output into anything else.
7. Every outbound HTTP request has an explicit timeout. GitHub requests disable redirects.
8. Each plan request passes the cooldown and daily cap before any GitHub or Gemini call.
9. .env is never committed. .gitignore lists .env and .env.* and excludes only .env.example.
10. No code path writes user content to disk or a database.
11. Dependencies stay pinned in requirements.txt. Any change is re-audited with pip-audit
    before it is merged.
12. The app never sets a custom HTML component, custom CSS, or JavaScript.

## Known limitations (accepted for v1, recorded for judges)
- The daily cap and cooldown are in memory. They reset when the process restarts and do not
  apply across multiple server instances. The provider-side spending limit is the real
  backstop.
- Demo rate limits do not stop a determined attacker. They stop accidental floods and cost
  surprises.
- Model output can still be wrong or misleading, even with the prompt rules. The UI should
  say that the plan is a starting point and must be checked against the repository.
- Streamlit's own websocket and session handling are framework code. We rely on the pinned
  version and on re-auditing after upgrades.
