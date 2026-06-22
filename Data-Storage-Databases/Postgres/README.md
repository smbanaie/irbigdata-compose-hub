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

---

## Production Cluster (`docker-compose-production-cluster.yml`)

PostgreSQL 18 replication cluster with synchronous, asynchronous, and cascading standbys.

| Service | Container | Port | Type |
|---------|-----------|------|------|
| primary | `pg-primary` | `5432` | Primary (read/write) |
| standby_sync | `pg-standby-sync` | `5433` | Synchronous standby |
| standby_async | `pg-standby-async` | `5434` | Asynchronous standby |
| standby_cascade | `pg-standby-cascade` | `5435` | Cascading standby (profile: `cascade`) |

### Key parameters

| Parameter | Why |
|-----------|-----|
| `max_wal_senders=10` | Enough for all standbys + tools |
| `max_replication_slots=10` | Room for growth |
| `wal_keep_size=2GB` | Extra safety buffer |
| `hot_standby_feedback=on` | Prevents query cancellation on standbys |
| `wal_log_hints=on` | Required for pg_rewind |
| `archive_mode=on` + `archive_command` | WAL archiving for point-in-time recovery |
| `synchronous_standby_names='FIRST 1 (standby_sync)'` | `standby_sync` is the synchronous standby |

### Initialising the Primary

```bash
docker compose -f docker-compose-production-cluster.yml up -d primary
sleep 10
```

Create the replication user and a monitoring user:

```bash
docker exec -it pg-primary psql -U postgres << 'EOF'
CREATE USER replicator WITH REPLICATION LOGIN PASSWORD 'replpass';
CREATE USER monitor WITH LOGIN PASSWORD 'monitor123';
GRANT pg_monitor TO monitor;
EOF
```

Create replication slots:

```bash
docker exec pg-primary psql -U postgres -c \
  "SELECT pg_create_physical_replication_slot('standby_sync_slot');"
docker exec pg-primary psql -U postgres -c \
  "SELECT pg_create_physical_replication_slot('standby_async_slot');"
docker exec pg-primary psql -U postgres -c \
  "SELECT pg_create_physical_replication_slot('standby_cascade_slot');"
```

Allow replication connections:

```bash
docker exec pg-primary bash -c \
  "echo 'host replication replicator 0.0.0.0/0 md5' >> /var/lib/postgresql/data/pg_hba.conf"
docker exec pg-primary psql -U postgres -c "SELECT pg_reload_conf();"
```

Verify slots:

```bash
docker exec pg-primary psql -U postgres -c \
  "SELECT slot_name, active FROM pg_replication_slots;"
```

### Loading Sample Data

```bash
docker exec -i pg-primary psql -U postgres << 'EOF'
CREATE TABLE customers (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES customers(id),
    amount NUMERIC(10,2) NOT NULL,
    status TEXT DEFAULT 'pending',
    order_date TIMESTAMP DEFAULT now()
);

INSERT INTO customers (name, email)
SELECT 'Customer ' || i, 'user' || i || '@example.com'
FROM generate_series(1, 10000) i;

INSERT INTO orders (customer_id, amount, status)
SELECT (random() * 9999)::int + 1,
       (random() * 1000)::numeric(10,2),
       CASE (random() * 3)::int
           WHEN 0 THEN 'pending'
           WHEN 1 THEN 'shipped'
           ELSE 'delivered'
       END
FROM generate_series(1, 50000) i;

CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
EOF
```

### Building the Synchronous Standby

```bash
docker compose -f docker-compose-production-cluster.yml stop standby_sync
rm -rf standby_sync_data/*

docker run --rm \
  --network postgres_pg-net \
  -v $(pwd)/standby_sync_data:/standby \
  docker.arvancloud.ir/postgres:18 \
  pg_basebackup -h pg-primary -U replicator -p 5432 -D /standby -Fp -Xs -P -R

cat >> standby_sync_data/postgresql.auto.conf << 'EOF'
primary_slot_name = 'standby_sync_slot'
primary_conninfo = 'host=pg-primary port=5432 user=replicator password=replpass application_name=standby_sync'
EOF

docker compose -f docker-compose-production-cluster.yml up -d standby_sync
sleep 5

docker exec pg-primary psql -U postgres -c \
  "SELECT application_name, state, sync_state FROM pg_stat_replication;"
```

Expected: `standby_sync` shows `sync_state = sync`.

### Building the Asynchronous Standby

```bash
docker compose -f docker-compose-production-cluster.yml stop standby_async
rm -rf standby_async_data/*

docker run --rm \
  --network postgres_pg-net \
  -v $(pwd)/standby_async_data:/standby \
  docker.arvancloud.ir/postgres:18 \
  pg_basebackup -h pg-primary -U replicator -p 5432 -D /standby -Fp -Xs -P -R

cat >> standby_async_data/postgresql.auto.conf << 'EOF'
primary_slot_name = 'standby_async_slot'
primary_conninfo = 'host=pg-primary port=5432 user=replicator password=replpass application_name=standby_async'
EOF

docker compose -f docker-compose-production-cluster.yml up -d standby_async
sleep 5

docker exec pg-primary psql -U postgres -c \
  "SELECT application_name, state, sync_state FROM pg_stat_replication ORDER BY sync_state DESC;"
```

Expected: `standby_sync` = sync, `standby_async` = async.

### Adding a Cascading Standby (Optional)

Requires the `cascade` profile.

#### Prepare `standby_sync` as Upstream

```bash
docker exec pg-standby-sync psql -U postgres << 'EOF'
CREATE USER replicator WITH REPLICATION LOGIN PASSWORD 'replpass';
SELECT pg_create_physical_replication_slot('standby_cascade_slot');
EOF

docker exec pg-standby-sync bash -c \
  "echo 'host replication replicator 0.0.0.0/0 md5' >> /var/lib/postgresql/data/pg_hba.conf"
docker exec pg-standby-sync psql -U postgres -c "SELECT pg_reload_conf();"
```

#### Clone from `standby_sync`

```bash
rm -rf standby_cascade_data/*

docker run --rm \
  --network postgres_pg-net \
  -v $(pwd)/standby_cascade_data:/standby \
  docker.arvancloud.ir/postgres:18 \
  pg_basebackup -h pg-standby-sync -U replicator -p 5432 -D /standby -Fp -Xs -P -R

cat >> standby_cascade_data/postgresql.auto.conf << 'EOF'
primary_slot_name = 'standby_cascade_slot'
primary_conninfo = 'host=pg-standby-sync port=5432 user=replicator password=replpass application_name=standby_cascade'
EOF

docker compose -f docker-compose-production-cluster.yml --profile cascade up -d standby_cascade
sleep 5

docker exec pg-standby-sync psql -U postgres -c \
  "SELECT application_name, state FROM pg_stat_replication;"
```
