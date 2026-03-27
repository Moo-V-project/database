import re
import json
import pathlib
import requests
import csv
import logging
from dotenv import load_dotenv
from typing import Any, Callable
from .reviews_aggregator import ReviewsAggregator

# Setup logger
logger = logging.getLogger(__name__)

APPROVED_CAST_JOBS = {"Voice", "Narrator"}
DEFAULT_CAST_JOB = "Actor"


class TMDBFetcher:
    def __init__(self, bearer_token: str | None):
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/original"
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {bearer_token}",
            "accept": "application/json",
        })

    def fetch(self, endpoint: str, params: dict[str, str] | None = None) -> dict:
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()

    def get_movie_details(self, movie_id: int) -> dict:
        return self.fetch(f"movie/{movie_id}")

    def get_movie_credits(self, movie_id: int) -> dict:
        return self.fetch(f"movie/{movie_id}/credits")

    def get_movie_keywords(self, movie_id: int) -> dict:
        return self.fetch(f"movie/{movie_id}/keywords")

    def get_movie_reviews(self, movie_id: int) -> dict:
        return self.fetch(f"movie/{movie_id}/reviews")

    def get_person_details(self, person_id: int) -> dict:
        return self.fetch(f"person/{person_id}")

    def get_company_details(self, company_id: int) -> dict:
        return self.fetch(f"company/{company_id}")

    def get_countries(self) -> list[dict]:
        result = self.fetch("configuration/countries")
        return result if isinstance(result, list) else []

    def get_genres(self) -> dict:
        return self.fetch("genre/movie/list")["genres"]

    def get_popular_movie_ids(self, count_movies: int) -> list[int]:
        movie_ids = []
        count_page = (count_movies + 19) // 20
        for page in range(1, count_page + 1):
            result = self.fetch("movie/popular", params={"page": str(page)})
            movie_ids.extend([movie["id"] for movie in result.get("results", [])])
        return movie_ids[:count_movies]

    def get_top_rated_movie_ids(self, count_movies: int) -> list[int]:
        movie_ids = []
        count_page = (count_movies + 19) // 20
        for page in range(1, count_page + 1):
            result = self.fetch("movie/top_rated", params={"page": str(page)})
            movie_ids.extend([movie["id"] for movie in result.get("results", [])])
        return movie_ids[:count_movies]


