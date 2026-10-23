from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

APP_PATH = str(Path(__file__).parent.parent / "app.py")


def test_ui_empty_input_warning():
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()
    assert not at.exception
    # Title Quizora appears
    assert at.title[0].value == "Quizora"

    # Click the build button with empty input
    at.button[0].click().run()
    assert not at.exception
    assert len(at.warning) > 0
    assert at.warning[0].value == "Paste a GitHub issue link first."


def test_ui_invalid_url_error():
    at = AppTest.from_file(APP_PATH, default_timeout=10)
    at.run()

    with patch("requests.get") as mock_get:
        at.text_input[0].input("https://invalid-url.com/something").run()
        at.button[0].click().run()
        assert not at.exception
        assert len(at.error) > 0
        assert at.error[0].value == "Use a link like https://github.com/owner/repo/issues/123"
        # Invariant: no network call to GitHub on invalid URL
        mock_get.assert_not_called()
