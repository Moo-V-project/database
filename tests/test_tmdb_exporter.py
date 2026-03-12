import json
import pytest
from unittest.mock import MagicMock
from data_transfer.TMDB_Exporter.tmdb_exporter import (
    TMDBExporter,
    TMDBFetcher,
    DEFAULT_CAST_JOB,
    APPROVED_CAST_JOBS,
)
from anthropic import Anthropic
from data_transfer.TMDB_Exporter.reviews_aggregator import ReviewsAggregator


# ── Fixtures ──────────────────────────────────────────────────────────────

@pytest.fixture
def mock_fetcher():
    fetcher = MagicMock(spec=TMDBFetcher)
    fetcher.image_base_url = "https://image.tmdb.org/t/p/original"
    return fetcher

@pytest.fixture
def exporter(mock_fetcher):
    return TMDBExporter(fetcher=mock_fetcher, output_dir="/tmp/tmdb_test")

@pytest.fixture
def reviews_aggregator():
    mock_client = MagicMock(spec=Anthropic)
    
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = "PROS:\n- Good acting: ...\nCONS:\n- Slow pacing: ...\nOVERALL:\nScore: 7/10\nAudience: ..."
    
    mock_client.messages.create.return_value.content = [mock_block]
    
    return ReviewsAggregator(client=mock_client, model="claude-haiku-4-5")


# ── _build_image_url ───────────────────────────────────────────────────────

class TestBuildImageUrl:
    def test_returns_full_url(self, exporter):
        assert exporter._build_image_url("/abc.jpg") == "https://image.tmdb.org/t/p/original/abc.jpg"

    def test_returns_none_for_none(self, exporter):
        assert exporter._build_image_url(None) is None

    def test_returns_none_for_empty_string(self, exporter):
        assert exporter._build_image_url("") is None


# ── _format_date ───────────────────────────────────────────────────────────

class TestFormatDate:
    def test_returns_date_string(self, exporter):
        assert exporter._format_date("2023-01-15") == "2023-01-15"

    def test_returns_none_for_none(self, exporter):
        assert exporter._format_date(None) is None

    def test_returns_none_for_empty_string(self, exporter):
        assert exporter._format_date("") is None


# ── _to_json_array ─────────────────────────────────────────────────────────

class TestToJsonArray:
    def test_list_of_strings(self, exporter):
        result = exporter._to_json_array(["a", "b"])
        assert json.loads(result) == ["a", "b"]

    def test_empty_list(self, exporter):
        assert json.loads(exporter._to_json_array([])) == []

    def test_cyrillic_preserved(self, exporter):
        result = exporter._to_json_array(["Привет"])
        assert "Привет" in result

    def test_list_of_dicts(self, exporter):
        data = [{"id": 1, "job": "Director"}]
        assert json.loads(exporter._to_json_array(data)) == data


# ── _extract_job_from_character ────────────────────────────────────────────

class TestExtractJobFromCharacter:
    def test_default_for_plain_name(self, exporter):
        assert exporter._extract_job_from_character("John Doe") == DEFAULT_CAST_JOB

    def test_empty_string_returns_default(self, exporter):
        assert exporter._extract_job_from_character("") == DEFAULT_CAST_JOB

    def test_voice_extracted(self, exporter):
        assert exporter._extract_job_from_character("Simba (Voice)") == "Voice"

    def test_narrator_extracted(self, exporter):
        assert exporter._extract_job_from_character("Narrator (Narrator)") == "Narrator"

    def test_unapproved_job_returns_default(self, exporter):
        assert exporter._extract_job_from_character("Bob (Stuntman)") == DEFAULT_CAST_JOB

    def test_case_insensitive_match(self, exporter):
        assert exporter._extract_job_from_character("Ghost (voice)") == "Voice"

    def test_no_parentheses_returns_default(self, exporter):
        assert exporter._extract_job_from_character("Batman") == DEFAULT_CAST_JOB


# ── _get_or_create_job_id ──────────────────────────────────────────────────

class TestGetOrCreateJobId:
    def test_first_job_gets_id_1(self, exporter):
        assert exporter._get_or_create_job_id("Director") == 1

    def test_same_job_same_id(self, exporter):
        id1 = exporter._get_or_create_job_id("Director")
        id2 = exporter._get_or_create_job_id("Director")
        assert id1 == id2

    def test_different_jobs_get_different_ids(self, exporter):
        id1 = exporter._get_or_create_job_id("Director")
        id2 = exporter._get_or_create_job_id("Writer")
        assert id1 != id2

    def test_ids_are_sequential(self, exporter):
        ids = [exporter._get_or_create_job_id(name) for name in ["A", "B", "C"]]
        assert ids == [1, 2, 3]


# ── Caching behavior ──────────────────────────────────────────────────────

class TestCaching:
    def test_movie_details_fetched_once(self, exporter, mock_fetcher):
        mock_fetcher.get_movie_details.return_value = {"id": 1, "title": "Test"}
        exporter.get_movie_details(1)
        exporter.get_movie_details(1)
        mock_fetcher.get_movie_details.assert_called_once_with(1)

    def test_person_details_fetched_once(self, exporter, mock_fetcher):
        mock_fetcher.get_person_details.return_value = {"id": 42, "name": "Actor"}
        exporter.get_person_details(42)
        exporter.get_person_details(42)
        mock_fetcher.get_person_details.assert_called_once_with(42)

    def test_countries_fetched_once(self, exporter, mock_fetcher):
        mock_fetcher.get_countries.return_value = []
        exporter.get_countries()
        exporter.get_countries()
        mock_fetcher.get_countries.assert_called_once()

    def test_genres_fetched_once(self, exporter, mock_fetcher):
        mock_fetcher.get_genres.return_value = []
        exporter.get_genres()
        exporter.get_genres()
        mock_fetcher.get_genres.assert_called_once()


