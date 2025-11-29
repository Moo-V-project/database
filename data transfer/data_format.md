# TMDB CSV Data Format Specification (Aligned with DB Schema)

This document defines CSV formats required for exporting movie-related data from TMDB before importing it into the database.
All CSV files follow the structure of the DB schema and exclude fields that are not present in the database.

It includes:

* **movies.csv**
* **people.csv**
* **companies.csv**
* **countries.csv**
* **linking tables** (genres, keywords, cast, crew)

---

# General CSV Conventions

* Encoding: **UTF-8**
* Separator: **comma (,)**
* Quotes: use `""` when needed
* Unknown values: empty field
* Dates: `YYYY-MM-DD`
* Boolean: `true` / `false`

---

# movies.csv

Maps to the `movie` table.

## Columns

1. **tmdb_id** (INT) — TMDB movie ID (unique; used for linking)
2. **title** (VARCHAR NOT NULL)
3. **adult** (BOOLEAN)
4. **overview** (TEXT) — raw text (importer will embed VECTOR)
5. **tagline** (VARCHAR)
6. **budget** (BIGINT)
7. **revenue** (BIGINT)
8. **runtime** (INT)
9. **release_date** (DATE)
10. **homepage** (VARCHAR)
11. **poster_url** (VARCHAR) — full image URL (`base_url + poster_path`)
12. **vote_count** (INT)
13. **avg_vote** (FLOAT)
14. **popularity** (FLOAT)
15. **reviews_sum** (TEXT) — raw JSON/string; importer converts to VECTOR
16. **collection_id** (INT) — FK → collection.id (TMDB `belongs_to_collection.id`)

### Notes

* No genres, keywords, cast, or crew — these will belong to linking CSVs.

---

# people.csv

Maps to the `person` table.

## Columns

1. **tmdb_id** (INT)
2. **name** (VARCHAR NOT NULL)
3. **birth_date** (DATE)
4. **profile_image_url** (VARCHAR)
5. **popularity** (FLOAT)
6. **birth_country_iso** (CHAR(2)) — ISO-3166 country code derived from TMDB `place_of_birth` (parsed)
7. **gender_code** (INT) — TMDB gender code (0–3)

### Notes

* Gender code would be converted into `gender_id` by importer.
* Birth country would be stored as ISO, importer would resolve it to `country.id`.

---

# companies.csv

Maps to the `company` table.

## Columns

1. **tmdb_id** (INT) — TMDB company ID
2. **name** (VARCHAR NOT NULL)
3. **country_iso** (CHAR(2)) — TMDB `origin_country`

### Notes

* Importer would resolve ISO → `company.country_id`.

---

# countries.csv

Maps to the `country` table.

## Columns

1. **iso_3166_1** (CHAR(2)) — primary key
2. **name** (VARCHAR NOT NULL) — human-readable country name (e.g., “United States of America”)

### Notes

* Used as reference table for companies and birth countries.
* ISO codes stored in other CSVs would be resolved against this table by the importer.

---

# Linking Tables (Many-to-Many CSV Files)

These CSVs do **not** store full objects (genres, keywords, etc.).
They store **only relationships**, matching the DB schema.

---

### movie_genres.csv

| Column   | Type | Description   |
| -------- | ---- | ------------- |
| movie_id | INT  | FK → movie.id |
| genre_id | INT  | FK → genre.id |

---

## movie_keywords.csv

| Column     | Type | Description     |
| ---------- | ---- | --------------- |
| movie_id   | INT  | FK → movie.id   |
| keyword_id | INT  | FK → keyword.id |

---

## movie_cast.csv

| Column    | Type    | Description           |
| --------- | ------- | --------------------- |
| movie_id  | INT     | FK → movie.id         |
| person_id | INT     | FK → person.id        |
| order     | INT     | TMDB “billing order”  |
| character | VARCHAR | Character name        |
| cast_id   | INT     | TMDB internal cast ID |

---

## movie_crew.csv

| Column     | Type    | Description                 |
| ---------- | ------- | --------------------------- |
| movie_id   | INT     | FK → movie.id               |
| person_id  | INT     | FK → person.id              |
| job        | VARCHAR | Example: Director, Writer   |
| department | VARCHAR | Example: Directing, Writing |
| credit_id  | VARCHAR | TMDB credit ID              |

---

# Summary: TMDB → CSV → DB Mapping

## Movies

| TMDB field                    | CSV column    | DB column           | Notes                 |
| ----------------------------- | ------------- | ------------------- | --------------------- |
| id                            | tmdb_id       | movie.tmdb_id       |                       |
| title                         | title         | movie.title         |                       |
| adult                         | adult         | movie.adult         |                       |
| overview                      | overview      | movie.overview      | will become VECTOR    |
| tagline                       | tagline       | movie.tagline       |                       |
| budget                        | budget        | movie.budget        |                       |
| revenue                       | revenue       | movie.revenue       |                       |
| runtime                       | runtime       | movie.runtime       |                       |
| release_date                  | release_date  | movie.release_date  |                       |
| homepage                      | homepage      | movie.homepage      |                       |
| poster_path                   | poster_url    | movie.poster_url    | converted to full URL |
| vote_count                    | vote_count    | movie.vote_count    |                       |
| vote_average                  | avg_vote      | movie.avg_vote      |                       |
| popularity                    | popularity    | movie.popularity    |                       |
| reviews (aggregated manually) | reviews_sum   | movie.reviews_sum   | TEXT → VECTOR         |
| belongs_to_collection.id      | collection_id | movie.collection_id | FK                    |

---

## People

| TMDB field           | CSV column        | DB column                | Notes              |
| -------------------- | ----------------- | ------------------------ | ------------------ |
| id                   | tmdb_id           | person.tmdb_id           |                    |
| name                 | name              | person.name              |                    |
| birthday             | birth_date        | person.birth_date        |                    |
| profile_path         | profile_image_url | person.profile_image_url | full URL           |
| popularity           | popularity        | person.popularity        |                    |
| gender               | gender_code       | person.gender_id         | importer maps code |
| place_of_birth → ISO | birth_country_iso | person.birth_country_id  | importer resolves  |

---

## Companies

| TMDB field     | CSV column  | DB column          | Notes              |
| -------------- | ----------- | ------------------ | ------------------ |
| id             | tmdb_id     | company.tmdb_id    |                    |
| name           | name        | company.name       |                    |
| origin_country | country_iso | company.country_id | ISO resolved to FK |

---

## Countries

| TMDB field | CSV column | DB column          | Notes          |
| ---------- | ---------- | ------------------ | -------------- |
| iso_3166_1 | iso_3166_1 | country.iso_3166_1 | PK             |
| name       | name       | country.name       | human-readable |