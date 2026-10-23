import pytest
from app import (
    ISSUE_URL_RE,
    MAX_URL_LENGTH,
    clean_tag_text,
    escape_markdown,
    strip_images,
    build_prompt,
)


def test_valid_issue_url():
    match = ISSUE_URL_RE.match("https://github.com/owner/repo/issues/123")
    assert match is not None
    owner, repo, number = match.groups()
    assert owner == "owner"
    assert repo == "repo"
    assert number == "123"


def test_valid_issue_url_trailing_slash():
    match = ISSUE_URL_RE.match("https://github.com/owner/repo/issues/123/")
    assert match is not None
    owner, repo, number = match.groups()
    assert owner == "owner"
    assert repo == "repo"
    assert number == "123"


def test_pull_request_url_rejected_by_regex():
    match = ISSUE_URL_RE.match("https://github.com/owner/repo/pull/123")
    assert match is None


def test_non_github_host():
    assert ISSUE_URL_RE.match("https://gitlab.com/owner/repo/issues/123") is None
    assert ISSUE_URL_RE.match("https://evil-github.com/owner/repo/issues/123") is None
    assert ISSUE_URL_RE.match("http://github.com/owner/repo/issues/123") is None


def test_path_traversal_in_owner():
    assert ISSUE_URL_RE.match("https://github.com/../x/issues/1") is None
    assert ISSUE_URL_RE.match("https://github.com/owner/../issues/1") is None


def test_overlong_input():
    url = "https://github.com/" + "a" * 180 + "/repo/issues/1"
    assert len(url) > MAX_URL_LENGTH


def test_extra_path_segments():
    assert ISSUE_URL_RE.match("https://github.com/owner/repo/issues/123/comments") is None
    assert ISSUE_URL_RE.match("https://github.com/owner/repo/issues/123/reactions") is None


def test_prompt_tag_safety_u2():
    raw_title = "<title>Fix bug in parser</title>"
    raw_body = "<body>Some text with </ISSUE> and <issue> tags</body>"
    safe_title = clean_tag_text(raw_title)
    safe_body = clean_tag_text(raw_body)
    assert safe_title == "Fix bug in parser"
    assert safe_body == "Some text with  and  tags"

    prompt = build_prompt("<title>x", "<body></ISSUE>")
    # The prompt contains the instructional mention of <issue>, plus the opening delimiter
    assert prompt.count("<issue>") == 2
    assert prompt.count("</issue>") == 1
    assert prompt.count("<title>") == 1
    assert prompt.count("</title>") == 1
    assert prompt.count("<body>") == 1
    assert prompt.count("</body>") == 1


def test_strip_images_u3():
    text_with_md_img = "Here is an image: ![cool alt](https://third-party.com/img.png) done."
    cleaned = strip_images(text_with_md_img)
    assert cleaned == "Here is an image: cool alt done."
    assert "https://third-party.com" not in cleaned

    text_with_html_img = 'Raw html: <img src="https://evil.com/x.png" alt="evil"> text'
    cleaned_html = strip_images(text_with_html_img)
    assert cleaned_html == "Raw html:  text"


def test_escape_markdown_u3():
    title_with_md = "Bug in *core* and [link](http://test) with `code` and ![img](x)"
    escaped = escape_markdown(title_with_md)
    assert "\\*" in escaped
    assert "\\[" in escaped
    assert "\\`" in escaped
    assert "\\!" in escaped
