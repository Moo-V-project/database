# TMDB CSV Data Format Specification (Aligned with DB Schema)

This document defines **four CSV formats** (movies, people, countries, companies) aligned to the database schema. All unnecessary TMDB fields have been removed.


* **movie**: title, adult, overview, tagline, budget, revenue, runtime, release_date, homepage, poster_url, vote_count, avg_vote, popularity, reviews_sum, tmdb_id, collection_id
* **person**: name, birth_date, profile_image_url, popularity, birth_country_id, gender_id
* **company**: name, country_id
* **country**: name, iso_3166_1

---

# General CSV conventions

* Encoding: **UTF‑8**
* Separator: **comma (,)**
* Quotes: **""** when needed
* Unknown values: empty field
* Dates: `YYYY-MM-DD`
* Boolean: `true` / `false`
* Numeric: raw numbers

---

# movie.csv

Match the `movie` table.

### Columns

1. **tmdb_id** (INT) — TMDB movie ID (unique; used for linking)
2. **title** (VARCHAR NOT NULL)
3. **adult** (BOOLEAN, default false)
4. **overview** (TEXT) — stored as the DB's `VECTOR` column but provided here as raw text
5. **tagline** (VARCHAR)
6. **budget** (BIGINT) — TMDB budget
7. **revenue** (BIGINT)
8. **runtime** (INT)
9. **release_date** (DATE)
10. **homepage** (VARCHAR)
11. **poster_url** (VARCHAR) — full TMDB image URL
12. **vote_count** (INT)
13. **avg_vote** (FLOAT) — vote_average
14. **popularity** (FLOAT)
15. **reviews_sum** (TEXT) — exported as JSON or simple string; importer will embed into VECTOR
16. **collection_id** (INT) — TMDB `belongs_to_collection.id` (maps to `collection` table)

### Notes

* No genre, keyword, cast, crew columns here — they belong to linking tables. 

---

# people.csv

Maps to the `person` table.

### Columns

1. **tmdb_id** (INT) — TMDB person ID
2. **name** (VARCHAR NOT NULL)
3. **birth_date** (DATE) — from TMDB `birthday`
4. **profile_image_url** (VARCHAR)
5. **popularity** (FLOAT)
6. **birth_country_iso** (CHAR(2)) — Used to join to `country.iso_3166_1` (importer will resolve `birth_country_id`)
7. **gender_code** (INT) — TMDB gender codes (0,1,2,3). Importer maps to `gender_id` table.

### Notes

* No `also_known_as`, biography, death date, departments — removed per DB schema.
* Gender mapping will happen at import time.
* Country will be stored as ISO code here; importer will resolve the country table.

---

# companies.csv

Maps to the `company` table.

### Columns

1. **tmdb_id** (INT) — TMDB company ID
2. **name** (VARCHAR NOT NULL)
3. **country_iso** (CHAR(2)) — TMDB `origin_country`

### Notes

* DB schema uses `company.country_id`; importer will ISO to map to `country.id`.
* No logos, no extra metadata — removed.

---

# countries.csv

Maps to the `country` table.

### Columns

1. **iso_3166_1** (CHAR(2)) — primary key for mapping
2. **name** (VARCHAR NOT NULL)

---

# Tables Summary: TMDB → CSV → DB Mapping

### Movies 

| TMDB source field              | CSV column    | DB column           | Notes                             |
| ------------------------------ | ------------- | ------------------- | --------------------------------- |
| movie.id                       | tmdb_id       | movie.tmdb_id       | TMDB movie ID                     |
| movie.title                    | title         | movie.title         |                                   |
| movie.adult                    | adult         | movie.adult         | boolean                           |
| movie.overview                 | overview      | movie.overview      |                                   |
| movie.tagline                  | tagline       | movie.tagline       |                                   |
| movie.budget                   | budget        | movie.budget        |                                   |
| movie.revenue                  | revenue       | movie.revenue       |                                   |
| movie.runtime                  | runtime       | movie.runtime       | minutes                           |
| movie.release_date             | release_date  | movie.release_date  | YYYY-MM-DD                        |
| movie.homepage                 | homepage      | movie.homepage      | official movie url                |
| movie.poster_path              | poster_url    | movie.poster_url    | full URL = base_url + poster_path |
| movie.vote_count               | vote_count    | movie.vote_count    |                                   |
| movie.vote_average             | avg_vote      | movie.avg_vote      | float                             |
| movie.popularity               | popularity    | movie.popularity    | float                             |
| movie.belongs_to_collection.id | collection_id | movie.collection_id | FK → collection.id                |

### People 

| TMDB source field                   | CSV column        | DB column                | Notes                                      |
| ----------------------------------- | ----------------- | ------------------------ | ------------------------------------------ |
| person.id                           | tmdb_id           | person.tmdb_id           |                                            |
| person.name                         | name              | person.name              |                                            |
| person.birthday                     | birth_date        | person.birth_date        | YYYY-MM-DD                                 |
| person.profile_path                 | profile_image_url | person.profile_image_url | full URL                                   |
| person.popularity                   | popularity        | person.popularity        |                                            |
| person.gender                       | gender_code       | person.gender_id         | importer maps TMDB gender code → gender.id |
| person.place_of_birth (country ISO) | birth_country_iso | person.birth_country_id  | importer resolves ISO → country.id         |

### Companies

| TMDB source field            | CSV column  | DB column          | Notes                              |
| ---------------------------- | ----------- | ------------------ | ---------------------------------- |
| company.id                   | tmdb_id     | company.tmdb_id    |                                    |
| company.name                 | name        | company.name       |                                    |
| company.origin_country (ISO) | country_iso | company.country_id | importer resolves ISO → country.id |

### Countries

| TMDB source field                 | CSV column | DB column          | Notes                       |
| --------------------------------- | ---------- | ------------------ | --------------------------- |
| production_countries[].iso_3166_1 | iso_3166_1 | country.iso_3166_1 | primary key                 |
| production_countries[].name       | name       | country.name       | human-readable country name |
