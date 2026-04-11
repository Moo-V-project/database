import pytest
from data_transfer.tmdb_exporter.tmdb_exporter import TMDBExporter
from data_transfer.tmdb_exporter.tmdb_exporter import TMDBFetcher


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
    
# test error handling
@pytest.mark.integration
@pytest.mark.parametrize("setup_data, expected_message", [
    ({"id": 0, "token": None}, "Resource not found"),
    ({"id": 550, "token": "WRONG_TOKEN"}, "Authentication failed"),
])
def test_fetch_errors(tmdb_fetcher, setup_data, expected_message):
    if setup_data.get("token"):
        fetcher = TMDBFetcher(bearer_token=setup_data.get("token"))
    else:
        fetcher = tmdb_fetcher
    
    with pytest.raises(ValueError) as excinfo:
        fetcher.get_movie_details(setup_data.get("id"))
        
    assert expected_message in str(excinfo.value)
    
