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

### Supporting Tables
Static reference data for classification and normalization:
- **jobs.csv** — job titles and departments
- **genres.csv** — film genre categories
- **keywords.csv** — film tags and keywords
- **genders.csv** — gender classification
- **collections.csv** — film franchise/series groupings

### Linking Tables
Many-to-many relationships between entities:
- **movie_genres.csv** — movies ↔ genres
- **movie_keywords.csv** — movies ↔ keywords
- **cast_credit.csv** — movies ↔ people (acting roles)
- **crew_credit.csv** — movies ↔ people (production roles)

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
| tmdb_id         | INT     | TMDB movie ID (unique)                           |
| title           | VARCHAR | Film title                                       |
| adult           | BOOLEAN | Adult content flag                               |
| overview        | TEXT    | Plot summary (converted to VECTOR by importer)   |
| tagline         | VARCHAR | Marketing tagline                                |
| budget          | BIGINT  | Production budget (USD)                          |
| revenue         | BIGINT  | Box office revenue (USD)                         |
| runtime         | INT     | Duration in minutes                              |
| release_date    | DATE    | Theatrical release date                          |
| homepage        | VARCHAR | Official website URL                             |
| poster_url      | VARCHAR | Full poster image URL                            |
| vote_count      | INT     | Number of user ratings                           |
| avg_vote        | FLOAT   | Average rating score                             |
| popularity      | FLOAT   | TMDB popularity metric                           |
| reviews_sum     | TEXT    | Aggregated reviews (converted to VECTOR)         |
| collection_id   | INT     | FK to collection table                           |

**Notes:**
- Genres, keywords, cast, and crew stored in separate linking tables
- `poster_url` = TMDB base_url + poster_path
- `overview` and `reviews_sum` are raw text; importer handles vector embedding

---

## people.csv

Maps to `person` table.

| Column             | Type    | Description                    |
|--------------------|---------|--------------------------------|
| tmdb_id            | INT     | TMDB person ID (unique)        |
| name               | VARCHAR | Full name                      |
| birth_date         | DATE    | Date of birth                  |
| profile_image_url  | VARCHAR | Full profile photo URL         |
| popularity         | FLOAT   | TMDB popularity metric         |
| birth_country_iso  | CHAR(2) | ISO 3166-1 country code        |
| gender_code        | INT     | TMDB gender code (0-3)         |

**Notes:**
- `gender_code` mapped to `gender_id` by importer (0=Not specified, 1=Female, 2=Male, 3=Non-binary)
- `birth_country_iso` parsed from TMDB `place_of_birth` field
- Importer resolves ISO code to `country_id` FK

---

## companies.csv

Maps to `company` table.

| Column      | Type    | Description                   |
|-------------|---------|-------------------------------|
| tmdb_id     | INT     | TMDB company ID (unique)      |
| name        | VARCHAR | Company name                  |
| country_iso | CHAR(2) | ISO 3166-1 origin country     |

**Notes:**
- Importer resolves `country_iso` to `country_id` FK

---

## countries.csv

Maps to `country` table.

| Column     | Type    | Description            |
|------------|---------|------------------------|
| iso_3166_1 | CHAR(2) | ISO country code (PK)  |
| name       | VARCHAR | Full country name      |

**Notes:**
- Reference table for companies and person birth countries
- Example: `US` → "United States of America"

---

# Supporting Tables

## jobs.csv

Maps to `job` table.

| Column     | Type    | Description            |
|------------|---------|------------------------|
| id         | INT     | Unique job identifier  |
| name       | VARCHAR | Job title              |
| department | VARCHAR | Department category    |

**Notes:**
- Pre-populated reference table
- Extracted from TMDB crew `job` and `department` fields
- Common examples: Director (Directing), Producer (Production), Actor (Acting)
- Must exist before importing cast/crew data

---

## genres.csv

Maps to `genre` table.

| Column  | Type    | Description      |
|---------|---------|------------------|
| tmdb_id | INT     | TMDB genre ID    |
| name    | VARCHAR | Genre name       |

**Notes:**
- Fixed TMDB genre list (~20 entries)
- Examples: Action, Drama, Science Fiction

---

## keywords.csv

Maps to `keyword` table.

| Column  | Type    | Description        |
|---------|---------|--------------------|
| tmdb_id | INT     | TMDB keyword ID    |
| name    | VARCHAR | Keyword text       |

**Notes:**
- User-generated tags from TMDB
- Large dataset (thousands of entries)

---

## genders.csv

Maps to `gender` table.

| Column | Type    | Description   |
|--------|---------|---------------|
| id     | INT     | Gender ID     |
| name   | VARCHAR | Gender label  |

**Notes:**
- Fixed reference: 0=Not specified, 1=Female, 2=Male, 3=Non-binary
- Maps TMDB numeric codes to readable labels

---

## collections.csv

Maps to `collection` table.

| Column     | Type    | Description                   |
|------------|---------|-------------------------------|
| tmdb_id    | INT     | TMDB collection ID            |
| name       | VARCHAR | Collection name               |
| poster_url | VARCHAR | Collection poster image URL   |

**Notes:**
- Groups related films (franchises, series)
- Examples: "Marvel Cinematic Universe", "Harry Potter Collection"
- Extracted from TMDB `belongs_to_collection` object

---

# Linking Tables

## movie_genres.csv

| Column   | Type | Description       |
|----------|------|-------------------|
| movie_id | INT  | FK to movie       |
| genre_id | INT  | FK to genre       |

