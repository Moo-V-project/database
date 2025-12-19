from os import path, PathLike
from typing import Any

from json import loads
from jsonschema import validate

from pandas import DataFrame, read_csv, to_datetime
from pandas._typing import Dtype
import numpy as np


class CSVSchema:
    def __init__(
        self,
        plain: dict[str, Dtype] | None = None,
        dates: list[str] | None = None,
        json: dict[str, dict[str, Any]] | None = None,
    ) -> None:
        if all(arg is None for arg in (plain, dates, json)):
            raise ValueError(
                "At least one of plain, dates, or json must be provided."
            )

        self.__plain = plain if plain is not None else {}
        self.__dates = dates if dates is not None else []
        self.__json = json if json is not None else {}

    def get_all_columns(self) -> list[str]:
        return (
            list(self.__plain.keys()) + list(self.__json.keys()) + self.__dates
        )

    def get_dtype_mapping(self) -> dict[str, Dtype]:
        return self.__plain

    def get_date_columns(self) -> list[str]:
        return self.__dates

    def get_json_schemas(self) -> dict[str, dict[str, Any]]:
        return self.__json


# the order: genres, countries, companies, people, movies
REQUIRED_FIELDS: dict[str, CSVSchema] = {
    "genres.csv": CSVSchema(
        plain={
            "tmdb_id": np.int64,
            "name": str,
        }
    ),
    "countries.csv": CSVSchema(
        plain={
            "tmdb_id": np.int64,
            "name": str,
            "iso_3166_1": str,
        }
    ),
    "companies.csv": CSVSchema(
        plain={
            "tmdb_id": np.int64,
            "name": str,
            "country_id": np.int64,
        }
    ),
    "people.csv": CSVSchema(
        plain={
            "tmdb_id": np.int64,
            "name": str,
            "profile_image_url": str,
            "popularity": np.float32,
            "birth_country_id": np.int64,
            "gender": np.int8,
        },
        dates=["birth_date"],
    ),
    "movies.csv": CSVSchema(
        plain={
            "tmdb_id": np.int64,
            "title": str,
            "adult": np.bool,
            "overview": str,
            "tagline": str,
            "budget": np.int64,
            "revenue": np.int64,
            "runtime": np.int16,
            "homepage": str,
            "poster_url": str,
            "vote_count": np.int32,
            "avg_vote": np.float32,
            "popularity": np.float32,
            "reviews_sum": np.int64,
            "collection": str,
        },
        dates=["release_date"],
        json={
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
            },
            "companies": {
                "type": "array",
                "items": {"type": "integer"},
            },
            "genres": {
                "type": "array",
                "items": {"type": "integer"},
            },
            "crew_jobs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "job": {"type": "string"},
                    },
                    "required": ["id", "job"],
                },
            },
            "cast_jobs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "job": {"type": "string"},
                        "character_name": {"type": "string"},
                    },
                    "required": ["id", "job", "character_name"],
                },
            },
        },
    ),
}


def read_all_movie_csvs(
    base_path: str | PathLike,
) -> tuple[DataFrame, DataFrame, DataFrame, DataFrame, DataFrame]:
    """
    Reads all required movie CSV files from the specified base path and returns them as DataFrames.

    Args:
        base_path (str): The base directory path where the CSV files are located.

    Returns:
        A tuple containing DataFrames for genres, countries, companies, people, and movies respectively.

    Raises:
        FileNotFoundError: If any of the required CSV files are not found in the specified base path.
        ValueError: If any of the CSV files do not conform to the expected schema
        jsonschema.ValidationError: If any JSON data in the CSV files fails schema validation.
    """
    # TODO: check all the exceptions the function can raise and document them properly
    result: list[DataFrame] = []
    for file_name, schema in REQUIRED_FIELDS.items():
        filepath = path.join(base_path, file_name)
        df = read_csv(
            filepath_or_buffer=filepath,
            usecols=schema.get_all_columns(),
            dtype=schema.get_dtype_mapping(),  # type: ignore
        )

        for date_col in schema.get_date_columns():
            df[date_col] = to_datetime(df[date_col], format="ISO8601")

        for json_col, json_schema in schema.get_json_schemas().items():
            # TODO: add proper error handling
            df[json_col] = df[json_col].apply(loads)
            df[json_col].apply(
                lambda data: validate(instance=data, schema=json_schema)
            )

        result.append(df)

    return tuple(result)  # type: ignore
