# Lakekeeper

LakeKeeper Iceberg catalog platform with Spark/Jupyter, MinIO, PostgreSQL, and optional Trino/StarRocks query engines.

## Variants

| Folder | Compose | Description |
|--------|---------|-------------|
| **v1** | `compose-lakekeeper.yaml` | LakeKeeper + Bitnami Postgres + Bitnami MinIO + Jupyter + Trino/StarRocks (profiles) |
| **v2** | `compose-lakekeeper.yaml` | Same stack with official Postgres 18 and mirror-docker LakeKeeper image |

## Services

| Service | Image | Port |
|---------|-------|------|
| jupyter | build (`./jupyter`) | `8888`, `4040` |
| lakekeeper | catalog image | `8181` |
| migrate | catalog image | — (one-time DB migration) |
| bootstrap | `docker.arvancloud.ir/curlimages/curl` | — (one-time API bootstrap) |
| initialwarehouse | `docker.arvancloud.ir/curlimages/curl` | — (creates default warehouse) |
| db | postgres | `5454:5432` |
| minio | bitnami/minio | `9000`, `9001` |
| trino | `docker.arvancloud.ir/trinodb/trino:476` (profile) | `9999:8080` |
| starrocks | `docker.arvancloud.ir/starrocks/allin1-ubuntu` (profile) | `9030`, `8030` |

## Profiles

| Profile | Adds |
|---------|------|
| *(default)* | Jupyter, LakeKeeper, Postgres, MinIO |
| `trino` | + Trino query engine |
| `starrocks` | + StarRocks query engine |

## Usage

```bash
cd v1
docker compose -f compose-lakekeeper.yaml up -d

# With query engines
docker compose -f compose-lakekeeper.yaml --profile trino up -d
docker compose -f compose-lakekeeper.yaml --profile starrocks up -d
```
