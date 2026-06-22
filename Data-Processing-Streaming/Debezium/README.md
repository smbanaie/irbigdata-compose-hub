# Debezium

Change Data Capture (CDC) pipeline with PostgreSQL -> Debezium -> Redpanda.

## Services

| Service | Image | Port |
|---------|-------|------|
| redpanda | `docker.arvancloud.ir/redpandadata/redpanda:latest` | `9092`, `29092` |
| console | `docker.arvancloud.ir/redpandadata/console:latest` | `9100:8080` |
| debezium | `docker.arvancloud.ir/debezium/connect:3.0.0.Final` | `8083` |
| debezium-ui | `docker.arvancloud.ir/debezium/debezium-ui:latest` | `8080` |
| postgres | `docker.arvancloud.ir/library/postgres:18` | `5434:5432` |

Postgres is configured with `wal_level=logical` for CDC. Debezium Connect captures changes and publishes to Redpanda.

## Usage

```bash
docker compose -f docker-compose-redpanda-postgres-cdc.yml up -d
```

## Access

| Service | URL |
|---------|-----|
| Redpanda Console | http://localhost:9100 |
| Debezium UI | http://localhost:8080 |
| Debezium API | http://localhost:8083/connectors |

## Creating a Connector

```bash
curl -X POST http://localhost:8083/connectors \
  -H "Content-Type: application/json" \
  -d '{
    "name": "financial-cdc-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "database.hostname": "postgres",
      "database.port": "5432",
      "database.user": "postgres",
      "database.password": "postgres",
      "database.dbname": "financial_db",
      "topic.prefix": "pg_financial",
      "plugin.name": "pgoutput"
    }
  }'
```
