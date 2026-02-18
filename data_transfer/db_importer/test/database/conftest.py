import subprocess
from pathlib import Path
from typing import Any, Generator

import psycopg
import pytest
from testcontainers.postgres import (  # type: ignore[import-untyped]
    PostgresContainer,
)

PG_USER = "postgres"
PG_PASSWORD = "password"
PG_DB = "moo-v"


@pytest.fixture(scope="package")
def postgres_container() -> Generator[PostgresContainer, Any, None]:
    with PostgresContainer(
        "postgres:18", username=PG_USER, password=PG_PASSWORD, dbname=PG_DB
    ) as postgres:
        yield postgres


@pytest.fixture(scope="package")
def migrated_postgres(postgres_container):
    migrations_dir = Path(__file__).parent / "migrations"

    jdbc_url = postgres_container.get_connection_url().replace(
        "postgresql+psycopg2", "jdbc:postgresql"
    )

    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "--network",
            f"container:{postgres_container._container.id}",
            "-v",
            f"{migrations_dir}:/flyway/sql",
            "flyway/flyway",
            f"-url={jdbc_url}",
            f"-user={PG_USER}",
            f"-password={PG_PASSWORD}",
            "migrate",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Flyway migration failed:\n{result.stderr}")

    return postgres_container


@pytest.fixture(scope="function")
def pg_connection(
    migrated_postgres,
) -> Generator[psycopg.Connection[tuple[Any, ...]], Any, None]:
    conn = psycopg.connect(
        host=migrated_postgres.get_container_host_ip(),
        port=migrated_postgres.get_exposed_port(5432),
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DB,
    )

    yield conn

    conn.rollback()
    conn.close()
