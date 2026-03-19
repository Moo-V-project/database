import pytest
from psycopg import Connection, Cursor
from test_cases import SimpleInsertTestCase

from db_importer.adapter import db, models


class TestSimpleInsert:
    @pytest.fixture(autouse=True)
    def setup(
        self, pg_connection: Connection, case: SimpleInsertTestCase
    ) -> None:
        with pg_connection.cursor() as cursor:
            if case.setup_function is not None:
                case.setup_function(cursor)

    def test_insert(
        self, pg_connection: Connection, case: SimpleInsertTestCase
    ) -> None:
        """
        Tests the insertion of records into the database.
        """

        with pg_connection.cursor() as cursor:
            case.function(cursor, case.base_data)

            res = case.select_all_func(cursor)
            assert res == case.insert_results

    def test_insert_duplicate(
        self, pg_connection: Connection, case: SimpleInsertTestCase
    ) -> None:
        """
        Tests an attempt of insertion of a duplicate record into the database.
        """

        with pg_connection.cursor() as cursor:
            case.insert_func(cursor, case.base_data[0])

            case.function(cursor, [case.duplicate_data])

            res = case.select_all_func(cursor)
            assert res == case.insert_duplicate_results

    def test_insert_mixed(
        self, pg_connection: Connection, case: SimpleInsertTestCase
    ) -> None:
        """
        Tests the insertion of both new and duplicate records into the database.
        """
        original_data = case.base_data[0]
        duplicate_data = case.duplicate_data
        new_data = case.base_data[1]

        with pg_connection.cursor() as cursor:
            case.insert_func(cursor, original_data)

            case.function(cursor, [duplicate_data, new_data])

            res = case.select_all_func(cursor)
            assert res == case.insert_mixed_results

    def test_insert_empty(
        self, pg_connection: Connection, case: SimpleInsertTestCase
    ) -> None:
        """
        Tests the insertion of an empty list of records into the database.
        """

        with pg_connection.cursor() as cursor:
            case.function(cursor, [])

            res = case.select_all_func(cursor)
            assert res == []

    def test_insert_all_duplicates(
        self, pg_connection: Connection, case: SimpleInsertTestCase
    ) -> None:
        """
        Tests the insertion of a list of records where all records are duplicates.
        """

        with pg_connection.cursor() as cursor:
            case.function(cursor, case.base_data)
            case.function(cursor, case.base_data)

            res = case.select_all_func(cursor)
            assert res == case.insert_results

    def insert_country(self, cursor: Cursor, name: str, iso_code: str) -> None:
        cursor.execute(
            "INSERT INTO country (name, iso_3166_1) VALUES (%s, %s)",
            params=(name, iso_code),
        )

    def get_all_countries(self, cursor: Cursor) -> list[tuple[str, str]]:
        cursor.execute("SELECT name, iso_3166_1 FROM country ORDER BY id")
        return cursor.fetchall()
