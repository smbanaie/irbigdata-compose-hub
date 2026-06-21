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
  --query "SELECT version()"
```

## Services

| Service | Container | Image | Ports |
|---------|-----------|-------|-------|
| **clickhouse** | `clickhouse-server` | `docker.arvancloud.ir/clickhouse/clickhouse-server:26.5` | `8123` (HTTP), `9000` (native) |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLICKHOUSE_VERSION` | `26.5` | ClickHouse image tag |
| `CLICKHOUSE_PASSWORD` | *(empty)* | Default user password. Requires `CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1` to be removed for this to take effect |
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

## Default User

With `CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1` (our default):

| Setting | Value |
|---------|-------|
| Username | `default` |
| Password | *(empty)* |
| Access | `access_management=1` — can create users, roles, grants via SQL |
| Network | `::/0` (all interfaces) |

Connect without a password and set one via SQL:

```sql
ALTER USER default IDENTIFIED BY 'new_password';
```

To switch to the traditional password model (password set via env var at container start), remove `CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT: 1` from the compose file.

## .env File

Create a `.env` in this directory (do not commit) to set passwords via SQL on first start, or remove `CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT=1` from the compose and set:

```ini
CLICKHOUSE_PASSWORD=your_strong_password
```

## CLI Commands

```bash
# Connect with client (no password when ACCESS_MANAGEMENT=1)
docker exec -it clickhouse-server clickhouse-client

# Run query directly
docker exec clickhouse-server clickhouse-client \
  --query "SHOW DATABASES"

# Check resource usage
docker stats clickhouse-server
```

## Remote Connections

By default, ClickHouse only listens on localhost inside the container. The `config.d/listen.xml` override enables listening on all interfaces (`0.0.0.0`), allowing remote connections.

Connect from a remote server using the host IP:

```bash
# Native protocol (port 9000)
clickhouse-client --host <host-ip> --port 9000

# HTTP interface (port 8123)
curl "http://<host-ip>:8123/?query=SELECT+version()"
```

**Requirements:**
- The host firewall must allow inbound traffic on ports `8123`/`9000`
- Docker must expose these ports (already configured in the compose file)

## Security

- Do not expose ports `8123`/`9000` directly to the public internet without a reverse proxy and TLS
- Default user has an empty password and full admin rights. Set a password via SQL for any remote-facing deployment:
  ```sql
  ALTER USER default IDENTIFIED BY 'your_strong_password';
  ```
- Change the password in the compose file by removing `CLICKHOUSE_DEFAULT_ACCESS_MANAGEMENT: 1` and setting `CLICKHOUSE_PASSWORD`

## Production Notes

- **Backup**: Use `clickhouse-backup` or `ALTER TABLE ... FREEZE` with S3-compatible storage
- **High Availability**: This is a single-node setup. For HA, deploy a replicated cluster with ClickHouse Keeper across multiple nodes
- **Monitoring**: ClickHouse exposes a built-in Prometheus endpoint at `http://localhost:8123/metrics`
