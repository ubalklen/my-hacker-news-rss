from unittest.mock import patch, MagicMock, mock_open
from src.main import filter_stories, fetch_top_stories, load_keywords, matches_keyword


def test_load_keywords():
    mock_keywords_content = "GPT\nLLM\nAI\n\nMachine Learning\n"
    with patch("builtins.open", mock_open(read_data=mock_keywords_content)):
        keywords = load_keywords("keywords.txt")
        assert len(keywords) == 4
        assert "GPT" in keywords
        assert "LLM" in keywords
        assert "AI" in keywords
        assert "Machine Learning" in keywords


def test_load_keywords_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        keywords = load_keywords("nonexistent.txt")
        assert keywords == []


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
