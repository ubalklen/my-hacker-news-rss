import requests
from feedgen.feed import FeedGenerator
import os
import argparse
from datetime import datetime, timezone
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

HN_API_BASE = "https://hacker-news.firebaseio.com/v0"
OUTPUT_DIR = "public"
OUTPUT_FILE = "feed.xml"


def load_keywords_from_file(filepath: str) -> list[str]:
    """Load keywords from a file, one keyword per line."""
    try:
        with open(filepath, "r") as f:
            keywords = [line.strip() for line in f if line.strip()]
        logging.info(f"Loaded {len(keywords)} keywords from {filepath}")
        return keywords
    except FileNotFoundError:
        logging.error(f"Keywords file not found: {filepath}")
        return []
    except Exception as e:
        logging.error(f"Error loading keywords from {filepath}: {e}")
        return []


def load_keywords_from_env(env_var_name: str) -> list[str]:
    """Load keywords from an environment variable (comma separated)."""
    env_val = os.environ.get(env_var_name)
    if env_val:
        keywords = [k.strip() for k in env_val.split(",") if k.strip()]
        logging.info(
            f"Loaded {len(keywords)} keywords from environment variable {env_var_name}"
        )
        return keywords
    else:
        logging.warning(f"Environment variable {env_var_name} not found or empty.")
        return []


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


def fetch_comment_details(comment_id: int) -> dict | None:
    """Fetch details for a specific comment."""
    try:
        response = requests.get(f"{HN_API_BASE}/item/{comment_id}.json", timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logging.error(f"Error fetching comment {comment_id}: {e}")
        return None


def fetch_top_comment(story: dict) -> str | None:
    """Fetch the top comment text for a story.
    
    Returns the text of the first comment if available, None otherwise.
    """
    kids = story.get("kids", [])
    if not kids:
        return None
    
    top_comment_id = kids[0]
    comment = fetch_comment_details(top_comment_id)
    
    if comment and "text" in comment:
        return comment["text"]
    
    return None


def matches_keyword(text: str, keyword: str) -> bool:
    """Check if keyword matches as a whole word in text (case-insensitive).

    Uses word boundaries to avoid false positives like 'AI' matching 'airlines'.
    """
    # Create a regex pattern with word boundaries
    # \b matches word boundaries (transition between word and non-word character)
    pattern = r"\b" + re.escape(keyword) + r"\b"
    return bool(re.search(pattern, text, re.IGNORECASE))


def filter_stories(story_ids: list[int], keywords: list[str]) -> list[dict]:
    """Filter stories based on keywords in the title. If keywords is empty, return all stories."""
    filtered_stories = []
    for story_id in story_ids:
        story = fetch_story_details(story_id)
        if not story or "title" not in story:
            continue

        # Some stories might not have a URL (e.g. Ask HN), link to HN item instead
        if "url" not in story:
            story["url"] = f"https://news.ycombinator.com/item?id={story['id']}"

        title = story["title"]
        if not keywords or any(matches_keyword(title, keyword) for keyword in keywords):
            filtered_stories.append(story)
            if keywords:
                logging.info(f"Found match: {title}")
            else:
                logging.debug(f"Adding story (no filter): {title}")

    return filtered_stories


def generate_rss(stories: list[dict], output_path: str):
    """Generate RSS feed from stories."""
    fg = FeedGenerator()
    fg.id("https://news.ycombinator.com/")
    fg.title("Hacker News Filtered Topics")
    fg.author({"name": "Hacker News RSS Bot"})
    fg.link(href="https://news.ycombinator.com/", rel="alternate")
    fg.subtitle("Filtered stories from Hacker News")
    fg.language("en")

    for story in stories:
        comments_url = f"https://news.ycombinator.com/item?id={story.get('id')}"
        fe = fg.add_entry()
        fe.id(str(story.get("id")))
        fe.title(story.get("title"))
        fe.link(href=comments_url)
        fe.published(datetime.fromtimestamp(story.get("time"), tz=timezone.utc))

        # Use top comment as description
        top_comment = fetch_top_comment(story)
        if top_comment:
            fe.description(top_comment)
        else:
            # Fallback to original behavior if no comment available
            original_url = story.get("url")
            if original_url and original_url != comments_url:
                fe.description(f"Article: {original_url}")
            else:
                fe.description(f"Comments: {comments_url}")

    fg.rss_file(output_path)
    logging.info(f"RSS feed generated at {output_path}")


def parse_args():
    parser = argparse.ArgumentParser(description="Hacker News RSS Filter")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--keywords", nargs="+", help="List of keywords to filter by")
    group.add_argument("--keywords-file", help="Path to a file containing keywords")
    group.add_argument(
        "--keywords-env",
        help="Name of the environment variable containing keywords (comma separated)",
    )
    return parser.parse_args()


def main():
    logging.info("Starting HN RSS fetcher...")

    args = parse_args()
    keywords = []

    if args.keywords:
        keywords = args.keywords
        logging.info(f"Loaded {len(keywords)} keywords from arguments")
    elif args.keywords_file:
        keywords = load_keywords_from_file(args.keywords_file)
    elif args.keywords_env:
        keywords = load_keywords_from_env(args.keywords_env)
    else:
        # Default behavior: No filtering if no arguments provided
        keywords = []
        logging.info("No keywords provided. Fetching all stories (no filtering).")

    top_ids = fetch_top_stories(limit=100)  # Check top 100 stories
    logging.info(f"Fetched {len(top_ids)} top stories.")

    matching_stories = filter_stories(top_ids, keywords)
    logging.info(f"Found {len(matching_stories)} matching stories.")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_FILE)
    generate_rss(matching_stories, output_path)
    logging.info("Done.")


if __name__ == "__main__":
    main()
