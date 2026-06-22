# Lakehouse

Iceberg lakehouse setups using Nessie catalog, MinIO storage, and Dremio SQL engine.

## Variants

| Folder | Compose | Description |
|--------|---------|-------------|
| **Intro** | `docker-compose.yml` | Nessie + MinIO + Dremio (basic Iceberg lakehouse) |
| **Dremio-Workshop** | `docker-compose.yml` | Nessie + MinIO + MinIO Setup + Dremio + Superset (full workshop) |

## Intro

| Service | Image | Port |
|---------|-------|------|
| nessie | `docker.arvancloud.ir/projectnessie/nessie:latest` | `19120` |
| minio | `docker.arvancloud.ir/minio/minio:latest` | `9000`, `9001` |
| dremio | `docker.arvancloud.ir/dremio/dremio-oss:latest` | `9047`, `31010`, `32010` |

## Dremio-Workshop

Adds MinIO setup (bucket creation, sample data loading) and Apache Superset for visualization.

| Service | Image | Port |
|---------|-------|------|
| nessie | `docker.arvancloud.ir/projectnessie/nessie:latest` | `19120` |
| minio | `docker.arvancloud.ir/minio/minio:latest` | `9000`, `9001` |
| minio-setup | `docker.arvancloud.ir/minio/mc:latest` | — (one-time init) |
| dremio | `docker.arvancloud.ir/dremio/dremio-oss` | `9047`, `31010`, `32010`, `45678` |
| superset | `docker.arvancloud.ir/alexmerced/dremio-superset` | `8088` |

## Usage

```bash
cd Intro
docker compose up -d

# Or for the workshop
cd ../Dremio-Workshop
docker compose up -d
```

## Access

- Dremio UI: http://localhost:9047
- MinIO Console: http://localhost:9001
- Nessie: http://localhost:19120
- Superset (workshop): http://localhost:8088
