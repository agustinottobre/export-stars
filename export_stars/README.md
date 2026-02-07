# export-stars

Export a GitHub user's starred repositories to CSV.

## Quickstart

```bash
# Create virtual environment with specific Python version and install dependencies
uv venv --python 3.11
uv pip install -r pyproject.toml --extra-index-url https://pypi.org/simple

# Or simply (if pyproject.toml is configured)
uv sync
```

### Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) - Fast Python package and project manager

## Usage

### Using environment variable

```bash
GH_USER=defunkt uv run export_stars.py > stars.csv
```

### Using command-line argument

```bash
uv run export_stars.py --user defunkt > stars.csv
```

### With GitHub token (for higher rate limits)

```bash
GH_USER=defunkt uv run export_stars.py --github-token YOUR_TOKEN > stars.csv
```

### Adjust rate limiting delay

If you're hitting rate limits, increase the delay between requests:

```bash
# Default is 1.0 second between page requests
GH_USER=defunkt uv run export_stars.py --delay 2.0 > stars.csv
```

## Development

```bash
# Run the script
uv run export_stars.py --help

# Add new dependencies
uv add <package>

# Update dependencies
uv lock --upgrade
```

## Output Format

The script outputs CSV with two columns:
- `html_url` - The GitHub repository URL
- `description` - The repository description

## License

MIT