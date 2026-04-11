import pytest
from unittest.mock import MagicMock
from data_transfer.tmdb_exporter.reviews_aggregator import ReviewsAggregator
from data_transfer.tmdb_exporter.tmdb_exporter import TMDBExporter, TMDBFetcher
import json
import pathlib
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

# Fixtures for unit tests (Mocks)

@pytest.fixture
def mock_fetcher():
    fetcher = MagicMock(spec=TMDBFetcher)
    fetcher.image_base_url = "https://image.tmdb.org/t/p/original"
    return fetcher

@pytest.fixture
def mock_exporter(mock_fetcher):
    return TMDBExporter(fetcher=mock_fetcher, output_dir="/tmp/tmdb_test")
    
@pytest.fixture
def reviews_aggregator():
    mock_client = MagicMock(spec=Anthropic)
    
    mock_block = MagicMock()
    mock_block.type = "text"
    mock_block.text = "PROS:\n- Good acting: ...\nCONS:\n- Slow pacing: ...\nOVERALL:\nScore: 7/10\nAudience: ..."
    
    mock_client.messages.create.return_value.content = [mock_block]
    
    return ReviewsAggregator(client=mock_client, model="claude-haiku-4-5")

@pytest.fixture
def movie_stub():
    path = pathlib.Path(__file__).parent / "fixtures" / "movie_550.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)
    
@pytest.fixture
def credits_stub():
    path = pathlib.Path(__file__).parent / "fixtures" / "credits_550.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)
    
# Integration tests fixtures (using real API calls)

@pytest.fixture
def tmdb_fetcher():
    token = os.getenv("TMDB_BEARER_TOKEN")
    if not token:
        pytest.skip("TMDB_BEARER_TOKEN is missing")
    return TMDBFetcher(bearer_token=os.getenv("TMDB_BEARER_TOKEN"))

@pytest.fixture
def tmdb_exporter(tmdb_fetcher: TMDBFetcher):
    return TMDBExporter(fetcher=tmdb_fetcher, output_dir="test_exports")
    
