# Airflow

Apache Airflow 3.2.1 with CeleryExecutor, custom image build, Redis, PostgreSQL 15, and optional MinIO.

## Services

| Service | Container | Image | Port |
|---------|-----------|-------|------|
| **postgres** | — | `docker.arvancloud.ir/postgres:15-alpine` | `5454:5432` |
| **redis** | — | `docker.arvancloud.ir/redis:alpine` | — |
| **airflow-apiserver** | — | custom (build: `.`) | `9080:8080` |
| **airflow-scheduler** | — | custom (build: `.`) | — |
| **airflow-dag-processor** | — | custom (build: `.`) | — |
| **airflow-worker** | — | custom (build: `.`) | — |
| **airflow-triggerer** | — | custom (build: `.`) | — |
| **flower** | — | custom (build: `.`) | `5555:5555` |
| **minio** | `minio` | `docker.arvancloud.ir/minio/minio:latest` | `9000`, `9001` |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AIRFLOW_IMAGE_NAME` | `docker.arvancloud.ir/apache/airflow:3.2.1` | Airflow image (overridden by `build: .`) |
| `AIRFLOW_UID` | `50000` | User ID in containers |
| `AIRFLOW_PROJ_DIR` | `.` | Base path for volume mounts |
| `_AIRFLOW_WWW_USER_USERNAME` | `airflow` | Admin username |
| `_AIRFLOW_WWW_USER_PASSWORD` | `airflow` | Admin password |
| `_PIP_ADDITIONAL_REQUIREMENTS` | `minio` | Extra pip packages |
| `FERNET_KEY` | — | Fernet encryption key |
| `ENV_FILE_PATH` | `.env` | Path to env file |

## Profiles

| Profile | Services |
|---------|----------|
| *(default)* | postgres, redis, api-server, scheduler, dag-processor, worker |
| `triggerer` | + airflow-triggerer |
| `flower` | + flower (Celery monitoring) |
| `minio` | + minio (S3-compatible storage) |
| `debug` | + airflow-cli |

## Usage

```bash
# Copy env file and start
cp .env.example .env
docker compose -f docker-compose.yml up -d

# With profiles
docker compose --profile minio --profile flower up -d

# Or with Makefile
make start
```

## Volumes

| Volume | Path (container) | Purpose |
|--------|------------------|---------|
| `./dags` | `/opt/airflow/dags` | DAG files |
| `./logs` | `/opt/airflow/logs` | Logs |
| `./config` | `/opt/airflow/config` | Config files |
| `./plugins` | `/opt/airflow/plugins` | Plugins |
| `./data` | `/data` | Shared data |
| `postgres-db-volume` | `/var/lib/postgresql` | Database files |
| `minio-data` | `/data` (minio) | Object storage |
