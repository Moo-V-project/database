import argparse
from .tmdb_exporter import TMDBExporter, TMDBFetcher
import dotenv
import os
from anthropic import Anthropic
from .reviews_aggregator import ReviewsAggregator
import logging 



#todo : add logging to the exporter and fetcher methods, especially around API calls and data transformations. This will help in debugging and monitoring the export process.
def main():

    dotenv.load_dotenv()

    # ── Parse cli arguments ────────────────────────────────────
    parser = argparse.ArgumentParser(description="TMDB_Exporter")
    parser.add_argument("--count", type=int, required=True, help="Number of movies to export")
    parser.add_argument("--endpoint", type = str, required=True,choices=["popular","top_rated"])
    parser.add_argument("--output-dir", type=str, required=False, default="output",  help="Directory to save exported CSV files")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show detailed logs")

    args = parser.parse_args() 
    
    # ──  Set up logging ────────────────────────────────────────────────
    logger = logging.getLogger(__name__)
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s - %(levelname)s - %(message)s') # if need to wr, filename="tmdb_exporter.log", filemode='a')


    # ── Initialize fetcher and exporter ───────────────────────────────────────
    fetcher = TMDBFetcher(os.getenv("TMDB_BEARER_TOKEN"))
    reviews_aggregator = ReviewsAggregator(Anthropic())
    exporter = TMDBExporter(fetcher,reviews_aggregator= reviews_aggregator, output_dir=args.output_dir)

    # ── Export data ───────────────────────────────────────────────────────────────────────
    exporter.export_batch(movie_ids=fetcher.get_popular_movie_ids(args.count) if args.endpoint == "popular" else fetcher.get_top_rated_movie_ids(args.count))

    if args.endpoint == "popular":
        movie_ids = fetcher.get_popular_movie_ids(args.count)
    elif args.endpoint == "top_rated":
        movie_ids = fetcher.get_top_rated_movie_ids(args.count)
        
    for movie_id in movie_ids:
        try:
            exporter.export_movies(movie_id)
            exporter.export_people(movie_id)
            exporter.export_companies(movie_id)
            logger.info(f"Successfully exported movie ID {movie_id}") 
        except Exception as e:
            logger.error(f"Error exporting movie ID {movie_id}: {e}")
            continue
            
    exporter.export_genres()
    exporter.export_jobs()

        
if __name__ == "__main__":
    main()


   