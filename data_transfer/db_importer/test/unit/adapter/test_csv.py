import pytest
from jsonschema import ValidationError


from db_importer.adapter.csv import read_all_movie_csvs


def test_read_csvs_valid(csv_dir_valid):
    dfs = read_all_movie_csvs(csv_dir_valid)
    assert len(dfs) == 5


def test_read_csvs_missing_file(csv_dir_missing_file):
    with pytest.raises(FileNotFoundError):
        read_all_movie_csvs(csv_dir_missing_file)


def test_read_csvs_invalid(csv_dir_invalid):
    with pytest.raises((ValueError, ValidationError)):
        read_all_movie_csvs(csv_dir_invalid)
