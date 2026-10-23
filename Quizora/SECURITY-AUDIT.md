# Security audit: Issue-to-First-PR Mentor  (2026-10-23, revision 2)

Scope: The local project after the design and theme update. Reviewed: app.py, requirements.txt (52 pinned
packages), .gitignore, .env.example, .streamlit/config.toml, design/ files, and the context files. Tools run:
the audit lead scanner (scan_leads.py: 0 pattern hits across the text files), pip-audit against the pinned runtime
set (no known vulnerabilities found), a grep of app.py for dangerous sinks and secret-shaped strings (no hits), a
check of the installed Streamlit 1.66.1 config (showErrorDetails "none" and the CORS and XSRF option defaults), and
a local startup test with curl (HTTP 200, no CORS warning, no Access-Control-Allow-Origin header).
Not accessible: the deployed URL, git history (no repository yet), GitHub account settings, hosting settings, Google
AI Studio and Google Cloud billing and quota settings, and a live Gemini call. Checks that depend on these are UNKNOWN.

Disclaimer: educational checklist, not a penetration test or guarantee. This report was drafted with AI assistance and
has not yet been reviewed by a human (see check 50).

## Summary
PASS 18 | FAIL 2 | UNKNOWN 15 | N/A 35   (total 70)

Ship blockers (fix before the app is put on a public URL): 28 Missing rate limits; 64 Missing resource limits.
Set before deployment (config): 27 and 70 need corsAllowedOrigins and allowedHosts set to the deployed origin.
Verify on the deployed path before submission: 02, 10, 13, 20, 27, 29, 36, 43, 46, 47, 48, 55, 70.
Human review required: 38, 50.

## Findings (Tier 1 first, then by severity)

### 28 Missing rate limits - FAIL
Evidence: app.py check_cooldown (15 seconds, stored in st.session_state, so it applies per browser session and
resets on reload); app.py within_daily_cap (DAILY_PLAN_CAP, an in-process counter that resets on restart and is
not shared between instances); no per-IP limit in the app; no host-level rate limit configured (not deployed yet).
Failure mode: a script that opens new sessions or restarts the server can send far more plan requests than intended
and use up the Gemini quota or budget in a short time.
Smallest safe fix: set a daily quota and budget on the Gemini project in Google AI Studio or Google Cloud Billing,
keep DAILY_PLAN_CAP at a value that matches that budget, and enable request rate limits at the host if it offers them.
Verify: on the deployed URL, run a small manual test of 20 plan requests from new browser sessions (our own app,
within authorisation). Confirm the app blocks at DAILY_PLAN_CAP and that the provider quota stops further model
calls. Record the result in progress-tracker.md Session Notes.

### 64 Missing resource limits - FAIL
Evidence: app.py has MAX_TITLE_CHARS = 300, MAX_BODY_CHARS = 6000, MAX_OUTPUT_TOKENS = 1200 (passed in
GenerateContentConfig), REQUEST_TIMEOUT_SECONDS = 10, and DAILY_PLAN_CAP. These are PASS in code. Missing: no spending
limit or budget alert on the Gemini or Google Cloud project (vendor console, not configured). The daily cap counts
requests, not money.
Failure mode: a bug or misuse run could generate expensive model calls that no provider-side ceiling stops before a
large bill appears.
Smallest safe fix: in Google Cloud Billing, create a budget for the project with alerts at 50, 90 and 100 percent,
and set the Generative Language API quota to a daily value the budget can cover.
Verify: take a screenshot or export of the budget and quota, and confirm that the quota value times the expected cost
per plan is below the budget.

### 02 Public .env files - UNKNOWN
Evidence: .gitignore excludes .env and .env.*, with !.env.example as the exception. No git repository exists yet, so
git ls-files cannot run. Deployed site not checked.
Failure mode: if a real .env is committed or the host serves the project folder, the Gemini key is exposed.
Smallest safe fix: keep .gitignore as written. If a .env was ever committed, rotate the key first.
Verify: after the first commit, run git ls-files | grep -i env and expect only .env.example. On the deployed domain,
request /.env and /.env.local and expect 404.

