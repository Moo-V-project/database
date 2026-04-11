import json
import pytest
from unittest.mock import MagicMock
from data_transfer.tmdb_exporter.tmdb_exporter import (
    TMDBExporter,
    TMDBFetcher,
    DEFAULT_CAST_JOB,
    APPROVED_CAST_JOBS,
)
from data_transfer.tmdb_exporter.reviews_aggregator import ReviewsAggregator

# ── _build_image_url ───────────────────────────────────────────────────────

class TestBuildImageUrl:
    def test_returns_full_url(self, mock_exporter):
        assert (
            mock_exporter._build_image_url("/abc.jpg")
            == "https://image.tmdb.org/t/p/original/abc.jpg"
        )

    def test_returns_none_for_none(self, mock_exporter):
        assert mock_exporter._build_image_url(None) is None

    def test_returns_none_for_empty_string(self, mock_exporter):
        assert mock_exporter._build_image_url("") is None

# ── _to_json_array ─────────────────────────────────────────────────────────

class TestToJsonArray:
    def test_list_of_strings(self, mock_exporter):
        result = mock_exporter._to_json_array(["a", "b"])
        assert json.loads(result) == ["a", "b"]

    def test_empty_list(self, mock_exporter):
        assert json.loads(mock_exporter._to_json_array([])) == []

    def test_list_of_dicts(self, mock_exporter):
        data = [{"id": 1, "job": "Director"}]
        assert json.loads(mock_exporter._to_json_array(data)) == data

# ── _extract_job_from_character ────────────────────────────────────────────

class TestExtractJobFromCharacter:
    def test_default_for_plain_name(self, mock_exporter):
        assert mock_exporter._extract_job_from_character("John Doe") == DEFAULT_CAST_JOB

    def test_empty_string_returns_default(self, mock_exporter):
        assert mock_exporter._extract_job_from_character("") == DEFAULT_CAST_JOB

    def test_voice_extracted(self, mock_exporter):
        assert mock_exporter._extract_job_from_character("Simba (Voice)") == "Voice"

    def test_narrator_extracted(self, mock_exporter):
        assert (
            mock_exporter._extract_job_from_character("Narrator (Narrator)")
            == "Narrator"
        )

    def test_unapproved_job_returns_default(self, mock_exporter):
        assert (
            mock_exporter._extract_job_from_character("Bob (Stuntman)")
            == DEFAULT_CAST_JOB
        )

    def test_case_insensitive_match(self, mock_exporter):
        assert mock_exporter._extract_job_from_character("Ghost (voice)") == "Voice"

    def test_no_parentheses_returns_default(self, mock_exporter):
        assert mock_exporter._extract_job_from_character("Batman") == DEFAULT_CAST_JOB

# ── _get_or_create_job_id ──────────────────────────────────────────────────

class TestGetOrCreateJobId:
    def test_first_job_gets_id_1(self, mock_exporter):
        assert mock_exporter._get_or_create_job_id("Director") == 1

    def test_same_job_same_id(self, mock_exporter):
        id1 = mock_exporter._get_or_create_job_id("Director")
        id2 = mock_exporter._get_or_create_job_id("Director")
        assert id1 == id2

    def test_different_jobs_get_different_ids(self, mock_exporter):
        id1 = mock_exporter._get_or_create_job_id("Director")
        id2 = mock_exporter._get_or_create_job_id("Writer")
        assert id1 != id2

    def test_ids_are_sequential(self, mock_exporter):
        ids = [mock_exporter._get_or_create_job_id(name) for name in ["A", "B", "C"]]
        assert ids == [1, 2, 3]

# ── Caching behavior ──────────────────────────────────────────────────────

class TestCaching:
    def test_movie_details_fetched_once(self, mock_exporter, mock_fetcher):
        mock_fetcher.get_movie_details.return_value = {"id": 1, "title": "Test"}
        mock_exporter.get_movie_details(1)
        mock_exporter.get_movie_details(1)
        mock_fetcher.get_movie_details.assert_called_once_with(1)

    def test_person_details_fetched_once(self, mock_exporter, mock_fetcher):
        mock_fetcher.get_person_details.return_value = {"id": 42, "name": "Actor"}
        mock_exporter.get_person_details(42)
        mock_exporter.get_person_details(42)
        mock_fetcher.get_person_details.assert_called_once_with(42)

    def test_countries_fetched_once(self, mock_exporter, mock_fetcher):
        mock_fetcher.get_countries.return_value = []
        mock_exporter.get_countries()
        mock_exporter.get_countries()
        mock_fetcher.get_countries.assert_called_once()

    def test_genres_fetched_once(self, mock_exporter, mock_fetcher):
        mock_fetcher.get_genres.return_value = []
        mock_exporter.get_genres()
        mock_exporter.get_genres()
        mock_fetcher.get_genres.assert_called_once()

# ── transform_movie_data ──────────────────────────────────────────────────