class TMDBExporter:
    def __init__(self, fetcher: TMDBFetcher, reviews_aggregator: ReviewsAggregator | None = None, output_dir: str = "tmdb_csv_exports"):
        self.fetcher = fetcher
        self.reviews_aggregator = reviews_aggregator
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self._movies_cache: dict[int, dict] = {}
        self._movie_keywords_cache: dict[int, dict] = {}
        self._movie_reviews_cache: dict[int, dict] = {}
        self._movie_credits_cache: dict[int, dict] = {}
        self._people_cache: dict[int, dict] = {}
        self._companies_cache: dict[int, dict] = {}
        self._countries_cache: list[dict] | None = None
        self._genres_cache: dict | None = None
        self._keywords_cache: dict[int, dict] = {}
        self._jobs_cache: dict[str, int] = {}
        self._next_job_id: int = 1

        # ── Progress Persistence ───────────────────────────────────────────
        self._exported_movies = self._load_existing_ids(self.output_dir / "movies.csv")
        self._exported_people = self._load_existing_ids(self.output_dir / "people.csv")
        self._exported_companies = self._load_existing_ids(self.output_dir / "companies.csv")
        
        logger.info(f"Initialized. Existing: {len(self._exported_movies)} movies, {len(self._exported_people)} people.")

    # ── Cache helpers ──────────────────────────────────────────────────

    def _get_with_cache(self, cache: dict[int, Any], key: int, fetch_method: Callable[[int], Any]) -> Any:
        if key not in cache:
            cache[key] = fetch_method(key)
        return cache[key]

    def _load_existing_ids(self, output_path: pathlib.Path) -> set[int]:
        if not output_path.exists():
            return set()
        try:
            with output_path.open("r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return {int(row["tmdb_id"]) for row in reader if row.get("tmdb_id")}
        except Exception as e:
            logger.warning(f"Failed to load IDs from {output_path.name}: {e}")
            return set()

    # ── Cached fetchers ────────────────────────────────────────────────

    def get_movie_details(self, movie_id: int) -> dict:
        return self._get_with_cache(self._movies_cache, movie_id, self.fetcher.get_movie_details)

    def get_movie_keywords(self, movie_id: int) -> dict:
        return self._get_with_cache(self._movie_keywords_cache, movie_id, self.fetcher.get_movie_keywords)

    def get_movie_reviews(self, movie_id: int) -> dict:
        return self._get_with_cache(self._movie_reviews_cache, movie_id, self.fetcher.get_movie_reviews)

    def get_movie_credits(self, movie_id: int) -> dict:
        return self._get_with_cache(self._movie_credits_cache, movie_id, self.fetcher.get_movie_credits)

    def get_person_details(self, person_id: int) -> dict:
        return self._get_with_cache(self._people_cache, person_id, self.fetcher.get_person_details)

    def get_company_details(self, company_id: int) -> dict:
        return self._get_with_cache(self._companies_cache, company_id, self.fetcher.get_company_details)

    def get_countries(self) -> list[dict]:
        if self._countries_cache is None:
            self._countries_cache = self.fetcher.get_countries()
        return self._countries_cache

    def get_genres(self) -> dict:
        if self._genres_cache is None:
            self._genres_cache = self.fetcher.get_genres()
        return self._genres_cache

    # ── Private helpers ────────────────────────────────────────────────

    def _build_image_url(self, path: str | None) -> str | None:
        return f"{self.fetcher.image_base_url}{path}" if path else None

    def _to_json_array(self, items: list) -> str:
        return json.dumps(items, ensure_ascii=False)

    def _extract_job_from_character(self, character_name: str) -> str:
        """Return job title parsed from character name, or 'Actor'
            by default."""
        if not character_name:
            return DEFAULT_CAST_JOB
        match = re.search(r"\(([^)]+)\)", character_name)
        if match:
            job = match.group(1).strip().title()
            if job in APPROVED_CAST_JOBS:
                return job
        return DEFAULT_CAST_JOB

    def _get_or_create_job_id(self, job_name: str) -> int:
        if job_name not in self._jobs_cache:
            self._jobs_cache[job_name] = self._next_job_id
            self._next_job_id += 1
        return self._jobs_cache[job_name]

    def _filter_new_ids(self, ids: set[int], exported_ids: set[int]) -> set[int]:
        new_ids = ids - exported_ids
        return new_ids

    def _export_csv(self, data: list[dict], output_path: pathlib.Path) -> None:
        if not data:
            return
        file_exists = output_path.exists()
        with output_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            if not file_exists:
                writer.writeheader()
            for row in data:
                writer.writerow(row)
                    
    # ── Public transform methods ───────────────────────────────────────

    def transform_movie_data(self, movie_id: int) -> dict:
        movie = self.get_movie_details(movie_id)
        keywords = self.get_movie_keywords(movie_id).get("keywords", [])
        credits = self.get_movie_credits(movie_id)
        reviews = self.get_movie_reviews(movie_id).get("results", [])[:10]
        reviews_sum = self.reviews_aggregator.summarize_reviews(reviews) if self.reviews_aggregator else None

        company_names = [
            self.get_company_details(c["id"])["name"]
            for c in movie.get("production_companies", [])
        ]

        return {
            "tmdb_id": movie.get("id"),
            "title": movie.get("title"),
            "adult": movie.get("adult"),
            "overview": movie.get("overview"),
            "tagline": movie.get("tagline"),
            "budget": movie.get("budget"),
            "revenue": movie.get("revenue"),
            "runtime": movie.get("runtime"),
            "release_date": self._format_date(movie.get("release_date")),
            "homepage": movie.get("homepage"),
            "poster_url": self._build_image_url(movie.get("poster_path")),
            "vote_count": movie.get("vote_count"),
            "avg_vote": movie.get("vote_average"),
            "popularity": movie.get("popularity"),
            "reviews_sum": reviews_sum,
            "collection": (movie.get("belongs_to_collection") or {}).get("name"),
            "keywords": self._to_json_array([kw["name"] for kw in keywords]),
            "companies": self._to_json_array(company_names),
            "genres": self._to_json_array([g["id"] for g in movie.get("genres", [])]),
            "crew_jobs": self._to_json_array(self._build_crew_jobs(credits.get("crew", []))),
            "cast_jobs": self._to_json_array(self._build_cast_jobs(credits.get("cast", []))),
        }

    def transform_person_data(self, person_id: int) -> dict:
        person = self._get_with_cache(self._people_cache, person_id, self.fetcher.get_person_details)
        return {
            "tmdb_id": person.get("id"),
            "name": person.get("name"),
            "birth_date": self._format_date(person.get("birthday")),
            "profile_image_url": self._build_image_url(person.get("profile_path")),
            "popularity": person.get("popularity"),
            "birth_country": person.get("place_of_birth"),
        }

    def transform_company_data(self, company_id: int) -> dict:
        company = self._get_with_cache(self._companies_cache, company_id, self.fetcher.get_company_details)
        return {
            "tmdb_id": company.get("id"),
            "name": company.get("name"),
            "country_iso": company.get("origin_country"),
        }

    def transform_country_data(self, country_iso: str) -> dict:
        country = next(
            (c for c in self.get_countries() if c["iso_3166_1"] == country_iso), None
        )
        if not country:
            return {"iso_3166_1": country_iso, "name": None}
        return {"iso_3166_1": country["iso_3166_1"], "name": country["english_name"]}

    def transform_genre_data(self, genre_id: int) -> dict:
        genres = self.get_genres()
        genre = next((g for g in genres if g["id"] == genre_id), None)
        if not genre:
            
            return {"tmdb_id": genre_id, "name": None}
        return {"tmdb_id": genre["id"], "name": genre["name"]}

    def transform_job_data(self, job_name: str) -> dict:
        return {"id": self._get_or_create_job_id(job_name), "name": job_name}
    
    # ── Public export methods ────────────────────────────────────────
    def export_movies(self, movie_id: int) -> None:
        movies_data = [self.transform_movie_data(movie_id)]
        self._export_csv(movies_data, pathlib.Path(self.output_dir) / "movies.csv")
        
    def export_people(self, movie_id: int) -> None:
        credits = self.get_movie_credits(movie_id)
        cast_ids = {member["id"] for member in credits.get("cast", [])}
        crew_ids = {member["id"] for member in credits.get("crew", [])}
        all_people_ids = cast_ids | crew_ids
        
        people_data = []
        
        for person_id in self._filter_new_ids(all_people_ids, self._exported_people):
            people_data.append(self.transform_person_data(person_id))
        self._export_csv(people_data, pathlib.Path(self.output_dir) / "people.csv")

    def export_companies(self, movie_id: int) -> None:
        company_data = []
        company_ids = {c["id"] for c in self.get_movie_details(movie_id).get("production_companies", [])}
        for company_id in self._filter_new_ids(company_ids, self._exported_companies):
                company_data.append(self.transform_company_data(company_id))
        self._export_csv(company_data, pathlib.Path(self.output_dir) / "companies.csv")        
       
     
    def export_countries(self) -> None:
        countries_data = [self.transform_country_data(c["iso_3166_1"]) for c in self.get_countries()]
        self._export_csv(countries_data, pathlib.Path(self.output_dir) / "countries.csv")
    
    def export_genres(self) -> None:
        genres_data = [self.transform_genre_data(g["id"]) for g in self.get_genres()]
        self._export_csv(genres_data, pathlib.Path(self.output_dir) / "genres.csv")
        
    def export_jobs(self) -> None:
        jobs_data = [self.transform_job_data(job_name) for job_name in self._jobs_cache.keys()]
        self._export_csv(jobs_data, pathlib.Path(self.output_dir) / "jobs.csv")
        
        