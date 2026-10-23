# UI Context: Issue-to-First-PR Mentor

The UI follows the FlexiQuiz design system, extracted from the site's own stylesheet. The token source is
design/flexiquiz-design-tokens.json. The visual reference is design/design-system.html. The CSS version is
design/flexiquiz-tokens.css. All three must stay in sync. If a token changes, change all three and the theme in
.streamlit/config.toml, and record the change in progress-tracker.md.

## Aesthetic direction
- Clean, bright and friendly, with a navy heading color and a strong blue call to action.
- White page, soft grey surfaces, pill-shaped buttons, 12px rounded cards with a faint blue glow.
- Poppins throughout, one family only, used at light, regular, medium, semibold and bold weights.
- Plain English copy in sentence case. Short sentences.
- No illustrations or animations in v1.

## Color tokens
These values are copied exactly from the FlexiQuiz stylesheet.

| Role | Token | Value | Used for |
|---|---|---|---|
| Primary | brand.blue | #0071f2 | Primary button, focus ring, Streamlit primaryColor |
| Heading and link | brand.navy | #0f1048 | Headings, nav and link text, Streamlit linkColor |
| Body text | neutral.text | #212529 | Body text, Streamlit textColor |
| Page | neutral.white | #ffffff | Page background, Streamlit backgroundColor |
| Surface | neutral.surface | #f7f8fa | Input fields, plan panel, Streamlit secondaryBackgroundColor |
| Border | neutral.border | #e0e0e0 | Dividers and input borders, Streamlit borderColor |
| Muted text | neutral.muted | #9ca5b0 | Captions and secondary labels |
| Secondary action | brand.seaGreen | #32a775 | Optional secondary button |
| Soft fill | brand.mint | #e3f7ee | Status chips such as "open" |
| Error | accent.error | #eb4963 | Error text only |

Accent colors (teal #2cc6ab, yellow #f5c900, orange #ff8f24, cyan #31b3eb, pink #f8b4b6) are reserved for
future illustrations and stats. Do not use them for text, borders or buttons in v1.

Contrast: navy #0f1048 and body #212529 on white are well above the 4.5:1 WCAG AA minimum. White text on
blue #0071f2 is checked before the demo, and the record is kept in progress-tracker.md. If it fails, darken the
button color only after updating every token source.

Streamlit's own semantic colors (st.warning, st.error, st.success) are not overridden in v1, so beginners see the
standard signals.

## Typography
- Family: Poppins, with sans-serif as fallback. Loaded from Google Fonts through Streamlit's font option (approved
  exception; see change log in SECURITY-AUDIT.md).
- Weights used: 300 (light), 400 (regular, default), 500 (medium), 600 (semibold), 700 (bold).
- Type scale in px: 12, 14, 16 (base), 18, 20, 24, 32, 36, 44, 52, 64.
- Headings default to weight 400 with navy color. Emphasis inside headings uses 600.
- Paragraph line height 25px. Lead paragraphs 31px.
- Line length stays under about 80 characters. The Streamlit layout is centered, which keeps lines short.

## Spacing, radius and elevation
- Section vertical rhythm: 100px on the marketing site. The Mentor screen uses Streamlit's own spacing, which is
  close enough. Do not add custom margins.
- Radius: 4px (xs), 12px (cards, Streamlit baseRadius), 20px (small buttons), 25px (pill buttons, Streamlit
  buttonRadius).
- Card glow: 0 0 12px 12px rgba(52,178,234,.12). Use it only for a card that is the main result.
- Breakpoints for any future custom layout: 576, 768, 992, 1200, 1400 px.

## Components
- Input: st.text_input with a visible label. Never rely on the placeholder alone.
- Button: st.button with the primary style. One per page.
- Waiting: st.spinner with short messages: "Reading the issue..." then "Gemma is writing your plan...".
- Warnings: st.warning for user mistakes (empty input, cooldown).
- Errors: st.error for failures, with fixed text from app.py only.
- Results: st.subheader for the issue title, st.caption for the state, st.markdown for the plan.

## Streamlit theme mapping (.streamlit/config.toml)
primaryColor #0071f2, backgroundColor #ffffff, secondaryBackgroundColor #f7f8fa, textColor #212529,
linkColor #0f1048, borderColor #e0e0e0, baseRadius 12px, buttonRadius 25px, baseFontSize 16, baseFontWeight 400,
font = Poppins from Google Fonts.
Not possible in Streamlit config: the navy heading color, the card glow shadow, and the 100px section spacing.
These appear only in design/design-system.html. Adding them to the app would require custom CSS, which the
architecture invariants forbid.

## Page structure (top to bottom)
1. Title: "Quizora"
2. One-line description: "Paste a public GitHub issue link and get a beginner's plan for contributing."
3. Labelled text input: "GitHub issue URL".
4. Primary button: "Build my plan".
5. Result area, shown only after a request: issue title, state caption, plan, disclaimer caption ("This plan is a starting point. Check it against the repository.").

No sidebar in v1.

## Copy (fixed messages; change only with a reason recorded in progress-tracker.md)
- Empty input: "Paste a GitHub issue link first."
- Bad format: "Use a link like https://github.com/owner/repo/issues/123"
- Cooldown: "Please wait N seconds before the next request."
- Daily cap: "The daily limit for this demo has been reached. Please try again tomorrow."
- Not found: "That issue was not found. Check that the repo is public and the link is correct."
- Pull request: "That link is a pull request. Paste a link to an issue instead."
- GitHub unreachable: "Could not reach GitHub. Please try again."
- Generic failure: "Something went wrong. Please try again in a few minutes."
- Plan disclaimer caption: "This plan is a starting point. Check it against the repository."

## Accessibility
- Every control has a label. Headings are in order.
- Focus must be visible. The primary color gives a clear focus state in Streamlit.
- Test once at 200 percent browser zoom and once at a 390 pixel wide phone viewport.
- Respect the reduced-motion setting. The v1 UI has no custom motion.

## What the UI must never do
- Show a traceback, exception text, response body or request ID.
- Show the API key, token, prompt or raw GitHub JSON.
- Render model output as HTML.
- Load scripts or images from third-party hosts. Fonts are the single approved exception.
- Use unsafe_allow_html, custom CSS or JavaScript components in the app.