class TestTransformMovieData:
    @pytest.fixture(autouse=True)
    def setup(self, movie_stub, credits_stub):
        self.fetcher = MagicMock(spec=TMDBFetcher)
        self.fetcher.image_base_url = "https://image.tmdb.org/t/p/original"
        self.fetcher.get_movie_details.return_value = movie_stub
        self.fetcher.get_movie_keywords.return_value = {
            "keywords": [{"name": "survival"}]
        }
        self.fetcher.get_movie_credits.return_value = credits_stub
        self.fetcher.get_company_details.return_value = {"name": "Fox"}
        self.mock_reviews_aggregator = MagicMock(spec=ReviewsAggregator)
        self.mock_reviews_aggregator.summarize_reviews.return_value = "PROS:\n- Good acting: ...\nCONS:\n- Slow pacing: ...\nOVERALL:\nScore: 7/10\nAudience: ..."
        self.mock_exporter = TMDBExporter(
            self.fetcher, self.mock_reviews_aggregator, output_dir="/tmp/tmdb_test"
        )

    def test_basic_fields(self):
        result = self.mock_exporter.transform_movie_data(550)
        assert result["tmdb_id"] == 550
        assert result["title"] == "Fight Club"
        assert result["collection"] is None
        assert self.mock_exporter.transform_movie_data(550)["budget"] == 63000000
        assert self.mock_exporter.transform_movie_data(550)["revenue"] == 100853753
        assert self.mock_exporter.transform_movie_data(550)["runtime"] == 139
        assert self.mock_exporter.transform_movie_data(550)["vote_count"] == 31657
        assert self.mock_exporter.transform_movie_data(550)["avg_vote"] == 8.438
        assert (
            self.mock_exporter.transform_movie_data(550)["release_date"] == "1999-10-15"
        )
        assert (
            self.mock_exporter.transform_movie_data(550)["homepage"]
            == "http://www.foxmovies.com/movies/fight-club"
        )
        assert (
            self.mock_exporter.transform_movie_data(550)["tagline"]
            == "Mischief. Mayhem. Soap."
        )

    def test_zero_values_handling(self):
        stub_with_zero = {
            "id": 550,
            "title": "Fight Club",
            "budget": 0,
            "revenue": 0,
            "runtime": 0,
            "vote_count": 0,
            "vote_average": 0,
        }
        self.fetcher.get_movie_details.return_value = stub_with_zero
        result = self.mock_exporter.transform_movie_data(550)
        assert result["budget"] is None
        assert result["revenue"] is None
        assert result["runtime"] is None
        assert result["vote_count"] == 0
        assert result["avg_vote"] == 0
        assert result["release_date"] is None
        assert result["homepage"] is None
        assert result["tagline"] is None

    def test_poster_url_built(self):
        result = self.mock_exporter.transform_movie_data(550)
        assert (
            result["poster_url"]
            == "https://image.tmdb.org/t/p/original/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg"
        )

    def test_keywords_serialized(self):
        result = self.mock_exporter.transform_movie_data(550)
        assert json.loads(result["keywords"]) == ["survival"]

    def test_cast_job_default_actor(self):
        result = self.mock_exporter.transform_movie_data(550)
        cast = json.loads(result["cast_jobs"])
        assert cast[0]["job"] == "Actor"

    def test_crew_job(self):
        result = self.mock_exporter.transform_movie_data(550)
        crew = json.loads(result["crew_jobs"])
        assert crew[0]["job"] == "Sound Editor"

    def test_production_companies(self):
        result = self.mock_exporter.transform_movie_data(550)
        expected_companies = [
            "Fox 2000 Pictures",
            "Regency Enterprises",
            "Linson Entertainment",
            "20th Century Fox",
            "Taurus Film",
        ]
        assert json.loads(result["companies"]) == expected_companies

        stub_with_missing_company_name = {
            "id": 555,
            "title": "Gay Club",
            "production_companies": [{"id": 1}, {"id": 2, "name": "Company Name"}],
        }
        self.fetcher.get_movie_details.return_value = stub_with_missing_company_name
        result = self.mock_exporter.transform_movie_data(555)
        companies = json.loads(result["companies"])
        assert companies == ["Company Name"]
        assert len(companies) == 1

    def test_genres(self):
        self.fetcher.get_genres.return_value = [
            {"id": 18, "name": "Drama"},
            {"id": 53, "name": "Thriller"},
        ]
        assert json.loads(self.mock_exporter.transform_movie_data(550)["genres"]) == [
            18,
            53,
        ]

        stub_with_missing_genre_id = {
            "id": 555,
            "title": "Gay Club",
            "genres": [{"name": "Drama"}, {"id": 53, "name": "Thriller"}],
        }
        self.fetcher.get_movie_details.return_value = stub_with_missing_genre_id
        result = self.mock_exporter.transform_movie_data(555)
        assert json.loads(result["genres"]) == [53]
        assert len(json.loads(result["genres"])) == 1

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
    def test_export_csv(self, mock_exporter, tmp_path):
        data = [{"id": 1, "name": "Test"}, {"id": 2, "name": "Another"}]
        output_file = tmp_path / "test.csv"
        mock_exporter._export_csv(data, output_file)
        assert output_file.exists()
        with output_file.open() as f:
            lines = f.read().splitlines()
            assert lines[0] == "id,name"
            assert lines[1] == "1,Test"
            assert lines[2] == "2,Another"
