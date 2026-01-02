from unittest.mock import patch, MagicMock, mock_open
from src.main import (
    filter_stories,
    fetch_top_stories,
    load_keywords_from_file,
    load_keywords_from_env,
    matches_keyword,
    fetch_comment_details,
    fetch_top_comment,
    main,
)
import argparse
import os


def test_load_keywords_from_file():
    mock_keywords_content = "GPT\nLLM\nAI\n\nMachine Learning\n"
    with patch("builtins.open", mock_open(read_data=mock_keywords_content)):
        keywords = load_keywords_from_file("keywords.txt")
        assert len(keywords) == 4
        assert "GPT" in keywords
        assert "LLM" in keywords
        assert "AI" in keywords
        assert "Machine Learning" in keywords


def test_load_keywords_from_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        keywords = load_keywords_from_file("nonexistent.txt")
        assert keywords == []


def test_load_keywords_from_env():
    with patch.dict(os.environ, {"TEST_KEYWORDS": "Python, Rust, GoLang"}):
        keywords = load_keywords_from_env("TEST_KEYWORDS")
        assert len(keywords) == 3
        assert "Python" in keywords
        assert "Rust" in keywords
        assert "GoLang" in keywords


def test_load_keywords_from_env_missing():
    with patch.dict(os.environ, {}, clear=True):
        keywords = load_keywords_from_env("NONEXISTENT_VAR")
        assert keywords == []


@patch("src.main.fetch_top_stories")
@patch("src.main.filter_stories")
@patch("src.main.generate_rss")
@patch("src.main.load_keywords_from_file")
@patch("src.main.load_keywords_from_env")
def test_main_priority_args(
    mock_load_env,
    mock_load_file,
    mock_generate,
    mock_filter,
    mock_fetch,
):
    # Test priority 1: Direct args
    with patch(
        "src.main.parse_args",
        return_value=argparse.Namespace(
            keywords=["Arg1", "Arg2"], keywords_file=None, keywords_env=None
        ),
    ):
        main()
        # Should use args directly, not call file or env loaders
        mock_load_file.assert_not_called()
        mock_load_env.assert_not_called()
        # Verify filter was called with the args
        mock_filter.assert_called_with(mock_fetch.return_value, ["Arg1", "Arg2"])


@patch("src.main.fetch_top_stories")
@patch("src.main.filter_stories")
@patch("src.main.generate_rss")
@patch("src.main.load_keywords_from_file")
@patch("src.main.load_keywords_from_env")
def test_main_priority_file(
    mock_load_env,
    mock_load_file,
    mock_generate,
    mock_filter,
    mock_fetch,
):
    # Test priority 2: File args
    mock_load_file.return_value = ["File1"]
    with patch(
        "src.main.parse_args",
        return_value=argparse.Namespace(
            keywords=None, keywords_file="test.txt", keywords_env=None
        ),
    ):
        main()
        mock_load_file.assert_called_with("test.txt")
        mock_load_env.assert_not_called()
        mock_filter.assert_called_with(mock_fetch.return_value, ["File1"])


@patch("src.main.fetch_top_stories")
@patch("src.main.filter_stories")
@patch("src.main.generate_rss")
@patch("src.main.load_keywords_from_file")
@patch("src.main.load_keywords_from_env")
def test_main_priority_env(
    mock_load_env,
    mock_load_file,
    mock_generate,
    mock_filter,
    mock_fetch,
):
    # Test priority 3: Env args
    mock_load_env.return_value = ["Env1"]
    with patch(
        "src.main.parse_args",
        return_value=argparse.Namespace(
            keywords=None, keywords_file=None, keywords_env="TEST_VAR"
        ),
    ):
        main()
        mock_load_file.assert_not_called()
        mock_load_env.assert_called_with("TEST_VAR")
        mock_filter.assert_called_with(mock_fetch.return_value, ["Env1"])


@patch("src.main.fetch_top_stories")
@patch("src.main.filter_stories")
@patch("src.main.generate_rss")
@patch("src.main.load_keywords_from_file")
@patch("src.main.load_keywords_from_env")
def test_main_no_args(
    mock_load_env,
    mock_load_file,
    mock_generate,
    mock_filter,
    mock_fetch,
):
    # Test priority 4: No args (Default)
    with patch(
        "src.main.parse_args",
        return_value=argparse.Namespace(
            keywords=None, keywords_file=None, keywords_env=None
        ),
    ):
        main()
        mock_load_file.assert_not_called()
        mock_load_env.assert_not_called()
        # Should pass empty list to filter (no filtering)
        mock_filter.assert_called_with(mock_fetch.return_value, [])


def test_filter_stories():
    mock_stories = {
        1: {"id": 1, "title": "GPT-4 is amazing", "url": "http://example.com/1"},
        2: {"id": 2, "title": "Cooking recipes", "url": "http://example.com/2"},
        3: {"id": 3, "title": "New AI model released", "url": "http://example.com/3"},
    }

    with patch(
        "src.main.fetch_story_details", side_effect=lambda id: mock_stories.get(id)
    ):
        filtered = filter_stories([1, 2, 3], ["GPT", "AI"])
        assert len(filtered) == 2
        assert filtered[0]["id"] == 1
        assert filtered[1]["id"] == 3


