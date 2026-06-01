# Postgres

PostgreSQL (configurable version) with pgAdmin 4.

## Services

| Service | Container | Image | Port |
|---------|-----------|-------|------|
| **postgres** | `postgres` | `docker.devneeds.ir/library/postgres:${PG_VERSION:-18}` | `5434:5432` |
| **pgadmin** | `pgadmin4` | `docker.devneeds.ir/dpage/pgadmin4` | `5050:80` |

pgAdmin runs under the `pgadmin` profile — start it with `--profile pgadmin`.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PG_VERSION` | `18` | PostgreSQL image version |
| `PG_USER` | `postgres` | Database user |
| `PG_PASS` | `postgres123` | Database password |
| `PG_DB` | `sepahram` | Default database name |
| `PG_AUTH` | `trust` | Host authentication method |
| `APP_NAME` | `sepahram` | Network name suffix |

pgAdmin credentials are hardcoded: email `admin@admin.com`, password `pgadmin123`.

## Usage

```bash
# Start PostgreSQL
docker compose -f docker-compose.yml up -d

# Start PostgreSQL + pgAdmin
docker compose -f docker-compose.yml --profile pgadmin up -d

# Or with Makefile
make start
```

## Volumes

| Volume | Path (container) | Purpose |
|--------|------------------|---------|
| `./db_data` | `/var/lib/postgresql/data` | Database files (PGDATA) |
| `./postgres-init/` | `/docker-entrypoint-initdb.d` | SQL init scripts (run once at first start) |
| `pgadmin_data` (named) | `/var/lib/pgadmin` | pgAdmin session data |
