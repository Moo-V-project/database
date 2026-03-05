-- The Vector extensions is required for vector processing.
CREATE EXTENSION IF NOT EXISTS vector;


CREATE TYPE gender AS ENUM (
    'female',
    'male',
    'non-binary'
);


-- Reference tables

CREATE TABLE collection (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE country (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    iso_3166_1 CHAR(2) UNIQUE NOT NULL
);

CREATE TABLE genre (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE keyword (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE job (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL
);

CREATE TABLE company (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    country_id INT REFERENCES country(id)
);


-- Main tables

CREATE TABLE movie (
    id SERIAL PRIMARY KEY,
    title VARCHAR NOT NULL,
    adult BOOLEAN DEFAULT FALSE,
    overview VARCHAR,
    overview_vector VECTOR(768),
    tagline VARCHAR,
    budget BIGINT CHECK (budget > 0),
    revenue BIGINT CHECK (revenue > 0),
    runtime INT CHECK (runtime > 0),
    release_date DATE,
    homepage VARCHAR,
    poster_url VARCHAR,
    vote_count INT CHECK (vote_count >= 0),
    avg_vote FLOAT CHECK (avg_vote >= 0),
    popularity FLOAT CHECK (popularity >= 0),
    reviews_sum_vector VECTOR(768),
    tmdb_id INT UNIQUE,
    collection_id INT REFERENCES collection(id)
);

CREATE TABLE person (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    birth_date DATE,
    profile_image_url VARCHAR,
    popularity FLOAT CHECK (popularity >= 0),
    gender gender,
    birth_country_id INT REFERENCES country(id),
    UNIQUE (name, birth_date)
);


-- Movie junction tables

CREATE TABLE movie_genre (
    movie_id INT NOT NULL REFERENCES movie(id) ON DELETE CASCADE,
    genre_id INT NOT NULL REFERENCES genre(id) ON DELETE CASCADE,
    UNIQUE (movie_id, genre_id)
);

CREATE TABLE movie_keyword (
    movie_id INT NOT NULL REFERENCES movie(id) ON DELETE CASCADE,
    keyword_id INT NOT NULL REFERENCES keyword(id) ON DELETE CASCADE,
    UNIQUE (movie_id, keyword_id)
);

CREATE TABLE cast_credit (
    id SERIAL PRIMARY KEY,
    character_name VARCHAR,
    movie_id INT NOT NULL REFERENCES movie(id) ON DELETE CASCADE,
    person_id INT NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    job_id INT REFERENCES job(id),
    UNIQUE (movie_id, person_id, job_id, character_name)
);

CREATE TABLE crew_credit (
    id SERIAL PRIMARY KEY,
    movie_id INT NOT NULL REFERENCES movie(id) ON DELETE CASCADE,
    person_id INT NOT NULL REFERENCES person(id) ON DELETE CASCADE,
    job_id INT REFERENCES job(id),
    UNIQUE (movie_id, person_id, job_id)
);

CREATE TABLE movie_company (
	movie_id INT NOT NULL REFERENCES movie(id) ON DELETE CASCADE,
	company_id INT NOT NULL REFERENCES company(id) ON DELETE CASCADE,
	UNIQUE (movie_id, company_id)
);