@patch("src.main.requests.get")
def test_fetch_top_stories(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = [1, 2, 3, 4, 5]
    mock_get.return_value = mock_response

    ids = fetch_top_stories(limit=3)
    assert len(ids) == 3
    assert ids == [1, 2, 3]


def test_matches_keyword_exact_match():
    """Test that exact keyword matches work"""
    assert matches_keyword("GPT-4 is amazing", "GPT")
    assert matches_keyword("New AI model released", "AI")
    assert matches_keyword("LLM performance", "LLM")


def test_matches_keyword_false_positives():
    """Test that false positives are avoided"""
    # "AI" should not match these words containing "ai"
    assert not matches_keyword("Airlines announce new routes", "AI")
    assert not matches_keyword("Chairman of the board", "AI")
    assert not matches_keyword("Waiter brings the check", "AI")
    assert not matches_keyword("Retail stores closing", "AI")
    assert not matches_keyword("Email provider", "AI")

    # "Machine Learning" should not match partial words
    assert not matches_keyword("Machinery in factories", "Machine")


def test_matches_keyword_case_insensitive():
    """Test that matching is case-insensitive"""
    assert matches_keyword("gpt-4 is great", "GPT")
    assert matches_keyword("New ai model", "AI")
    assert matches_keyword("llm Performance", "LLM")


def test_matches_keyword_with_punctuation():
    """Test that keywords match even with punctuation"""
    assert matches_keyword("GPT-4 is amazing", "GPT")
    assert matches_keyword("AI, ML, and DL", "AI")
    assert matches_keyword("(AI) in healthcare", "AI")
    assert matches_keyword("AI.", "AI")
    assert matches_keyword("AI!", "AI")
    assert matches_keyword("AI?", "AI")
    assert matches_keyword("Using AI/ML", "AI")


def test_matches_keyword_word_boundaries():
    """Test that word boundaries are respected"""
    assert matches_keyword("AI model", "AI")
    assert matches_keyword("The AI revolution", "AI")
    assert not matches_keyword("SAIL boat", "AI")
    assert not matches_keyword("PAID service", "AI")


def test_filter_stories_with_false_positives():
    """Test that filter_stories avoids false positives"""
    mock_stories = {
        1: {"id": 1, "title": "New AI breakthrough", "url": "http://example.com/1"},
        2: {
            "id": 2,
            "title": "Airlines face challenges",
            "url": "http://example.com/2",
        },
        3: {"id": 3, "title": "GPT-4 announced", "url": "http://example.com/3"},
        4: {"id": 4, "title": "Chairman steps down", "url": "http://example.com/4"},
        5: {
            "id": 5,
            "title": "Machine Learning advances",
            "url": "http://example.com/5",
        },
    }

    with patch(
        "src.main.fetch_story_details", side_effect=lambda id: mock_stories.get(id)
    ):
        filtered = filter_stories([1, 2, 3, 4, 5], ["AI", "GPT", "Machine Learning"])
        assert len(filtered) == 3
        # Should match stories 1, 3, and 5
        assert filtered[0]["id"] == 1
        assert filtered[1]["id"] == 3
        assert filtered[2]["id"] == 5


@patch("src.main.requests.get")
def test_fetch_comment_details(mock_get):
    """Test fetching comment details from HN API"""
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "id": 12345,
        "by": "testuser",
        "text": "This is a test comment",
        "time": 1609459200,
    }
    mock_get.return_value = mock_response

    comment = fetch_comment_details(12345)
    assert comment is not None
    assert comment["id"] == 12345
    assert comment["text"] == "This is a test comment"
    assert comment["by"] == "testuser"


@patch("src.main.requests.get")
def test_fetch_comment_details_error(mock_get):
    """Test handling of errors when fetching comment details"""
    import requests
    mock_get.side_effect = requests.RequestException("Network error")

    comment = fetch_comment_details(12345)
    assert comment is None


def test_fetch_top_comment_with_comments():
    """Test fetching top comment when story has comments"""
    story = {
        "id": 1,
        "title": "Test Story",
        "kids": [101, 102, 103],
    }

    mock_comment = {
        "id": 101,
        "by": "commenter1",
        "text": "This is the top comment",
        "time": 1609459200,
    }

    with patch("src.main.fetch_comment_details", return_value=mock_comment):
        top_comment = fetch_top_comment(story)
        assert top_comment == "This is the top comment"


def test_fetch_top_comment_no_comments():
    """Test fetching top comment when story has no comments"""
    story = {
        "id": 1,
        "title": "Test Story",
    }

    top_comment = fetch_top_comment(story)
    assert top_comment is None


def test_fetch_top_comment_empty_kids():
    """Test fetching top comment when story has empty kids array"""
    story = {
        "id": 1,
        "title": "Test Story",
        "kids": [],
    }

    top_comment = fetch_top_comment(story)
    assert top_comment is None


def test_fetch_top_comment_comment_fetch_fails():
    """Test handling when comment fetch fails"""
    story = {
        "id": 1,
        "title": "Test Story",
        "kids": [101],
    }

    with patch("src.main.fetch_comment_details", return_value=None):
        top_comment = fetch_top_comment(story)
        assert top_comment is None


def test_fetch_top_comment_comment_no_text():
    """Test handling when comment has no text field"""
    story = {
        "id": 1,
        "title": "Test Story",
        "kids": [101],
    }

    mock_comment = {
        "id": 101,
        "by": "commenter1",
        "time": 1609459200,
    }

    with patch("src.main.fetch_comment_details", return_value=mock_comment):
        top_comment = fetch_top_comment(story)
        assert top_comment is None
