# ClickHouse

Production-ready ClickHouse 26.5 single-node deployment with resource limits, healthchecks, and init script support.

## Quick Start

```bash
# Create config directories (required even if empty)
mkdir -p config.d users.d initdb

# Start
docker compose up -d

# Verify
docker exec -it clickhouse-server clickhouse-client \
  --password clickhouse123 --query "SELECT version()"
```

## Services

| Service | Container | Image | Ports |
|---------|-----------|-------|-------|
| **clickhouse** | `clickhouse-server` | `clickhouse/clickhouse-server:26.5` | `8123` (HTTP), `9000` (native) |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLICKHOUSE_VERSION` | `26.5` | ClickHouse image tag |
| `CLICKHOUSE_PASSWORD` | `clickhouse123` | Default user password |
| `CH_HTTP_PORT` | `8123` | HTTP interface port |
| `CH_NATIVE_PORT` | `9000` | Native TCP protocol port |
| `CH_CPU_LIMIT` | `4` | CPU limit |
| `CH_MEM_LIMIT` | `16G` | Memory limit |
| `CH_CPU_RESERVE` | `2` | CPU reservation |
| `CH_MEM_RESERVE` | `8G` | Memory reservation |

## Volumes

| Volume | Container Path | Purpose |
|--------|---------------|---------|
| `clickhouse_data` | `/var/lib/clickhouse` | Persistent data storage |
| `clickhouse_logs` | `/var/log/clickhouse-server` | Server logs |
| `./config.d` | `/etc/clickhouse-server/config.d` | Custom XML config files |
| `./users.d` | `/etc/clickhouse-server/users.d` | Per-user quotas and settings |
| `./initdb` | `/docker-entrypoint-initdb.d` | SQL/shell scripts (run on first start) |

## Initialization Scripts

Place `.sql`, `.sql.gz`, or `.sh` files in `./initdb/`. They execute in alphabetical order on the first container start.

Example — `./initdb/01-create-tables.sql`:
```sql
CREATE DATABASE IF NOT EXISTS analytics;

CREATE TABLE analytics.events (
    timestamp DateTime,
    event_type String,
    user_id UInt64,
    payload String
) ENGINE = MergeTree()
ORDER BY (event_type, timestamp);
```

## Custom Configuration

Drop XML files into `config.d/` to override server settings:

`config.d/custom.xml`:
```xml
<clickhouse>
    <max_connections>200</max_connections>
    <max_memory_usage>10000000000</max_memory_usage>
</clickhouse>
```

Per-user quotas go in `users.d/`:

`users.d/analyst.xml`:
```xml
<clickhouse>
    <profiles>
        <analyst>
            <max_memory_usage>5000000000</max_memory_usage>
            <max_threads>4</max_threads>
        </analyst>
    </profiles>
</clickhouse>
```

## .env File

Create a `.env` in this directory (do not commit):

```ini
CLICKHOUSE_PASSWORD=your_strong_password
```

## CLI Commands

```bash
# Connect with client
docker exec -it clickhouse-server clickhouse-client --password clickhouse123

# Run query directly
docker exec -it clickhouse-server clickhouse-client \
  --password clickhouse123 --query "SHOW DATABASES"

# Check resource usage
docker stats clickhouse-server
```

## Production Notes

- **Backup**: Use `clickhouse-backup` or `ALTER TABLE ... FREEZE` with S3-compatible storage
- **High Availability**: This is a single-node setup. For HA, deploy a replicated cluster with ClickHouse Keeper across multiple nodes
- **Security**: Do not expose ports `8123`/`9000` to the public internet without a reverse proxy and TLS
- **Monitoring**: ClickHouse exposes a built-in Prometheus endpoint at `http://localhost:8123/metrics`
