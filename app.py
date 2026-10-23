import json
import logging
import os
import re
import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("quizora")

MODEL = os.getenv("GEMMA_MODEL", "gemini-2.5-flash")


@st.cache_resource
def get_client():
    return genai.Client()


def generate_quiz_json(topic: str, num_questions: int = 5, difficulty: str = "Medium"):
    prompt = f"""You are an expert quiz generator. Generate a {difficulty.lower()} level quiz on the topic: "{topic}".
Create exactly {num_questions} multiple-choice questions.

Return ONLY a valid JSON array of objects with no markdown code fences and no extra text.
Each object must have exactly these keys:
- "question": string (the question text)
- "options": list of 4 strings (the multiple choice choices)
- "answer": string (the exact correct option from the options list)
- "explanation": string (brief explanation of why this answer is correct)

Example structure:
[
  {{
    "question": "What is the capital of France?",
    "options": ["Berlin", "Madrid", "Paris", "Rome"],
    "answer": "Paris",
    "explanation": "Paris is the capital of France."
  }}
]
"""
    client = get_client()
    # Try with response_mime_type="application/json"
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7,
            ),
        )
        text = response.text or ""
    except Exception:
        # Fallback without json mime type if model doesn't support it
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
        )
        text = response.text or ""

    # Clean potential markdown wrapping
    cleaned = text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    data = json.loads(cleaned)
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("Invalid quiz structure returned")
    return data


# Streamlit Page Config
st.set_page_config(page_title="Quizora - AI Quiz Taker", page_icon="📝", layout="centered")

# Header
st.title("🎯 Quizora")
st.write("Generate and take instant interactive quizzes on any topic powered by AI.")

# Initialize Session State
if "quiz_data" not in st.session_state:
    st.session_state["quiz_data"] = None
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False
if "user_answers" not in st.session_state:
    st.session_state["user_answers"] = {}

# Quiz Generation Form
with st.container():
    st.subheader("Create a Quiz")
    col1, col2 = st.columns([3, 1])
    with col1:
        topic_input = st.text_input(
            "Topic or Subject",
            placeholder="e.g. Python Programming, World History, Solar System, Biology",
            max_chars=200,
        )
    with col2:
        difficulty_input = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)

    num_q = st.slider("Number of Questions", min_value=3, max_value=10, value=5)

    if st.button("Generate Quiz 🚀", use_container_width=True):
        if not topic_input.strip():
            st.warning("Please enter a topic first!")
        else:
            with st.spinner("AI is crafting your quiz questions..."):
                try:
                    quiz = generate_quiz_json(topic_input.strip(), num_q, difficulty_input)
                    st.session_state["quiz_data"] = quiz
                    st.session_state["submitted"] = False
                    st.session_state["user_answers"] = {}
                    st.session_state["quiz_topic"] = topic_input.strip()
                    st.rerun()
                except Exception as e:
                    log.exception("Quiz generation failed")
                    st.error("Failed to generate quiz. Please check your API key and try again.")

# Display Active Quiz
if st.session_state["quiz_data"]:
    st.divider()
    st.subheader(f"📝 Quiz: {st.session_state.get('quiz_topic', 'Interactive Quiz')}")

    quiz = st.session_state["quiz_data"]
    total = len(quiz)

    with st.form("quiz_form"):
        for i, q in enumerate(quiz):
            st.markdown(f"**Question {i+1} of {total}:** {q['question']}")
            # Formulate options
            opts = q.get("options", [])
            key = f"q_{i}"
            st.radio(
                "Choose your answer:",
                opts,
                key=key,
                index=None,
                disabled=st.session_state["submitted"],
                label_visibility="collapsed",
            )
            st.markdown("---")

        submit_btn = st.form_submit_button("Submit Answers ✨", disabled=st.session_state["submitted"])

    if submit_btn and not st.session_state["submitted"]:
        st.session_state["submitted"] = True
        st.rerun()

    # Results Section
    if st.session_state["submitted"]:
        score = 0
        st.subheader("📊 Your Results")

        for i, q in enumerate(quiz):
            key = f"q_{i}"
            selected = st.session_state.get(key)
            correct = q.get("answer")

            if selected == correct:
                score += 1
                st.success(f"**Q{i+1}: Correct!** ✅  \nYour answer: {selected}")
            else:
                st.error(
                    f"**Q{i+1}: Incorrect** ❌  \nYour answer: {selected or 'No answer selected'}  \n**Correct answer:** {correct}"
                )

            if q.get("explanation"):
                st.info(f"💡 *Explanation:* {q['explanation']}")

        percentage = int((score / total) * 100)
        st.metric(label="Final Score", value=f"{score} / {total} ({percentage}%)")

        if percentage >= 80:
            st.balloons()
            st.success("🏆 Outstanding job! You've mastered this topic.")
        elif percentage >= 50:
            st.info("👍 Good effort! Review the explanations above to improve.")
        else:
            st.warning("Keep practicing! Try taking another quiz on this topic.")

        if st.button("Take Another Quiz 🔄"):
            st.session_state["quiz_data"] = None
            st.session_state["submitted"] = False
            st.session_state["user_answers"] = {}
            st.rerun()
