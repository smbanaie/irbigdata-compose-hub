# irbigdata-compose-hub

A centralized repository of **Docker Compose** files for Big Data engineering services.

## All Compose Files

| Category | Folder | Compose File | Description |
|----------|--------|-------------|-------------|
| Workflow & Orchestration | `Airflow/` | `docker-compose.yml` | Airflow 3.2.1 CeleryExecutor + Redis + Postgres + MinIO |
|  | `Druid/` | `docker-compose.yml` | Druid real-time analytics (single-server) |
|  | `Druid/` | `docker-compose-original.yml` | Druid original reference compose |
|  | `Superset/` | (2 variants) | Superset latest DuckDB / DuckDB 1.3 |
| Visualization & BI | `Grafana/Step1-Observability/` | `docker-compose.yml` | Grafana + Prometheus + Node Exporter + cAdvisor |
|  | `Grafana/Step2-Postgres-Monitoring/` | `docker-compose.yml` | Grafana + Postgres + pgAdmin + postgres-exporter |
|  | `Grafana/Step3-Microservices/` | `docker-compose.yaml` | Grafana + Prometheus + Loki + Tempo + Pyroscope |
|  | `Metabase/` | (1 compose) | Metabase BI with DuckDB |
| Messaging & Streaming | `Kafka/` | `docker-compose.yml` | Kafka 4.2.0 KRaft + Console + KafkaHQ + Kafka-UI |
|  | `Kafka/` | `docker-compose-cluster.yml` | Kafka 4.2.0 3-controller + 3-broker KRaft cluster |
|  | `Redpanda/` | `docker-compose.yml` | Redpanda + Console + KafkaHQ + Kafka-UI |
|  | `Redpanda/` | `docker-compose-workshop.yml` | Redpanda + MinIO + MinIO MC workshop |
|  | `Redpanda/` | `docker-compose-connect.yml` | Redpanda + Console + Redpanda Connect |
|  | `RisingWave/` | `compose.yml` (rw-single-node-docker) | RisingWave single node |
|  | `RisingWave/` | `compose-cluster.yml` | RisingWave cluster (FE + CN + Meta + etcd) |
|  | `Debezium/` | `docker-compose-redpanda-postgres-cdc.yml` | CDC: Postgres → Debezium → Redpanda |
| Storage & Object Store | `Minio/` | `docker-compose.yml` | MinIO standalone single-node |
|  | `Minio/` | `docker-compose-cluster.yml` | MinIO 3-node distributed cluster |
|  | `Minio/` | `docker-compose-cluster-lb.yml` | MinIO 3-node cluster + HAProxy LB |
|  | `RustFS/` | `docker-compose.yml` | RustFS standalone S3 storage |
|  | `LakeFS/` | `docker-compose-lake-fs.yml` | LakeFS standalone |
|  | `LakeFs-Minio/` | `docker-compose-minio.yml` | LakeFS + MinIO standalone |
|  | `LakeFs-Minio/` | `docker-compose-minio-cluster.yml` | LakeFS + MinIO cluster |
|  | `LakeFs-Minio/` | `docker-compose-lakefs.yml` | LakeFS + MinIO (alternative) |
| Databases | `Starrocks/` | `docker-compose.yml` | StarRocks 4.0.5 shared-data cluster + MinIO + HAProxy + Grafana |
|  | `Postgres/` | `docker-compose.yml` | PostgreSQL (configurable version) + pgAdmin + Northwind |
|  | `Mariadb/` | `docker-compose-pg-mariadb.yml` | MariaDB + PostgreSQL sidecar |
|  | `ClickHouse/` | `docker-compose.yml` | ClickHouse columnar database |
|  | `mongo/` | `docker-compose.yml` | MongoDB with init scripts |
|  | `Rredis/` | `docker-compose.yml` | Redis cache |
| Search & Analytics | `EK/` | `docker-compose.yml` | Elasticsearch + Kibana single-node |
|  | `EK/` | `docker-compose-logstash.yml` | ES + Logstash + Kibana (ELK) |
|  | `EK/` | `docker-compose-cluster.yml` | ES 3-node cluster + Kibana + APM Server |
|  | `EK/` | `docker-elk/docker-compose.yml` | ELK build-from-source variant |
|  | `EK/` | `apm-server-compose.yml` | APM Server standalone companion |
|  | `Hadoop/single_node/` | `docker-compose.yml` | Hadoop single-node (HDFS + YARN + MR) |
|  | `Spark/` | `docker-compose.yml` | Spark 3.1.2 + Hadoop + pyspark |
|  | `Spark/` | `docker-compose-hadoop.yml` | Spark + Hadoop integration |
|  | `Spark/` | `docker-compose-jupyter-minio.yml` | Spark 4.0.1 + Jupyter Lab + MinIO |
| Lakehouse & Catalog | `Lakehouse/Intro/` | `docker-compose.yml` | Nessie + MinIO + Dremio lakehouse |
|  | `Lakehouse/Dremio-Workshop/` | `docker-compose.yml` | Nessie + MinIO + Dremio + Superset workshop |
|  | `Lakekeeper/v1/` | `compose-lakekeeper.yaml` | LakeKeeper + Jupyter/Spark + MinIO + Postgres + Trino/StarRocks |
|  | `Lakekeeper/v2/` | `compose-lakekeeper.yaml` | LakeKeeper V2 (alternative mirrors) |

## Usage

Each compose file is self-contained. Run from the repo root or navigate into the folder:

```bash
# From repo root
docker compose -f Airflow/docker-compose.yml up -d

# Or navigate into folder
cd Redpanda
docker compose -f docker-compose-workshop.yml up -d
```

Many folders include a `Makefile` with convenience commands (e.g., `make start`, `make stop`).

## Makefiles

### Common commands

| Command | Description |
|---------|-------------|
| `make up` / `make start` | Start containers in detached mode |
| `make down` | Stop and remove containers |
| `make downv` | Stop and remove containers and volumes |
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

`make` is not available in PowerShell or Cmd by default. Options:

1. **Git Bash** (recommended) — Use the bash terminal from Git for Windows, or run `& "C:\Program Files\Git\bin\bash.exe" -c "make <command>"` from PowerShell.
2. **Chocolatey** — `choco install make`
3. **WSL** — Run `make` inside Windows Subsystem for Linux.

## Requirements

- Docker Engine 24+
- Docker Compose v2  
