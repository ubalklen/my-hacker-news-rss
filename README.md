# Hacker News RSS - AI Topics

A Python-based RSS feed generator that filters Hacker News top stories for AI and machine learning related topics. The feed is automatically updated every 6 hours via GitHub Actions and published to GitHub Pages.

## Features

- 🔍 **Keyword-based filtering**: Filters Hacker News top stories based on customizable AI/ML keywords
- 📰 **RSS feed generation**: Creates a clean RSS feed compatible with any RSS reader
- ⏰ **Automated updates**: Runs every 6 hours via GitHub Actions
- 🌐 **GitHub Pages deployment**: Automatically publishes the RSS feed to a public URL
- 🎯 **Smart matching**: Uses word boundary detection to avoid false positives (e.g., "AI" won't match "airlines")

## How It Works

1. Fetches the top 100 stories from Hacker News API
2. Filters stories whose titles contain any of the configured keywords
3. Generates an RSS feed with matching stories
4. Deploys the feed to GitHub Pages

## Requirements

- Python 3.12 or higher
- Dependencies managed via `uv` package manager

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ubalklen/hackernews-rss-ai-topics.git
   cd hackernews-rss-ai-topics
   ```

2. Install `uv` (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Install dependencies:
   ```bash
   uv sync
   ```

## Usage

### Running Locally

Generate the RSS feed manually:

```bash
uv run src/main.py
```

The generated RSS feed will be saved to `public/feed.xml`.

### Automated Updates

The repository is configured with GitHub Actions to automatically:
- Run every 6 hours (configurable in `.github/workflows/update_feed.yml`)
- Generate a fresh RSS feed
- Deploy it to GitHub Pages

You can also manually trigger the workflow from the Actions tab in GitHub.

## Configuration

### Customizing Keywords

Edit `keywords.txt` to add or remove AI/ML-related keywords. Each keyword should be on its own line:

```
GPT
LLM
AI
Machine Learning
Neural Network
OpenAI
Claude
Gemini
Llama
DeepSeek
```

The filter uses case-insensitive matching with word boundaries to ensure accurate results.

## Development

### Running Tests

```bash
uv run pytest
```

### Linting

```bash
uv run ruff check .
```

### Project Structure

```
.
├── src/
│   └── main.py           # Main script for fetching and filtering stories
├── tests/
│   └── test_main.py      # Unit tests
├── .github/
│   └── workflows/
│       └── update_feed.yml  # GitHub Actions workflow
├── keywords.txt          # List of AI/ML keywords
├── pyproject.toml        # Project configuration
└── README.md            # This file
```

## RSS Feed

Once deployed, the RSS feed is available at:
```
https://<username>.github.io/hackernews-rss-ai-topics/feed.xml
```

Replace `<username>` with your GitHub username.

## Contributing

Contributions are welcome! Feel free to:
- Add new keywords to `keywords.txt`
- Improve the filtering logic
- Enhance the RSS feed format
- Fix bugs or improve documentation

## License

This project is open source and available under the terms specified in the repository.
