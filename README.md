# Quizora: Issue-to-First-PR Mentor

[![CI](https://github.com/placeholder/quizora/actions/workflows/ci.yml/badge.svg)](https://github.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)

**Quizora** turns public GitHub issues into structured, approachable contribution plans for first-time open-source contributors.

A beginner pastes a link to any public GitHub issue. Quizora fetches the issue details through GitHub's REST API, prompts Google's open-weight **Gemma 4** model via the Gemini API, and provides a clear five-section roadmap:
1. **What it asks for**: Plain-language summary.
2. **Difficulty for a beginner**: Easy, Medium, or Hard with rationale.
3. **Files to read first**: Initial files to inspect in the repository.
4. **Step-by-step plan**: 5 actionable steps from fork to pull request.
5. **Questions to ask the maintainer**: Thoughtful clarifying questions.

> **Important:** This plan is a starting point. Always check it against the repository, its README, and its `CONTRIBUTING.md`.

---

## 🚀 Live Deployment Guide

Quizora is built to be deployed live instantly without any issues.

### Option 1: Deploy to Railway (Recommended)
Railway natively supports long-lived WebSocket connections required by Streamlit.

1. **Push your code to a GitHub repository.**
2. Go to [railway.app](https://railway.app/) and click **New Project** -> **Deploy from GitHub repo**.
3. Select your Quizora repository.
4. Add the required Environment Variables in the Railway Dashboard under **Variables**:
   - `GEMINI_API_KEY`: Your Google Gemini API key.
   - `GITHUB_TOKEN` *(optional)*: GitHub personal access token for higher rate limits.
   - `GEMMA_MODEL`: `gemma-4-26b-a4b-it` *(default)*.
   - `DAILY_PLAN_CAP`: `100` *(or desired daily cap)*.
5. Railway will automatically detect the included `Procfile` / `railway.json` / `Dockerfile` and start Streamlit on the dynamically assigned `$PORT`.
6. Click **Generate Domain** under Settings -> Networking to get your public HTTPS URL.

---

### Option 2: Deploy to Vercel
Streamlit requires persistent WebSockets and a running server process. If deploying on Vercel:
- Use Vercel's Git integration with the included `vercel.json` rewrite configuration or Docker deployment.
- Alternatively, for the best production experience with Streamlit, host the application on Railway or Streamlit Community Cloud.

---

## 💻 Local Quickstart

### Prerequisites
- Python 3.12+ installed
- Google Gemini API key (from [Google AI Studio](https://aistudio.google.com/))
- *(Optional)* GitHub personal access token (public read-only)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/quizora.git
   cd quizora
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```

3. Install the audited and pinned dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure your environment:
   ```bash
   cp .env.example .env
   ```
   Add your `GEMINI_API_KEY` to `.env`. Never commit this file.

5. Start the application:
   ```bash
   streamlit run app.py
   ```
   Open your browser at `http://localhost:8501`.

---

## 🧪 Testing and Verification

Run the comprehensive test suite (22 unit, validation, and UI smoke tests):
```bash
python -m pytest tests/ -v
```

Syntax check:
```bash
python -m py_compile app.py
```

---

## 🔒 Security & Privacy Notice

- **Untrusted Input**: All GitHub issue text and model responses are treated as untrusted data. HTML rendering is disabled, tags are stripped case-insensitively, and images are cleansed to prevent third-party tracking.
- **SSRF & Network Invariant**: The server initiates network connections exclusively to `api.github.com` and the official Gemini API endpoint.
- **No Persistence**: Quizora stores no user accounts, passwords, personal information, or plan history on disk.
- **Gemini API Logging**: Plan generation requests are processed by Google's Gemini API and may be logged in accordance with [Google's Terms of Service and Privacy Policy](https://policies.google.com/terms). Do not paste sensitive or private issues into this demo.

---

## 🤖 Model Information & License

- **Model Used**: Google Gemma 4 (`gemma-4-26b-a4b-it`) accessed through the Gemini API client (`google-genai` v2.33.0).
- **Model Card & License**: Gemma models are open-weight models released by Google under the Gemma Terms of Use. (Verify exact license terms on the Google AI Studio model card).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
