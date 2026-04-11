import argparse
from .tmdb_exporter import TMDBExporter, TMDBFetcher
import dotenv
import os
from anthropic import Anthropic
from .reviews_aggregator import ReviewsAggregator
import logging 


# ── Build parser───────────────────────────────
def build_parser() -> argparse.ArgumentParser:
     parser = argparse.ArgumentParser(description="TMDB_Exporter")
     parser.add_argument("--count", type=int, required=True, help="Number of movies to export")
     parser.add_argument("--endpoint", type = str, required=True,choices=["popular","top_rated"])
     parser.add_argument("--output-dir", type=str, required=False, default="output",  help="Directory to save exported CSV files")
     parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed logs")
     return parser



def main():
    dotenv.load_dotenv()

    # ── Parse cli arguments ────────────────────────────────────
    args = build_parser().parse_args() 
    
    # ──  Set up logging ────────────────────────────────────────────────
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s') # if need to write logging to file, add  filename="tmdb_exporter.log", filemode='a')
    logger = logging.getLogger(__name__)
    
    # ──  ────────────────────────────────────────────────
    required_keys = ["TMDB_BEARER_TOKEN", "ANTHROPIC_API_KEY"]
    config = {key: os.getenv(key) for key in required_keys}
    
    missing = [k for k, v in config.items() if not v]
    
    if missing:
        logger.error(f"Missing variable:{', '.join(missing)}")
        return 

    # ── Initialize fetcher and exporter ───────────────────────────────────────
    fetcher = TMDBFetcher(config["TMDB_BEARER_TOKEN"])
    client = Anthropic(api_key=config["ANTHROPIC_API_KEY"])
    reviews_aggregator = ReviewsAggregator(client)
    exporter = TMDBExporter(fetcher,reviews_aggregator= reviews_aggregator, output_dir=args.output_dir)

    # ── Export data ───────────────────────────────────────────────────────────────────────
    exporter.export_batch(movie_ids=fetcher.get_popular_movie_ids(args.count) if args.endpoint == "popular" else fetcher.get_top_rated_movie_ids(args.count))
        
        
if __name__ == "__main__":
    main()


   