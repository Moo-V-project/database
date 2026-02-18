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


def upsert_countries(
    cursor: psycopg.Cursor, countries: list[Country]
) -> list[int]:
    """
    Upserts a country into the database.

    Args:
        cursor (psycopg.Cursor): The database cursor.
        country (Country): The Country object to be upserted.

    Returns:
        list[int]: The IDs of the upserted countries.
    """
    query = """
    INSERT INTO country (name, iso_3166_1)
    VALUES (%s, %s)
    ON CONFLICT DO NOTHING
    RETURNING id;
    """

    cursor.executemany(
        query,
        [(country.name, country.iso_3166_1) for country in countries],
        returning=True,
    )

    ids = [-1] * len(countries)

    for i, _ in enumerate(cursor.results()):
        fetched_data = cursor.fetchone()
        if fetched_data is None:
            raise psycopg.ProgrammingError("No query result to fetch")

        ids[i] = fetched_data[0]

    return ids


def upsert_genres(cursor: psycopg.Cursor, genres: list[Genre]) -> list[int]:
    """
    Upserts a genre into the database.

    Args:
        cursor (psycopg.Cursor): The database cursor.
        genres (list[Genre]): The list of Genre objects to be upserted.

    Returns:
        list[int]: The IDs of the upserted genres.
    """
    query = """
    INSERT INTO genre (name)
    VALUES (%s)
    ON CONFLICT DO NOTHING
    RETURNING id;
    """

    cursor.executemany(
        query, [(genre.name) for genre in genres], returning=True
    )

    ids = [-1] * len(genres)

    for i, _ in enumerate(cursor.results()):
        fetched_data = cursor.fetchone()
        if fetched_data is None:
            raise psycopg.ProgrammingError("No query result to fetch")

        ids[i] = fetched_data[0]

    return ids


def upsert_companies(
    cursor: psycopg.Cursor, companies: list[Company]
) -> list[int]:
    query = """
    INSERT INTO company (name, country_id)
    VALUES (%s)
    ON CONFLICT DO UPDATE SET country_id = EXCLUDED.country_id
    RETURNING id;
    """

    cursor.executemany(
        query, [(company.name, company.country_id) for company in companies]
    )

    ids = [-1] * len(companies)

    for i, _ in enumerate(cursor.results()):
        fetched_data = cursor.fetchone()
        if fetched_data is None:
            raise psycopg.ProgrammingError("No query result to fetch")

        ids[i] = fetched_data[0]

    return ids


def upsert_jobs(cursor: psycopg.Cursor, jobs: list[Job]) -> list[int]:
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
    genres: list[str],
    keywords: list[int],
) -> None:
    # 1. Clean up data in many-to-many tables for the movie
    # 2. Upsert the movie itself, getting the movie_id
    # 3. Upsert genres and keywords, getting their ids
    # 4. Upsert cast and crew, getting people ids
    # 5. Upsert new many-to-many tables data
    raise NotImplementedError