# ── transform_country_data ─────────────────────────────────────────────────

class TestTransformCountryData:
    def test_known_country(self, exporter, mock_fetcher):
        mock_fetcher.get_countries.return_value = [
            {"iso_3166_1": "US", "english_name": "United States"}
        ]
        result = exporter.transform_country_data("US")
        assert result == {"iso_3166_1": "US", "name": "United States"}

    def test_unknown_country_returns_none_name(self, exporter, mock_fetcher):
        mock_fetcher.get_countries.return_value = []
        result = exporter.transform_country_data("XX")
        assert result == {"iso_3166_1": "XX", "name": None}


# ── transform_genre_data ───────────────────────────────────────────────────

class TestTransformGenreData:
    def test_known_genre(self, exporter, mock_fetcher):
        mock_fetcher.get_genres.return_value = [{"id": 28, "name": "Action"}]
        assert exporter.transform_genre_data(28) == {"tmdb_id": 28, "name": "Action"}

    def test_unknown_genre(self, exporter, mock_fetcher):
        mock_fetcher.get_genres.return_value = []
        assert exporter.transform_genre_data(999) == {"tmdb_id": 999, "name": None}


# ── transform_movie_data ───────────────────────────────────────────────────

MOVIE_STUB = {
    "id": 550,
    "title": "Fight Club",
    "adult": False,
    "overview": "...",
    "tagline": "Mischief. Mayhem. Soap.",
    "budget": 63000000,
    "revenue": 100853753,
    "runtime": 139,
    "release_date": "1999-10-15",
    "homepage": "",
    "poster_path": "/poster.jpg",
    "vote_count": 26280,
    "vote_average": 8.4,
    "popularity": 61.4,
    "belongs_to_collection": None,
    "production_companies": [{"id": 10}],
    "genres": [{"id": 18}],
}

CREDITS_STUB = {
    "cast": [{"id": 1, "character": "The Narrator"}],
    "crew": [{"id": 2, "job": "Director"}],
}

class TestTransformMovieData:
    def setup_method(self):
        self.fetcher = MagicMock(spec=TMDBFetcher)
        self.fetcher.image_base_url = "https://image.tmdb.org/t/p/original"
        self.fetcher.get_movie_details.return_value = MOVIE_STUB
        self.fetcher.get_movie_keywords.return_value = {"keywords": [{"name": "survival"}]}
        self.fetcher.get_movie_credits.return_value = CREDITS_STUB
        self.fetcher.get_company_details.return_value = {"name": "Fox"}
        self.mock_reviews_aggregator = MagicMock(spec=ReviewsAggregator)
        self.mock_reviews_aggregator.summarize_reviews.return_value = "PROS:\n- Good acting: ...\nCONS:\n- Slow pacing: ...\nOVERALL:\nScore: 7/10\nAudience: ..."
        self.exporter = TMDBExporter(self.fetcher, self.mock_reviews_aggregator, output_dir="/tmp/tmdb_test")

    def test_basic_fields(self):
        result = self.exporter.transform_movie_data(550)
        assert result["tmdb_id"] == 550
        assert result["title"] == "Fight Club"
        assert result["collection"] is None

    def test_poster_url_built(self):
        result = self.exporter.transform_movie_data(550)
        assert result["poster_url"] == "https://image.tmdb.org/t/p/original/poster.jpg"

    def test_keywords_serialized(self):
        result = self.exporter.transform_movie_data(550)
        assert json.loads(result["keywords"]) == ["survival"]

    def test_cast_job_default_actor(self):
        result = self.exporter.transform_movie_data(550)
        cast = json.loads(result["cast_jobs"])
        assert cast[0]["job"] == "Actor"

    def test_crew_job(self):
        result = self.exporter.transform_movie_data(550)
        crew = json.loads(result["crew_jobs"])
        assert crew[0]["job"] == "Director"

    def test_company_names_fetched(self):
        result = self.exporter.transform_movie_data(550)
        assert json.loads(result["companies"]) == ["Fox"]
        
# ── ReviewsAggregator ───────────────────────────────────────────────
class TestReviewsAggregator:
    def test_aggregate_reviews(self, reviews_aggregator):
        reviews = [
            {"author": "Alice", "content": "Great movie! Loved the acting."},
            {"author": "Bob", "content": "Not my cup of tea. Too slow."},
        ]
        summary = reviews_aggregator.summarize_reviews(reviews)
        assert "PROS:" in summary
        assert "CONS:" in summary
        assert "OVERALL:" in summary
        
# ── _export_csv ───────────────────────────────────────────────────────
class TestExportCsv:
    def test_export_csv(self, exporter, tmp_path):
        data = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Another"}]
        output_file = tmp_path / "test.csv"
        exporter._export_csv(data, output_file)
        assert output_file.exists()
        with output_file.open() as f:
            lines = f.read().splitlines()
            assert lines[0] == "id,name"
            assert lines[1] == "1,Test"
            assert lines[2] == "2,Another"