# ClickHouse

Production-ready ClickHouse single-node and distributed 3-node cluster deployments.

## Single-Node

### Quick Start

```bash
# Setup directories
mkdir -p config.d users.d initdb

# Start
docker compose up -d

# Verify
docker exec clickhouse-26.5-jammy clickhouse-client \
  --password clickh0use@123 --query "SELECT version()"
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLICKHOUSE_VERSION` | `26.5` | ClickHouse image tag |
| `CLICKHOUSE_PASSWORD` | `clickh0use@123` | Default user password |
| `CLICKHOUSE_DB` | `forex` | Pre-created database |
| `CH_HTTP_PORT` | `8123` | HTTP interface port |
| `CH_NATIVE_PORT` | `9000` | Native TCP protocol port |
| `CH_CPU_LIMIT` | `4` | CPU limit |
| `CH_MEM_LIMIT` | `16G` | Memory limit |
| `CH_CPU_RESERVE` | `2` | CPU reservation |
| `CH_MEM_RESERVE` | `8G` | Memory reservation |

### Volumes

| Volume | Container Path | Purpose |
|--------|---------------|---------|
| `clickhouse_data` | `/var/lib/clickhouse` | Persistent data storage |
| `clickhouse_logs` | `/var/log/clickhouse-server` | Server logs |
| `./config.d` | `/etc/clickhouse-server/config.d` | Custom XML config files |
| `./users.d` | `/etc/clickhouse-server/users.d` | Per-user settings |
| `./initdb` | `/docker-entrypoint-initdb.d` | SQL/shell scripts (run on first start) |

### CLI

```bash
docker exec -it clickhouse-26.5-jammy clickhouse-client --password clickh0use@123
docker exec clickhouse-26.5-jammy clickhouse-client --password clickh0use@123 --query "SHOW DATABASES"
```

## Distributed 3-Node Cluster

Located in `distributed/`. 3 shards × 1 replica (3S_1R) with embedded ClickHouse Keeper.

### Quick Start

```bash
cd distributed
docker compose up -d
```

### Port Mapping

| Node | HTTP | Native | Keeper | Interserver |
|------|------|--------|--------|-------------|
| chnode1 | `8123` | `9000` | `9181` | `9234` |
| chnode2 | `8124` | `9001` | `9182` | `9235` |
| chnode3 | `8125` | `9002` | `9183` | `9236` |

### Basic Usage

```bash
# Create database & tables on all nodes
docker exec chnode1 clickhouse-client --query \
  "CREATE DATABASE IF NOT EXISTS rides ON CLUSTER 'cluster_3S_1R'"

docker exec chnode1 clickhouse-client --query \
  "CREATE TABLE rides.trips_local ON CLUSTER 'cluster_3S_1R' (
     VendorID Int32, tpep_pickup_datetime DateTime64(6),
     tpep_dropoff_datetime DateTime64(6), passenger_count Nullable(Int64),
     trip_distance Nullable(Float64), fare_amount Nullable(Float64),
     tip_amount Nullable(Float64), total_amount Nullable(Float64)
   ) ENGINE = MergeTree
   PARTITION BY toYYYYMM(tpep_pickup_datetime)
   ORDER BY (tpep_pickup_datetime, tpep_dropoff_datetime)"

# Create distributed table
docker exec chnode1 clickhouse-client --query \
  "CREATE TABLE rides.trips_distributed ON CLUSTER 'cluster_3S_1R'
   AS rides.trips_local
   ENGINE = Distributed('cluster_3S_1R', rides, trips_local, rand())"

# Insert & query across all nodes
docker exec chnode1 clickhouse-client --query \
  "INSERT INTO rides.trips_distributed VALUES
   (1,'2023-09-27 08:00:00','2023-09-27 08:30:00',2,5.2,20.5,4.0,25.8),
   (2,'2023-09-27 09:15:00','2023-09-27 09:45:00',1,3.8,16.0,0,17.3)"

docker exec chnode1 clickhouse-client --query \
  "SELECT hostName() AS host, count(*) AS cnt FROM rides.trips_distributed GROUP BY host"
```

## Production Notes

- **Backup**: Use `clickhouse-backup` or `ALTER TABLE ... FREEZE` with S3-compatible storage
- **Security**: Do not expose ports directly. Default user (`clickh0use@123`) has `access_management=1`. Set a stronger password via `ALTER USER default IDENTIFIED BY 'new_pass'`
- **Monitoring**: Built-in Prometheus endpoint at `http://localhost:8123/metrics`
