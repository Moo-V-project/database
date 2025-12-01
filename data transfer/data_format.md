# TMDB CSV Data Format Specification

This document defines CSV formats for exporting movie data from TMDB and importing into the database.
All CSV files align with the database schema structure.

---

## File Organization

### Core Entity Tables
Primary entities forming the database foundation:
- **movies.csv** — film records
- **people.csv** — actors, directors, crew members
- **companies.csv** — production companies
- **countries.csv** — geographic reference data
- **genres.csv** — film genre categories

---

## CSV Conventions

- **Encoding:** UTF-8
- **Delimiter:** comma (`,`)
- **Quotes:** `""` for fields containing delimiters
- **Empty values:** blank field
- **Date format:** `YYYY-MM-DD`
- **Boolean:** `true` / `false`

---

# Core Entity Tables

## movies.csv

Maps to `movie` table.

| Column          | Type    | Description                                      |
|-----------------|---------|--------------------------------------------------|
| tmdb_id         | INTEGER | TMDB movie ID (unique)                           |
| title           | STRING  | Film title                                       |
| adult           | BOOLEAN | Adult content flag                               |
| overview        | STRING  | Plot summary (converted to VECTOR by importer)   |
| tagline         | STRING  | Marketing tagline                                |
| budget          | INTEGER | Production budget (USD)                          |
| revenue         | INTEGER | Box office revenue (USD)                         |
| runtime         | INTEGER | Duration in minutes                              |
| release_date    | DATE    | Theatrical release date                          |
| homepage        | STRING  | Official website URL                             |
| poster_url      | STRING  | Full poster image URL                            |
| vote_count      | INTEGER | Number of user ratings                           |
| avg_vote        | FLOAT   | Average rating score                             |
| popularity      | FLOAT   | TMDB popularity metric                           |
| reviews_sum     | STRING  | Aggregated reviews (converted to VECTOR)         |
| collection_id   | INTEGER | FK to collection table                           |
| keywords        | ARRAY   | Includes keyword id(int) and keyword(str)        |
| genre_id        | INTEGER | FK to genres table                               |
| collection      | ARRAY   | collection_id(int) and name(str)                 |
| crew_jobs       | JSON    | Person id(int), job(str)                         |
| cast_jobs       | JSON    | Person id(int), job(str), character_name(str)    |



**Notes:**
- Genres, keywords, cast, and crew stored in separate linking tables
- `poster_url` = TMDB base_url + poster_path
- `overview` and `reviews_sum` are raw text; importer handles vector embedding

---

## people.csv

Maps to `person` table.

| Column             | Type    | Description                     |
|--------------------|---------|---------------------------------|
| tmdb_id            | INTEGER | TMDB person ID (unique)         |
| name               | STRING  | Full name                       |
| birth_date         | DATE    | Date of birth                   |
| profile_image_url  | STRING  | Full profile photo URL          |
| popularity         | FLOAT   | TMDB popularity metric          |
| birth_country_iso  | STRING  | ISO 3166-1 country code         |
| gender             | ARRAY   | TMDB gender code (0-3)          |
| crew_jobs          | ARRAY   | Includes crew jobs' name and id |
| cast_jobs          | ARRAY   | Includes cast jobs' name and id |

**Notes:**
- `gender_code` would be mapped to `gender_id` by importer (0=Not specified, 1=Female, 2=Male, 3=Non-binary)
- `birth_country_iso` parsed from TMDB `place_of_birth` field
- Importer resolves ISO code to `country_id` FK

---

## companies.csv

Maps to `company` table.

| Column      | Type    | Description                   |
|-------------|---------|-------------------------------|
| tmdb_id     | INTEGER | TMDB company ID (unique)      |
| name        | STRING  | Company name                  |
| country_iso | STRING  | ISO 3166-1 origin country     |

**Notes:**
- Importer resolves `country_iso` to `country_id` FK

---
## countries.csv

Maps to `country` table.

| Column     | Type    | Description            |
|------------|---------|------------------------|
| iso_3166_1 | STRING  | ISO country code (PK)  |
| name       | STRING  | Full country name      |

**Notes:**
- Reference table for companies and person birth countries
- Example: `US` → "United States of America"

---

## genres.csv

Maps to `genre` table.

| Column  | Type    | Description      |
|---------|---------|------------------|
| tmdb_id | INTEGER | TMDB genre ID    |
| name    | STRING  | Genre name       |

**Notes:**
- Fixed TMDB genre list (~20 entries)
- Examples: Action, Drama, Science Fiction

