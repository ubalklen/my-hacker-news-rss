import requests
from feedgen.feed import FeedGenerator
import os
from datetime import datetime, timezone
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

KEYWORDS = [
    "GPT",
    "LLM",
    "AI",
    "Machine Learning",
    "Neural Network",
    "OpenAI",
    "Claude",
    "Gemini",
    "Llama",
    "DeepSeek",
]
HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
OUTPUT_DIR = "public"
OUTPUT_FILE = "feed.xml"


def fetch_top_stories(limit: int = 100) -> list[int]:
    """Fetch top story IDs from Hacker News."""
    try:
        response = requests.get(f"{HN_API_BASE}/topstories.json", timeout=10)
        response.raise_for_status()
        return response.json()[:limit]
    except requests.RequestException as e:
        logging.error(f"Error fetching top stories: {e}")
        return []


def fetch_story_details(story_id: int) -> dict | None:
    """Fetch details for a specific story."""
    try:
        response = requests.get(f"{HN_API_BASE}/item/{story_id}.json", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching story {story_id}: {e}")
        return None


def filter_stories(story_ids: list[int], keywords: list[str]) -> list[dict]:
    """Filter stories based on keywords in the title."""
    filtered_stories = []
    for story_id in story_ids:
        story = fetch_story_details(story_id)
        if not story or "title" not in story:
            continue

        # Some stories might not have a URL (e.g. Ask HN), link to HN item instead
        if "url" not in story:
            story["url"] = f"https://news.ycombinator.com/item?id={story['id']}"

        title = story["title"]
        if any(keyword.lower() in title.lower() for keyword in keywords):
            filtered_stories.append(story)
            logging.info(f"Found match: {title}")

    return filtered_stories


def generate_rss(stories: list[dict], output_path: str):
    """Generate RSS feed from stories."""
    fg = FeedGenerator()
    fg.id("https://news.ycombinator.com/")
    fg.title("Hacker News AI Topics")
    fg.author({"name": "Hacker News RSS Bot"})
    fg.link(href="https://news.ycombinator.com/", rel="alternate")
    fg.subtitle("Top AI/ML stories from Hacker News")
    fg.language("en")

    for story in stories:
        fe = fg.add_entry()
        fe.id(str(story.get("id")))
        fe.title(story.get("title"))
        fe.link(href=story.get("url"))
        fe.published(datetime.fromtimestamp(story.get("time"), tz=timezone.utc))
        fe.description(
            f"Comments: https://news.ycombinator.com/item?id={story.get('id')}"
        )

    fg.rss_file(output_path)
    logging.info(f"RSS feed generated at {output_path}")


def main():
    logging.info("Starting HN RSS fetcher...")
    top_ids = fetch_top_stories(limit=100)  # Check top 100 stories
    logging.info(f"Fetched {len(top_ids)} top stories.")

    matching_stories = filter_stories(top_ids, KEYWORDS)
    logging.info(f"Found {len(matching_stories)} matching stories.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    generate_rss(matching_stories, output_path)
    logging.info("Done.")


if __name__ == "__main__":
    main()
