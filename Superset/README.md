# Superset

Apache Superset with DuckDB support for data exploration and visualization.

## Variants

| Compose | Description |
|---------|-------------|
| `docker-compose.yml` | Superset with DuckDB (latest) |
| `docker-compose-duckdb1.3.yml` | Superset with DuckDB 1.3 pinned |

Both use custom Dockerfiles that install the DuckDB driver and mount `superset_config.py` for configuration.

## Services

| Service | Image | Port |
|---------|-------|------|
| superset | build (custom Dockerfile) | `8088:8088` |

## Usage

```bash
docker compose -f docker-compose.yml up -d
# or for DuckDB 1.3
docker compose -f docker-compose-duckdb1.3.yml up -d
```

Access at http://localhost:8088.

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Superset build with DuckDB driver |
| `Dockerfile-1.3` | Superset build with pinned DuckDB 1.3 |
| `superset_config.py` | Superset configuration |
| `data/` | Mount point for DuckDB files |
