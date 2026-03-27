import json
from data_transfer.tmdb_exporter.tmdb_exporter import TMDBFetcher
import os
from dotenv import load_dotenv
import pathlib

load_dotenv()

output_dir = pathlib.Path(__file__).parent
fetcher = TMDBFetcher(os.getenv("TMDB_BEARER_TOKEN"))

movie = fetcher.get_movie_details(550)
with open(output_dir/"movie_550.json", "w", encoding="utf-8") as f:
    json.dump(movie, f, ensure_ascii=False, indent=2)

credits = fetcher.get_movie_credits(550)
with open(output_dir/"credits_550.json", "w", encoding="utf-8") as f:
    json.dump(credits, f, ensure_ascii=False, indent=2)
    