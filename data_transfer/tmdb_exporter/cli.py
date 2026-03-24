import argparse
from .tmdb_exporter import TMDBExporter, TMDBFetcher
import dotenv
import os
from anthropic import Anthropic
from .reviews_aggregator import ReviewsAggregator

def main():
    dotenv.load_dotenv()

    # ── Parse cli arguments ────────────────────────────────────
    parser = argparse.ArgumentParser(description="TMDB_Exporter")
    parser.add_argument("--count", type=int, required=True, help="Number of movies to export")
    parser.add_argument("--endpoint", type = str, required=True,choices=["popular","top_rated"])
    parser.add_argument("--output-dir", type=str, required=False, default="output",  help="Directory to save exported CSV files")


    args = parser.parse_args() 

    # ── Initialize fetcher and exporter ───────────────────────────────────────
    fetcher = TMDBFetcher(os.getenv("TMDB_BEARER_TOKEN"))
    reviews_aggregator = ReviewsAggregator(Anthropic())
    exporter = TMDBExporter(fetcher,reviews_aggregator= reviews_aggregator, output_dir=args.output_dir)

    # ── Export data ───────────────────────────────────────────────────────────────────────
    exporter.export_countries()

    if args.endpoint == "popular":
        movie_ids = fetcher.get_popular_movie_ids(args.count)
    elif args.endpoint == "top_rated":
        movie_ids = fetcher.get_top_rated_movie_ids(args.count)
        
    for movie_id in movie_ids:
        exporter.export_movies(movie_id)
        exporter.export_people(movie_id)
        exporter.export_companies(movie_id) 
        
    exporter.export_genres()
    exporter.export_jobs()

        
if __name__ == "__main__":
    main()


   