# TODO: implement function connecting to the DB and returning a connection object
# TODO: implement functions for upserting data from each data frame,
#       the functions should take a data frame and a DB connection as arguments

# 0. Create a db connection
# 1. Upsert data into the inner-level tables (countries, etc.), saving a map tmdb_id -> db_id.
# 2. Upsert data into all the other tables from inner to outer levels, saving id maps as well.
# 3. Upsert data into the connecting tables.
# 4. Commit the transaction.
# 5. On any error rollback the transaction.


import psycopg

from .models import (
    CastCreditData,
    Collection,
    Company,
    Country,
    CrewCreditData,
    Genre,
    Job,
    Movie,
    Person,
)


def get_db_conn(
    host: str, port: int, user: str, password: str, dbname: str
) -> psycopg.Connection:
    """
    Establishes and returns a connection to the PostgreSQL database.

    Args:
        host (str): The database host address.
        port (int): The port number on which the database is listening.
        user (str): The username to connect to the database.
        password (str): The password for the database user.
        dbname (str): The name of the database to connect to.

    Returns:
        psycopg.Connection: A connection object to interact with the PostgreSQL database.
    """
    conn = psycopg.connect(
        host=host, port=port, user=user, password=password, dbname=dbname
    )
    return conn


def insert_countries(cursor: psycopg.Cursor, countries: list[Country]) -> None:
    """
    Inserts countries into the database.

    Args:
        cursor (psycopg.Cursor): The database cursor.
        countries (list[Country]): The list of Country objects to be inserted.
    """
    query = """
    INSERT INTO country (name, iso_3166_1)
    VALUES (%s, %s)
    ON CONFLICT DO NOTHING;
    """

    cursor.executemany(
        query,
        [(country.name, country.iso_3166_1) for country in countries],
    )


def get_all_country_codes(cursor: psycopg.Cursor) -> list[tuple[int, str]]:
    """
    Retrieves all country IDs and their corresponding ISO 3166-1 codes from the database.

    Args:
        cursor (psycopg.Cursor): The database cursor."""

    cursor.execute("SELECT id, iso_3166_1 FROM country ORDER BY id")
    return cursor.fetchall()


def insert_genres(cursor: psycopg.Cursor, genres: list[Genre]) -> None:
    """
    Inserts genres into the database.

    Args:
        cursor (psycopg.Cursor): The database cursor.
        genres (list[Genre]): The list of Genre objects to be inserted.
    """
    query = """
    INSERT INTO genre (name)
    VALUES (%s)
    ON CONFLICT DO NOTHING;
    """

    cursor.executemany(
        query, [(genre.name,) for genre in genres], returning=True
    )


def get_all_genres(cursor: psycopg.Cursor) -> list[tuple[int, str]]:
    """
    Retrieves all genre IDs and their corresponding names from the database.

    Args:
        cursor (psycopg.Cursor): The database cursor.
    """
    cursor.execute("SELECT id, name FROM genre ORDER BY id")
    return cursor.fetchall()


def insert_companies(cursor: psycopg.Cursor, companies: list[Company]) -> None:
    query = """
    INSERT INTO company (name, country_id)
    VALUES (%s, %s)
    ON CONFLICT DO NOTHING
    RETURNING id;
    """

    cursor.executemany(
        query, [(company.name, company.country_id) for company in companies]
    )


def insert_jobs(cursor: psycopg.Cursor, jobs: list[Job]) -> list[int]:
    raise NotImplementedError


def upsert_people(cursor: psycopg.Cursor, people: list[Person]) -> list[int]:
    raise NotImplementedError


def upsert_keywords(cursor: psycopg.Cursor, keywords: list[str]) -> list[int]:
    raise NotImplementedError


def upsert_movie(cursor: psycopg.Cursor, movie: Movie) -> int:
    raise NotImplementedError


def upsert_collection(cursor: psycopg.Cursor, collection: Collection) -> int:
    raise NotImplementedError


def upsert_cast_credits(
    cursor: psycopg.Cursor, movie_id: int, cast_credits: list[CastCreditData]
) -> list[int]:
    raise NotImplementedError


def upsert_crew_credits(
    cursor: psycopg.Cursor, movie_id: int, crew_credits: list[CrewCreditData]
) -> list[int]:
    raise NotImplementedError


def upsert_movie_genres(
    cursor: psycopg.Cursor, movie_id: int, genre_ids: list[int]
) -> None:
    raise NotImplementedError


def upsert_movie_keywords(
    cursor: psycopg.Cursor, movie_id: int, keyword_ids: list[int]
) -> None:
    raise NotImplementedError


def upsert_movie_data(
    cursor: psycopg.Cursor,
    movie: Movie,
    cast_credits: list[CastCreditData],
    crew_credits: list[CrewCreditData],
    genre_ids: list[int],
    keyword_ids: list[int],
) -> None:
    # 1. Clean up data in many-to-many tables for the movie
    # 2. Upsert the movie itself, getting the movie_id
    # 3. Upsert new many-to-many tables data
    raise NotImplementedError
