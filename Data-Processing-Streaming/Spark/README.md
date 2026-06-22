# Spark

Apache Spark cluster with Hadoop integration and optional Jupyter Lab + MinIO.

## Variants

| Compose | Description |
|---------|-------------|
| `docker-compose.yml` | Spark 3.1.2 + Hadoop + pyspark (Jupyter Notebook) |
| `docker-compose-hadoop.yml` | Spark + Hadoop cluster |
| `docker-compose-jupyter-minio.yml` | Spark 4.0.1 + Jupyter Lab + MinIO (build from Dockerfile) |

## Jupyter + MinIO variant

Spark 4 master/worker cluster with Jupyter Lab and MinIO object storage.

| Service | Port |
|---------|------|
| spark-master | `9080:8080`, `7077:7077` |
| spark-worker | `9081:8081` |
| jupyter | `9888:8888`, `4040-4042` |
| minio | `9000`, `9001` (requires `--profile minio`) |

```bash
# Build the Spark 4 image first
docker compose -f docker-compose-jupyter-minio.yml build

# Start without MinIO
docker compose -f docker-compose-jupyter-minio.yml up -d

# Start with MinIO
docker compose -f docker-compose-jupyter-minio.yml --profile minio up -d
```

Access Jupyter Lab at http://localhost:9888 (no token/password).
