# Progress Tracker: Quizora (Issue-to-First-PR Mentor)

Read this file first in every session. It is the single source of truth for where the project
stands. Update it after every meaningful change.

## Current Phase
Phase 2 Complete: Build units U1 to U9 completed, all 22 tests passing, and deployment configurations generated for Railway and Vercel.
Phase 3 Next: Live deployment and submission.

## Current Goal
Deploy Quizora live to Railway / Vercel, configure GEMINI_API_KEY, and verify live execution on a real public good-first issue.

## Completed
- Project scoped to Quizora (Issue-to-First-PR Mentor).
- Decisions D1 to D5 approved and implemented:
  - D1: Product name is Quizora throughout UI, documentation, and metadata.
  - D2: Design tokens structured in design/ directory.
  - D3: LICENSE added with "Quizora contributors" placeholder (MIT).
  - D4: Model name default gemma-4-26b-a4b-it, overridable with GEMMA_MODEL.
  - D5: Production-ready Railway (Procfile, railway.json, Dockerfile) and Vercel configurations created.
- Build units U1 to U9:
  - U1: Repository files (.gitignore, .env.example, .streamlit/config.toml with theme and security settings).
  - U2: Prompt safety (clean_tag_text strips all 6 delimiting tags case-insensitively).
  - U3: Output safety (strip_images removes markdown and HTML images, escape_markdown protects untrusted titles).
  - U4: Copy & branding (Quizora title, fixed copy adherence, generic error on empty model text, disclaimer caption).
  - U5: Input validation tests in tests/test_validation.py (traversal, overlong, malformed, extra segments).
  - U6: Client mock tests in tests/test_app.py (status codes 200, 404, 500, PR payloads, cooldown, daily cap, token headers).
  - U7: Streamlit UI smoke tests in tests/test_ui.py using AppTest (empty input warning, invalid link error).
  - U8: Documentation (README.md, LICENSE, architecture updates, SECURITY-AUDIT.md revision 3).
  - U9: Verification (22/22 tests passing, py_compile verified, 0 secret scan hits, pip dependencies pinned).

## Next Up (User Manual Steps for Live Deployment)
1. Push this repository to GitHub:
   ```bash
   git init
   git add .
   git commit -m "feat: complete Quizora Issue-to-First-PR Mentor v1"
   git remote add origin https://github.com/<your-username>/quizora.git
   git push -u origin main
   ```
2. Deploy to Railway:
   - Link your GitHub repository in [railway.app](https://railway.app/).
   - Add variable: `GEMINI_API_KEY` (and optional `GITHUB_TOKEN`).
   - Railway will build with Nixpacks/Dockerfile and run on the assigned `$PORT`.
3. Verify live URL and complete submission before deadline.

## Open Questions
- Q1: Exact Gemma model identifier in Google AI Studio. Code uses gemma-4-26b-a4b-it (overridable with GEMMA_MODEL).
- Q2: License of the specific Gemma 4 model. To confirm on model card before final submission.
- Q3: Hosting: Railway (recommended for Streamlit WebSockets) and Vercel configured.
- Q4: Submission deadline: Under 20 minutes target requested by user.

## Architecture Decisions
- ADR-001: Single-file Streamlit app for v1 (app.py).
- ADR-002: Gemma 4 is called through the Gemini API.
- ADR-003: Strict allowlist regex with path traversal protection ((?!.*\.\.)).
- ADR-004: No persistence in v1 (zero user data retention).
- ADR-005: Cooldown, daily cap, and provider-side budget for abuse prevention.
- ADR-006: Issue text is untrusted data, stripped of tags and images.
- ADR-007: Streamlit server configured for containerized dynamic port binding ($PORT).

## Session Notes
- Session 2 (2026-10-23): Executed full build units U1-U9. Created .gitignore, .env.example, .streamlit/config.toml, Procfile, railway.json, Dockerfile, vercel.json, LICENSE, README.md, tests/test_validation.py, tests/test_app.py, tests/test_ui.py. All 22 tests passing. Zero secret scan hits. Verified python -m py_compile app.py. Ready for immediate live deployment.
