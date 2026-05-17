# irbigdata-compose-hub

A centralized repository of **Docker Compose** files for Big Data engineering services. Spin up data infrastructure locally with minimal configuration.

## Services

### Workflow & Orchestration
- **[Airflow](./Airflow)** — Apache Airflow 3.2.1 (CeleryExecutor) with custom image, minio, management UIs
- **[Druid](./Druid)** — Apache Druid real-time analytics database

### Messaging & Streaming
- **[Kafka](./Kafka)** — Apache Kafka 4.2.0 KRaft (no Zookeeper) + Console, KafkaHQ, Kafka-UI (and legacy ZK-based variants)
- **[Redpanda](./Redpanda)** — Redpanda Kafka-compatible streaming + Console, KafkaHQ, Kafka-UI
- **[RisingWave](./RisingWave)** — RisingWave streaming database

### Storage & Object Store
- **[Minio](./Minio)** — Standalone MinIO S3-compatible object storage
- **[LakeFS](./LakeFS)** — Standalone LakeFS data lake versioning
- **[LakeFs-Minio](./LakeFs-Minio)** — LakeFS backed by MinIO (standalone or clustered)

### Databases
- **[Starrocks](./Starrocks)** — StarRocks v4 (shared-data) with MinIO, 3 FE + 3 CN cluster
- **[Postgres](./Postgres)** — PostgreSQL
- **[Mariadb](./Mariadb)** — MariaDB (with PostgreSQL sidecar)
- **[ClickHouse](./ClickHouse)** — ClickHouse columnar database
- **[Mongo](./mongo)** — MongoDB with init scripts
- **[Rredis](./Rredis)** — Redis (in-memory cache)

### Search & Analytics
- **[EK](./EK)** — Elasticsearch + Kibana (ELK stack) with APM Server, Logstash, Metricbeat, and other extensions
- **[Hadoop](./Hadoop)** — Single-node Hadoop (HDFS, YARN, MapReduce) with examples
- **[Spark](./Spark)** — Apache Spark with Hadoop integration

### Log Processing
- **[logstash](./logstash)** — *(empty — ready for Logstash configs)*

## Usage

Each directory is self-contained. Navigate into a service folder and run:

```bash
docker compose up -d
```

Many folders include a `Makefile` with convenience commands (e.g., `make start`, `make stop`, `make env`).

## Makefiles

Many service folders include a `Makefile` with convenience commands to simplify Docker management.

### Common commands

| Command | Description |
|---------|-------------|
| `make up` / `make start` | Start containers in detached mode |
| `make down` | Stop and remove containers |
| `make downv` | Stop and remove containers **and** volumes |
| `make stop` | Stop containers (without removing) |
| `make restart` | Down then up |
| `make logs` | Tail container logs |
| `make ps` | List container status |
| `make exec` | Open a shell inside the main container |
| `make run` | Run a one-off command inside the main container |
| `make stats` | Show live Docker resource usage |
| `make clean` | Remove all exited containers |
| `make remove` | Stop and delete containers |

### Using Make on Windows

`make` is not available in PowerShell or Cmd by default. You have several options:

1. **Git Bash** (recommended) — Git for Windows ships with a Bash environment that includes `make`. Use its terminal instead of PowerShell/Cmd, or run `& "C:\Program Files\Git\bin\bash.exe" -c "make <command>"` from PowerShell.

2. **Chocolatey** — Install make globally:
   ```powershell
   choco install make
   ```

3. **GnuWin32** — Download `make` from GnuWin32 and add it to your `PATH`.

4. **WSL** — Run `make` inside Windows Subsystem for Linux.

## Requirements

- Docker Engine 24+
- Docker Compose v2  
