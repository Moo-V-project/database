from typing import Any, Callable

import pytest
from psycopg import Cursor

from db_importer.adapter import db, models


class SimpleInsertTestCase:
    def __init__(
        self,
        function: Callable[[Cursor, list[Any]], None],
        setup_function: Callable[[Cursor], None] | None,
        base_data: list[Any],
        duplicate_data: Any,
        insert_func: Callable[[Cursor, Any], None | Cursor],
        select_all_func: Callable[[Cursor], list[tuple[Any, ...]]],
        insert_results: list[tuple[Any, ...]],
        insert_duplicate_results: list[tuple[Any, ...]],
        insert_mixed_results: list[tuple[Any, ...]],
    ):
        self.function = function
        self.setup_function = setup_function
        self.base_data = base_data
        self.duplicate_data = duplicate_data
        self.insert_func = insert_func
        self.select_all_func = select_all_func
        self.insert_results = insert_results
        self.insert_duplicate_results = insert_duplicate_results
        self.insert_mixed_results = insert_mixed_results


def setup_countries_insert(cursor: Cursor) -> None:
    cursor.execute(
        """
        INSERT INTO country (id, name, iso_3166_1) VALUES
            (1, 'Country A', 'CA'),
            (2, 'Country B', 'CB')
        """,
    )


simple_insert_test_cases = [
    # Countries
    pytest.param(
        SimpleInsertTestCase(
            db.insert_countries,
            setup_function=None,
            base_data=[
                models.Country("Country A", "CA"),
                models.Country("Country B", "CB"),
            ],
            duplicate_data=models.Country("Country A NEW", "CA"),
            insert_func=lambda cursor, data: cursor.execute(
                "INSERT INTO country (name, iso_3166_1) VALUES (%s, %s)",
                (data.name, data.iso_3166_1),
            ),
            select_all_func=lambda cursor: cursor.execute(
                "SELECT name, iso_3166_1 FROM country"
            ).fetchall(),
            insert_results=[
                ("Country A", "CA"),
                ("Country B", "CB"),
            ],
            insert_duplicate_results=[
                ("Country A", "CA"),
            ],
            insert_mixed_results=[
                ("Country A", "CA"),
                ("Country B", "CB"),
            ],
        ),
        id="countries",
    ),
    # Genres
    pytest.param(
        SimpleInsertTestCase(
            db.insert_genres,
            setup_function=None,
            base_data=[
                models.Genre("Genre A"),
                models.Genre("Genre B"),
            ],
            duplicate_data=models.Genre("Genre A"),
            insert_func=lambda cursor, data: cursor.execute(
                "INSERT INTO genre (name) VALUES (%s)",
                (data.name,),
            ),
            select_all_func=lambda cursor: cursor.execute(
                "SELECT name FROM genre"
            ).fetchall(),
            insert_results=[
                ("Genre A",),
                ("Genre B",),
            ],
            insert_duplicate_results=[
                ("Genre A",),
            ],
            insert_mixed_results=[
                ("Genre A",),
                ("Genre B",),
            ],
        ),
        id="genres",
    ),
    # Companies
    pytest.param(
        SimpleInsertTestCase(
            db.insert_companies,
            setup_function=setup_countries_insert,
            base_data=[
                models.Company("Company A", 1),
                models.Company("Company B", 2),
            ],
            duplicate_data=models.Company("Company A", 1),
            insert_func=lambda cursor, data: cursor.execute(
                "INSERT INTO company (name, country_id) VALUES (%s, %s)",
                (data.name, data.country_id),
            ),
            select_all_func=lambda cursor: cursor.execute(
                "SELECT name, country_id FROM company"
            ).fetchall(),
            insert_results=[
                ("Company A", 1),
                ("Company B", 2),
            ],
            insert_duplicate_results=[
                ("Company A", 1),
            ],
            insert_mixed_results=[
                ("Company A", 1),
                ("Company B", 2),
            ],
        ),
        id="companies",
    ),
]