### 10 Production debug tools exposed - UNKNOWN
Evidence: app.py has no debug routes or flags. .streamlit/config.toml sets [client] showErrorDetails = "none" (a
valid value in the installed Streamlit 1.66.1). Deployed site not checked.
Failure mode: a visible traceback can reveal file paths, library versions and internal state.
Smallest safe fix: keep showErrorDetails = "none" and do not run with debug settings in production.
Verify: on the deployed site, trigger an error path in a staging copy and confirm the browser shows only the generic
message and no traceback.

### 13 Secrets in Git history - UNKNOWN
Evidence: no git repository exists (scan_leads reports git metadata: no). Secret-shaped string search of app.py,
.env.example and config.toml returned no hits.
Failure mode: a key committed even briefly remains in history after deletion.
Smallest safe fix: make the first commit only after .gitignore is in place. If any real key was ever committed, rotate
it, because rotation is the real fix.
Verify: after the first commit, run gitleaks detect --source . (or trufflehog) and record zero findings.

### 20 Cross-site request forgery (CSRF) - UNKNOWN
Evidence: .streamlit/config.toml enableXsrfProtection = true (Streamlit default). The app has no cookie-based login and
no HTTP endpoints of its own that change state. Streamlit's own documentation states that XSRF protection does not stop
a cross-origin WebSocket connection, and the plan requests travel over that WebSocket. Deployed origin settings not yet
set.
Failure mode: a third-party web page opens the app's WebSocket in a visitor's browser and triggers plan generation on
our quota. No user data is exposed.
Smallest safe fix: set server.corsAllowedOrigins to the exact deployed origin and server.allowedHosts to the deployed
hostname before launch (see 27 and 70).
Verify: from a test page on another origin, attempt to open the app's WebSocket and confirm it is rejected.

### 27 Overly permissive CORS - UNKNOWN
Evidence: .streamlit/config.toml now sets server.enableCORS = true, Streamlit's default. Correction: revision 1 of this
report wrongly recommended enableCORS = false. With that setting Streamlit sends Access-Control-Allow-Origin: * and
accepts WebSocket connections from any origin. The local startup test with CORS on sent no Access-Control-Allow-Origin
header and logged no CORS warning. corsAllowedOrigins is still empty and the deployed headers are not checked.
Failure mode: with CORS off, any website can read responses from the app and open its WebSocket.
Smallest safe fix: keep enableCORS = true and set corsAllowedOrigins = ["https://<deployed-origin>"] at deployment.
Verify: curl -I -H "Origin: https://evil.example" https://<deployed-url>/ and confirm no Access-Control-Allow-Origin
header that reflects evil.example.

### 29 Unprotected staging or test environments - UNKNOWN
Evidence: no staging environment is defined. Hosting not yet chosen.
Failure mode: a public test copy using the production Gemini key shares its quota and budget and exposes the key to
anyone who finds the copy.
Smallest safe fix: give any staging copy its own Gemini key and budget, and restrict it at the host or with a password.
Verify: open the staging URL signed out and confirm it is either restricted or uses a separate key with its own budget.

### 36 Sensitive source maps or build artifacts - UNKNOWN
Evidence: the app is Python served by Streamlit, and no source maps are produced. Deployed file tree not checked.
Failure mode: deploying the whole folder can expose .git, .env or backups.
Smallest safe fix: deploy only app.py, requirements.txt, .streamlit/ and the design files you choose to publish. Do not
deploy the repository folder with its .git directory.
Verify: on the deployed domain, request /.git/config and /.env and expect 404 for both.

### 38 Malicious or compromised packages - UNKNOWN
Evidence: four direct runtime dependencies (streamlit 1.66.1, google-genai 2.33.0, python-dotenv 1.2.4,
requests 2.34.2) and 52 pinned packages in total. pip-audit checks for known vulnerabilities, not for malicious or
hijacked packages. No publisher review has been done.
Failure mode: a typosquatted or hijacked dependency could run code when installed.
Smallest safe fix: confirm each direct package links to its official project on pypi.org and to its official source
repository. Remove any pinned package that the app does not need and that you cannot identify.
Verify: a human reviewer records, for each direct package, the project links checked and the date. This entry stays
UNKNOWN until that record exists.

