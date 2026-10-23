import json
from unittest.mock import MagicMock, patch
from pathlib import Path
import pytest
from streamlit.testing.v1 import AppTest

from app import generate_quiz_json

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_generate_quiz_json_success():
    sample_quiz = [
        {
            "question": "What is Python?",
            "options": ["A snake", "A programming language", "A car", "A fruit"],
            "answer": "A programming language",
            "explanation": "Python is a widely used high-level programming language.",
        }
    ]

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = json.dumps(sample_quiz)
    mock_client.models.generate_content.return_value = mock_resp

    with patch("app.get_client", return_value=mock_client):
        result = generate_quiz_json("Python", 1, "Easy")
        assert len(result) == 1
        assert result[0]["question"] == "What is Python?"
        assert result[0]["answer"] == "A programming language"


def test_generate_quiz_json_markdown_wrapped():
    sample_quiz = [
        {
            "question": "What is 2+2?",
            "options": ["3", "4", "5", "6"],
            "answer": "4",
            "explanation": "2 plus 2 equals 4.",
        }
    ]

    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = f"```json\n{json.dumps(sample_quiz)}\n```"
    mock_client.models.generate_content.return_value = mock_resp

    with patch("app.get_client", return_value=mock_client):
        result = generate_quiz_json("Math", 1, "Easy")
        assert len(result) == 1
        assert result[0]["answer"] == "4"


def test_ui_smoke_test():
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    assert not at.exception
    # Title appears
    assert "Quizora" in at.title[0].value

    # Click button without topic -> warning
    at.button[0].click().run()
    assert not at.exception
    assert len(at.warning) > 0
    assert "enter a topic first" in at.warning[0].value
