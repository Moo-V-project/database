# Flyway automated database migrations for Moo-V.

## Flyway

### Installation

You can use the Flyway desktop application, cli tool, docker image, etc. by your choice.
The official quickstart guides for all the options is available at https://documentation.red-gate.com/flyway/getting-started-with-flyway/quickstart-guides.

Also you can install the Flyway CLI tool using package managers such as homebrew or snap.

### Configuration

#### General configuration

The configuration file `flyway.toml` includes only general and environment-agnostic settings for Flyway.
This file must not be altered for any specific environment and must not include any connection details or credentials.

#### Environment-specific configuration

The environment-specific configuration file `flyway.dev.toml` includes connection details and credentials for the development environment.
This file is ignored by git and must not be committed to the repository.
Each developer should create their own `flyway.dev.toml` file based on the template `flyway.dev.toml.example` with the appropriate connection details for their local development environment.

As an alternative, you can also set the connection details using environment variables:
- `FLYWAY_URL` - the JDBC URL of the database.
- `FLYWAY_USER` - the database user.
- `FLYWAY_PASSWORD` - the database password.

The full configuration reference for Flyway is available at https://documentation.red-gate.com/fd/configuration-277578842.html

### Migrations

#### Design

Before creating a migration script, the updated database schema must be designed and documented in the `schema` directory.
Schema design documents must follow the Flyway naming convention: `V{version}__{description}.md`,
where `{version}` is a [SemVer version number](https://semver.org/) and `{description}` is a brief description of the schema change (e.g., `add_email_to_user`).
The version number represents only the version of the database and does not have to match the version of the application itself.

The full naming convention reference is available at https://www.red-gate.com/blog/database-devops/flyway-naming-patterns-matter/.
Since the official documentation is a bit screwed up, it is a link to a blog post, but it describes the naming convention clearly.

#### Migration SQL scripts

Migrations' SQL scripts are located in the `sql` directory and must follow the same naming convention as the schema design documents: `V{version}__{description}.sql`.

### Running migrations

Migration running process differs based on the Flyway tool you are using.
The exact instructions for each tool are available in the [official quickstart guides](https://documentation.red-gate.com/flyway/getting-started-with-flyway/quickstart-guides).

Take into account that is you're using flyway.dev.toml for configuration, you must specify it when running the migrations.
For example with the CLI tool you should run `flyway -configFiles=flyway.dev.toml migrate`.

