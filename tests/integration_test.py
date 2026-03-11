import pytest 
from data_transfer.TMDB_Exporter.tmdb_exporter import TMDBExporter
from data_transfer.TMDB_Exporter.tmdb_exporter import TMDBFetcher
import os
import dotenv  


dotenv.load_dotenv()

@pytest.fixture
def tmdb_fetcher():
    return TMDBFetcher(bearer_token=os.getenv("TMDB_BEARER_TOKEN"))

@pytest.fixture
def tmdb_exporter(tmdb_fetcher: TMDBFetcher):
    return TMDBExporter(fetcher=tmdb_fetcher, output_dir="test_exports")

@pytest.mark.integration
def test_fetch_movie_details(tmdb_fetcher: TMDBFetcher):
    movie_id = 550  # Fight Club
    details = tmdb_fetcher.get_movie_details(movie_id)
    assert details["id"] == movie_id
    assert details["title"] == "Fight Club"
    
@pytest.mark.integration
def test_fetch_movie_credits(tmdb_fetcher: TMDBFetcher):
    movie_id = 550  # Fight Club
    credits = tmdb_fetcher.get_movie_credits(movie_id)
    assert credits["id"] == movie_id
    assert "cast" in credits
    assert "crew" in credits
    
@pytest.mark.integration
def test_fetch_movie_genres(tmdb_fetcher: TMDBFetcher):
    genres = tmdb_fetcher.get_genres()
    assert isinstance(genres, list)
    assert any(genre["name"] == "Action" for genre in genres)
    
@pytest.mark.integration
def test_fetch_countries(tmdb_fetcher: TMDBFetcher):
    countries = tmdb_fetcher.get_countries()
    assert isinstance(countries, list)
    assert any(country["iso_3166_1"] == "US" for country in countries)
    