---

## movie_keywords.csv

| Column     | Type | Description       |
|------------|------|-------------------|
| movie_id   | INT  | FK to movie       |
| keyword_id | INT  | FK to keyword     |

---

## cast_credit.csv

Maps to `cast_credit` table. Represents acting roles.

| Column    | Type    | Description                          |
|-----------|---------|--------------------------------------|
| cast_id   | INT     | TMDB internal cast ID                |
| character | VARCHAR | Character name portrayed             |
| movie_id  | INT     | FK to movie                          |
| person_id | INT     | FK to person                         |
| job_id    | INT     | FK to job (always "Actor")           |
| order     | INT     | Billing order (lower = higher)       |

**Notes:**
- `job_id` always references "Actor" job
- Importer resolves job name to ID

---

## crew_credit.csv

Maps to `crew_credit` table. Represents production roles.

| Column    | Type    | Description                   |
|-----------|---------|-------------------------------|
| credit_id | VARCHAR | TMDB credit ID                |
| movie_id  | INT     | FK to movie                   |
| person_id | INT     | FK to person                  |
| job_id    | INT     | FK to job                     |

**Notes:**
- `job_id` references various production roles (Director, Producer, Writer, etc.)
- Department stored in `job` table, not duplicated here
- Importer maps TMDB job names to job IDs

---

# TMDB → CSV → Database Mapping

## Movies

| TMDB API Field                | CSV Column    | Database Column  | Transformation    |
|-------------------------------|---------------|------------------|-------------------|
| id                            | tmdb_id       | tmdb_id          | Direct            |
| title                         | title         | title            | Direct            |
| adult                         | adult         | adult            | Direct            |
| overview                      | overview      | overview         | Text → VECTOR     |
| tagline                       | tagline       | tagline          | Direct            |
| budget                        | budget        | budget           | Direct            |
| revenue                       | revenue       | revenue          | Direct            |
| runtime                       | runtime       | runtime          | Direct            |
| release_date                  | release_date  | release_date     | Direct            |
| homepage                      | homepage      | homepage         | Direct            |
| poster_path                   | poster_url    | poster_url       | Path → Full URL   |
| vote_count                    | vote_count    | vote_count       | Direct            |
| vote_average                  | avg_vote      | avg_vote         | Direct            |
| popularity                    | popularity    | popularity       | Direct            |
| reviews (manual aggregation)  | reviews_sum   | reviews_sum      | Text → VECTOR     |
| belongs_to_collection.id      | collection_id | collection_id    | Extract ID        |

---

## People

| TMDB API Field  | CSV Column        | Database Column   | Transformation    |
|-----------------|-------------------|-------------------|-------------------|
| id              | tmdb_id           | tmdb_id           | Direct            |
| name            | name              | name              | Direct            |
| birthday        | birth_date        | birth_date        | Direct            |
| profile_path    | profile_image_url | profile_image_url | Path → Full URL   |
| popularity      | popularity        | popularity        | Direct            |
| gender          | gender_code       | gender_id         | Code → FK         |
| place_of_birth  | birth_country_iso | birth_country_id  | Parse → ISO → FK  |

---

## Companies

| TMDB API Field | CSV Column  | Database Column | Transformation |
|----------------|-------------|-----------------|----------------|
| id             | tmdb_id     | tmdb_id         | Direct         |
| name           | name        | name            | Direct         |
| origin_country | country_iso | country_id      | ISO → FK       |

---

## Countries

| TMDB API Field | CSV Column | Database Column | Transformation |
|----------------|------------|-----------------|----------------|
| iso_3166_1     | iso_3166_1 | iso_3166_1      | Direct (PK)    |
| english_name   | name       | name            | Direct         |

---

## Jobs

| TMDB API Field  | CSV Column | Database Column | Transformation        |
|-----------------|------------|-----------------|-----------------------|
| —               | id         | id              | Auto-generate         |
| crew.job        | name       | name            | Extract unique values |
| crew.department | department | department      | Extract unique values |


---

## Genders

| TMDB API Field     | CSV Column | Database Column | Transformation  |
|--------------------|------------|-----------------|-----------------|
| person.gender      | id         | id              | Direct          |
| —                  | name       | name            | Map code → label|

---

## Collections

| TMDB API Field                  | CSV Column | Database Column | Transformation    |
|---------------------------------|------------|-----------------|-------------------|
| belongs_to_collection.id        | tmdb_id    | tmdb_id         | Extract from nest |
| belongs_to_collection.name      | name       | name            | Extract from nest |
| belongs_to_collection.poster_path | poster_url | poster_url    | Path → Full URL   |


---

## Cast Credits

| TMDB API Field | CSV Column | Database Column | Transformation      |
|----------------|------------|-----------------|---------------------|
| cast.id        | person_id  | person_id       | Direct              |
| cast.order     | order      | order           | Direct              |
| cast.character | character  | character       | Direct              |
| cast.cast_id   | cast_id    | cast_id         | Direct              |
| "Actor"        | job_id     | job_id          | Resolve name → ID   |

---

## Crew Credits

| TMDB API Field | CSV Column | Database Column | Transformation      |
|----------------|------------|-----------------|---------------------|
| crew.id        | person_id  | person_id       | Direct              |
| crew.job       | job_id     | job_id          | Resolve name → ID   |
| crew.credit_id | credit_id  | credit_id       | Direct              |

---