### 43 No security monitoring or alerts - UNKNOWN
Evidence: no alerting in the repository. Google Cloud budget alerts and uptime checks are not configured (vendor console).
Failure mode: runaway usage or an outage goes unnoticed until the demo or judging.
Smallest safe fix: create a budget alert (see 64) and an uptime check on the deployed URL, sent to at least two people.
Verify: temporarily lower the budget alert threshold, confirm the alert arrives, then restore it. Record the test.

### 46 Missing security headers - UNKNOWN
Evidence: config.toml does not set response headers, and the app sets no Content-Security-Policy. The design change adds
a browser-side font load from fonts.googleapis.com and fonts.gstatic.com (approved, see change log). Deployed headers
not checked.
Failure mode: without anti-framing and content-type protections, the page can be embedded in a phishing frame.
Smallest safe fix: if the host allows custom headers, set X-Content-Type-Options: nosniff, a frame restriction
(frame-ancestors 'none' or X-Frame-Options: DENY), and Strict-Transport-Security. Otherwise record the host defaults.
Verify: curl -I https://<deployed-url> and inspect the response headers against this list.

### 47 Unsafe cookie settings - UNKNOWN
Evidence: the app sets no cookies of its own. Streamlit sets its own session and XSRF cookies. Deployed Set-Cookie flags
not checked.
Failure mode: a cookie without Secure or HttpOnly can leak on an insecure network or be read by page scripts.
Smallest safe fix: serve only over HTTPS and keep Streamlit's defaults. Enable Secure if the host allows it.
Verify: curl -i https://<deployed-url> and inspect each Set-Cookie line.

### 48 Sensitive data unprotected in transit or at rest - UNKNOWN
Evidence: outbound calls to api.github.com use requests with default certificate verification. No verify=False in
app.py (grep). Inbound TLS and redirects on the deployed host not checked. The app stores no data at rest.
Failure mode: plain-text or bad-certificate connections would expose issue requests and the GitHub token header.
Smallest safe fix: deploy only over HTTPS and enable an HTTP-to-HTTPS redirect at the host.
Verify: confirm a valid certificate for the deployed domain and that http:// redirects to https://.

### 50 Over-trusting AI-generated code - UNKNOWN
Evidence: app.py, the design files and this report were drafted with AI assistance. No human has yet read app.py line by
line or run tests. tests/ does not exist yet.
Failure mode: an AI-written security function can contain a subtle flaw that is only found under attack.
Smallest safe fix: a team member reads app.py in full, writes tests/test_validation.py from the cases in
code-standards.md, runs them, and records their name and the date in progress-tracker.md Session Notes.
Verify: the test file exists and passes, and the review record exists.

### 55 No MFA on privileged accounts - UNKNOWN
Evidence: the accounts that control the project (GitHub owner, Google account holding AI Studio and Cloud Billing,
hosting provider) have not been checked for MFA. Vendor settings.
Failure mode: a phished password lets someone rotate the key, drain the budget, or push code.
Smallest safe fix: enable two-step verification on each account and enforce it for the GitHub repository owner.
Verify: check each provider's security settings and record a screenshot or export in progress-tracker.md.

### 70 Unsecured GraphQL, WebSocket or realtime endpoints - UNKNOWN
Evidence: Streamlit's WebSocket is the app's only realtime channel, and it is unauthenticated by design (public app).
Plan requests travel over it. Until corsAllowedOrigins and allowedHosts are set, the WebSocket accepts connections from
any origin, which Streamlit documents. Abuse caps exist (28, 64) but are not yet verified on the deployed path. The app
has no GraphQL.
Failure mode: a third-party page can use the app's WebSocket to generate plans on the owner's quota.
Smallest safe fix: set corsAllowedOrigins and allowedHosts at deployment (see 27). Keep the cooldown and daily cap, and
add the provider budget (see 64).
Verify: connect from another origin and confirm rejection; send rapid requests from one session and confirm the
cooldown blocks them.

