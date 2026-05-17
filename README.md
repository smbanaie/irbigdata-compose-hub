# irbigdata-compose-hub

A centralized repository of **Docker Compose** files for Big Data engineering services. Spin up data infrastructure locally with minimal configuration.

## Services

### Workflow & Orchestration
- **[Airflow](./Airflow)** — Apache Airflow with worker support, sample DAGs, and image extension guide
- **[Druid](./Druid)** — Apache Druid real-time analytics database

### Messaging & Streaming
- **[Kafka](./Kafka)** — Apache Kafka (multiple compose variants), Kafka Manager, Zookeeper, JAAS config

### Storage & Object Store
- **[Minio](./Minio)** — Standalone MinIO S3-compatible object storage with Nginx
- **[LakeFS](./LakeFS)** — Standalone LakeFS data lake versioning
- **[LakeFs-Minio](./LakeFs-Minio)** — LakeFS backed by MinIO (standalone or clustered)

### Databases
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

## Requirements

- Docker Engine 24+
- Docker Compose v2  
