from unittest.mock import patch, MagicMock
from src.main import filter_stories, fetch_top_stories


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