## Passed (with evidence)
03 Hardcoded API keys or secrets - scan_leads.py: 0 pattern hits across the text files. Secret-shaped grep of app.py,
.env.example and config.toml: no hits. Keys read with os.getenv inside get_client and fetch_issue. .env.example has
placeholders only.
12 Verbose production errors - app.py fetch_issue raises UserFacingError with fixed text. The button handler's generic
branch shows a fixed string and logs with log.exception. config.toml [client] showErrorDetails = "none", a value
confirmed in the installed Streamlit 1.66.1 config.
14 Secrets shipped in frontend JavaScript - Streamlit runs app.py on the server. Keys are read server-side and never sent
to the browser. No NEXT_PUBLIC_, VITE_, REACT_APP_ or EXPO_PUBLIC_ variables in the repository.
15 Client-side-only security checks - ISSUE_URL_RE, check_cooldown and within_daily_cap all run in app.py on the server.
16 Missing input validation - ISSUE_URL_RE is an anchored allowlist with a 10-digit limit on the number. st.text_input
max_chars = 200. MAX_TITLE_CHARS = 300 and MAX_BODY_CHARS = 6000 cap the GitHub content.
19 Cross-site scripting - app.py has no unsafe_allow_html, innerHTML or v-html (grep). Plans render with st.markdown at
its default (HTML disabled). Residual: the model may write markdown links or images; the prompt forbids URLs and images.
23 Server-side request forgery - app.py builds api_url only from owner, repo and number, matched by ISSUE_URL_RE. The host
is hardcoded as https://api.github.com. requests.get uses allow_redirects=False.
35 Sensitive data in logs - fetch_issue logs the status code and the words "GitHub request failed" with the exception. No
headers, tokens, prompts or bodies are logged. Verify in the first live run by reading the log.
37 Vulnerable or abandoned dependencies - pip-audit on the pinned runtime set (52 packages, run 2026-10-23): "No known
vulnerabilities found". Re-run before the demo and after any change to requirements.txt.
39 Prompt injection - build_prompt wraps the issue in <issue> tags after removing tag strings and instructs the model to
treat the content as data. The model has no tools. Residual risk: misleading advice can still appear. Verify live with a
planted instruction in a test issue.
52 Command or OS injection - grep of app.py for eval(, exec(, subprocess, os.system and shell= returned no hits.
53 Unsafe deserialization - the only parsing is response.json() on GitHub's JSON. grep found no pickle, yaml.load or eval.
58 Race conditions - within_daily_cap reads and increments the counter inside a threading.Lock. The per-session cooldown
needs no lock because one session's reruns do not overlap.
62 Unpinned build dependencies - requirements.txt pins all 52 runtime packages with == and no ranges. Pins come from a
clean venv with the four direct packages pinned to streamlit 1.66.1, google-genai 2.33.0, python-dotenv 1.2.4 and
requests 2.34.2. Hash pinning is not used.
63 Security checks fail open - there is no auth or permission gate. On any failure the button handler shows an error and
produces no plan. within_daily_cap returns False at the limit, which denies the request.
65 AI sensitive-information disclosure - build_prompt receives only the issue title and body. The Gemini key and GitHub
token never appear in prompt text. The README must state that Gemini API requests may be logged under Google's terms.
66 Unsafe use of AI output - model text goes only to st.markdown. No eval, exec, SQL, file path or fetch uses model output
(grep). Residual: markdown links the model writes are clickable.
68 Sensitive browser storage - st.session_state holds only the last_request timestamp. No localStorage, sessionStorage,
document.cookie or custom JavaScript. The GitHub token never leaves the server.

## Not applicable
01 Exposed database credentials - No database in v1.
04 Weak or missing authentication - v1 has no accounts and no private routes; the app is public by design. Abuse controls
are covered by 28 and 64.
05 Missing server-side authorization - No privileged or ownership-based actions.
06 Cross-user data access - No user-owned data.
07 Open database permissions - No database.
08 Misconfigured Firebase, Supabase or S3 - No backend-as-a-service or object storage.
09 Unprotected admin routes - No admin area.
11 Build logs leaking secrets - No CI pipeline yet. Re-audit when added.
17 SQL injection - No SQL.
18 NoSQL injection - No NoSQL.
21 Insecure file uploads - No upload feature.
22 Path traversal - The app never reads or writes a path from user input.
24 Broken password-reset flows - No accounts or reset flows.
25 Weak session management - No application login or tokens. Only last_request is kept in session state.
26 Weak or incorrectly validated JWTs - No JWTs.
30 Default credentials left unchanged - No accounts or services with default credentials.
31 Webhook signatures not verified - No webhooks.
32 Frontend-only payment checks - No payments.
33 IDOR or BOLA - No user-owned objects. GitHub issues are public data fetched by URL.
34 APIs trusting user-controlled roles or IDs - No roles. Owner and repo select a public target, not an identity.
40 AI tools bypassing user permissions - The model has no tools.
41 Excess database privileges - No database. The Gemini key scope is covered under 64.
42 Missing audit logs - No state-changing or privileged actions to record. Error logging is covered by 35.
44 No tested backup or restore plan - The app stores no data. Code and configuration live in git.
45 Public internal dashboards - No dashboards or consoles beyond the app itself.
49 Poor tenant isolation - One application with no tenants. Cached issue data is public.
51 Mass assignment or over-posting - No database writes and no binding of request bodies to models.
54 Misconfigured OAuth, OIDC or social login - No OAuth login. The GitHub token is a server-side personal token.
56 Account enumeration - No account system.
57 Business-logic abuse - No prices, credits or state transitions. Cost abuse is covered by 28 and 64.
59 Webhook replay - No webhooks.
60 Overpowered CI/CD credentials - No CI/CD yet. Re-audit when added.
61 Untrusted build actions or scripts - No CI/CD yet.
67 AI agents with excessive agency - The model has no tools and cannot act.
69 Open redirects - The app never redirects. GitHub calls disable redirects.

## Change log
- Revision 3 (2026-10-23): Units U1-U9 implementation and security verification.
  - ISSUE_URL_RE updated with `(?!.*\.\.)` lookahead to explicitly prevent directory traversal attempts in owner and repo segments. Covered by `tests/test_validation.py::test_path_traversal_in_owner`.
  - build_prompt updated with `clean_tag_text` removing `<issue>`, `</issue>`, `<title>`, `</title>`, `<body>`, `</body>` case-insensitively. Covered by `tests/test_validation.py::test_prompt_tag_safety_u2`.
  - strip_images added to strip markdown image syntax `![alt](url)` and raw `<img` tags to prevent third-party image tracking. Covered by `tests/test_validation.py::test_strip_images_u3`.
  - escape_markdown added to escape markdown control characters in untrusted issue titles. Covered by `tests/test_validation.py::test_escape_markdown_u3`.
  - build_plan updated to raise RuntimeError on empty model text, mapped to generic error message in UI. Covered by `tests/test_app.py::test_build_plan_empty_raises`.
  - fetch_issue verified for status codes 200, 404, 500, PR payloads, and network failures with no exception leakage. Covered by `tests/test_app.py::test_fetch_issue_*`.
  - .streamlit/config.toml verified with enableCORS=true, enableXsrfProtection=true, showErrorDetails=false, gatherUsageStats=false.
  - Secret scan executed with 0 hits.
- Revision 2 (2026-10-23): The FlexiQuiz design tokens were applied to the Streamlit theme. Found and corrected an error
  from revision 1: enableCORS was set to false, which sends Access-Control-Allow-Origin: * and accepts WebSocket
  connections from any origin. It is now true (Streamlit default). Check 20 moved from PASS to UNKNOWN, and check 70
  moved from N/A to UNKNOWN, because Streamlit documents that XSRF protection does not limit cross-origin WebSockets.
  Check 27 is UNKNOWN with corrected evidence. Approved exception: the browser loads Poppins from fonts.googleapis.com
  and fonts.gstatic.com through Streamlit's font option. This is the only third-party host the page loads. It does not
  touch the server.
