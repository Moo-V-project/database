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
- **jobs.csv** — jobs list 

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

| Column                 | Type    | Description                                                                 |
|------------------------|---------|-----------------------------------------------------------------------------|
| tmdb_id                | INTEGER | TMDB movie ID (unique)                                                      |
| title                  | STRING  | Film title                                                                  |
| adult                  | BOOLEAN | Adult content flag                                                          |
| overview               | STRING  | Plot summary                                                                |
| tagline                | STRING  | Marketing tagline                                                           |
| budget                 | INTEGER | Production budget (USD)                                                     |
| revenue                | INTEGER | Box office revenue (USD)                                                    |
| runtime                | INTEGER | Duration in minutes                                                         |
| release_date           | DATE    | Theatrical release date                                                     |
| homepage               | STRING  | Official website URL                                                        |
| poster_url             | STRING  | Full poster image URL                                                       |
| vote_count             | INTEGER | Number of user ratings                                                      |
| avg_vote               | FLOAT   | Average rating score                                                        |
| popularity             | FLOAT   | TMDB popularity metric                                                      |
| reviews_sum_vector     | STRING  | Aggregated reviews                                                          |
| collection             | STRING  | Collection name                                                             |
| keywords               | ARRAY   | Array of keywords(str)                                                      |
| companies              | ARRAY   | Array of company ids                                                        |
| genres                 | ARRAY   | Array if ids from genres csv                                                |
| crew_jobs              | ARRAY   | Array of crew member objects: { id: int, job: str }                         |
| cast_jobs              | ARRAY   | Array of cast member objects: { id: int, character_name: str, job: str }    |


**Notes:**
- `poster_url` = TMDB base_url + poster_path
- `overview` and `reviews_sum_vector` are raw text; importer handles vector embedding

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
| birth_country_iso  | STRING  | FK to countries csv             |
| gender             | INTEGER | TMDB gender code (0-3)          |

---

**Notes:**
- `gender_code` would be mapped to the `GENDER` database enum by importer (0=Not specified(NULL), 1=female, 2=male, 3=non-binary)

---

## companies.csv

Maps to `company` table.

| Column      | Type    | Description                   |
|-------------|---------|-------------------------------|
| tmdb_id     | INTEGER | TMDB company ID (unique)      |
| name        | STRING  | Company name                  |
| country_iso | STRING  | FK to countries csv           |

---
## countries.csv

Maps to `country` table.

| Column     | Type    | Description            |
|------------|---------|------------------------|
| iso_3166_1 | STRING  | ISO country code       |
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

---

## jobs.csv

Maps to `job` table.

| Column  | Type    | Description      |
|---------|---------|------------------|
| Id      | INTEGER | Job id           |
| name    | STRING  | Job name         |

**Notes:**
- Fixed jobs list (includes cast and crew)

