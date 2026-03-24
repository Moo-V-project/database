# TMDB Exporter

## Overview
This module fetches movie data from the TMDB API and exports it to CSV files for further import into a PostgreSQL database. It includes a ReviewsAggregator powered by Claude Haiku that summarizes movie reviews.

## Project Structure
- `__init__.py` — marks the directory as a Python package
- `cli.py` — CLI application to run export process
- `reviews_aggregator.py` — summarizes movie reviews using Claude Haiku
- `tmdb_exporter.py` — script includes data fetcher and exporter, each of them has its own related methods

## Configuration
Copy `.env.example` to `.env` and fill in your credentials:
```
TMDB_BEARER_TOKEN=your_tmdb_bearer_token
ANTHROPIC_API_KEY=your_anthropic_api_key
```

Never commit `.env` to version control — it contains sensitive API keys.

## Usage

Run the CLI from the project root:
```bash
python -m data_transfer.tmdb_exporter.cli --endpoint [popular|top_rated] --count [number] --output-dir [path]
```

**Arguments:**
- `--endpoint` — which movie list to use: `popular` for most popular right now, `top_rated` for highest rated of all time
- `--count` — number of movies to export
- `--output-dir` — directory to save CSV files (default: `output`)

**Examples:**
```bash
python -m data_transfer.tmdb_exporter.cli --endpoint popular --count 2 --output-dir ./test_exports
python -m data_transfer.tmdb_exporter.cli --endpoint top_rated --count 2 --output-dir ./test_exports
```

## Output

The exporter creates 6 CSV files in the specified `--output-dir`:

- `movies.csv` — movie details
- `people.csv` — cast and crew members
- `companies.csv` — production companies
- `countries.csv` — countries
- `genres.csv` — movie genres
- `jobs.csv` — job titles for cast and crew

For detailed column descriptions see [data_format.md](data_format.md).