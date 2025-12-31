# Hacker News RSS AI Topics

An automated RSS feed generator that filters Hacker News top stories for AI and Machine Learning related content.

## Overview

This project automatically fetches the top stories from Hacker News, filters them based on AI/ML keywords, and generates an RSS feed that's published via GitHub Pages. The feed updates every 6 hours automatically.

## Features

- 🤖 Automatically filters Hacker News stories for AI/ML topics
- 📰 Generates a clean RSS feed with matched stories
- ⏰ Updates every 6 hours via GitHub Actions
- 🌐 Published automatically to GitHub Pages
- 🔍 Searches for keywords: GPT, LLM, AI, Machine Learning, Neural Network, OpenAI, Claude, Gemini, Llama, DeepSeek

## RSS Feed

Subscribe to the feed at: `https://<username>.github.io/hackernews-rss-ai-topics/feed.xml`

Replace `<username>` with the repository owner's GitHub username.

## How It Works

1. Fetches the top 100 stories from Hacker News API
2. Filters stories whose titles contain AI/ML-related keywords
3. Generates an RSS feed with the matching stories
4. Publishes the feed to GitHub Pages

## Installation

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ubalklen/hackernews-rss-ai-topics.git
cd hackernews-rss-ai-topics
```

2. Install dependencies:

Using uv (recommended):
```bash
uv sync
```

Or using pip:
```bash
pip install -e .
```

## Usage

### Run Locally

```bash
uv run src/main.py
```

Or if using pip:
```bash
python src/main.py
```

The RSS feed will be generated at `public/feed.xml`.

### Configure GitHub Pages

1. Go to your repository Settings > Pages
2. Set Source to "GitHub Actions"
3. The workflow will automatically deploy the feed

### Customize Keywords

Edit the `KEYWORDS` list in `src/main.py`:

```python
KEYWORDS = [
    "GPT",
    "LLM",
    "AI",
    "Machine Learning",
    # Add more keywords...
]
```

## Development

### Running Tests

```bash
uv run pytest
```

### Linting

```bash
uv run ruff check .
```

## Project Structure

```
.
├── src/
│   └── main.py          # Main application code
├── tests/
│   └── test_main.py     # Unit tests
├── .github/
│   └── workflows/
│       └── update_feed.yml  # GitHub Actions workflow
├── public/              # Generated RSS feed (created at runtime)
├── pyproject.toml       # Project dependencies
└── README.md            # This file
```

## GitHub Actions Workflow

The project uses GitHub Actions to automatically update the RSS feed:

- **Schedule**: Runs every 6 hours
- **Manual trigger**: Can be triggered manually via workflow_dispatch
- **Deployment**: Automatically deploys to GitHub Pages

## Dependencies

- `feedgen` - RSS feed generation
- `requests` - HTTP requests to Hacker News API
- `pytest` - Testing framework (dev)
- `ruff` - Linting and formatting (dev)

## License

This project is open source and available under the MIT License.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Acknowledgments

- Data provided by [Hacker News API](https://github.com/HackerNews/API)
- Built with [feedgen](https://github.com/lkiesow/python-feedgen)
