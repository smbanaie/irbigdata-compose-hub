# MinIO

MinIO S3-compatible object storage. Two compose variants:

- **`docker-compose.yml`** — single-node with init container (minio_mc)
- **`docker-compose-cluster.yml`** — 3-node cluster (distributed mode)

## Single-node (`docker-compose.yml`)

### Services

| Service | Container | Image | Ports |
|---------|-----------|-------|-------|
| **minio** | `minio` | `docker.arvancloud.ir/minio/minio:latest` | `9000`, `9001` |
| **minio_mc** | — | `docker.arvancloud.ir/minio/mc:latest` | — |

`minio_mc` is a short-lived init container that creates a service account access key pair on startup, then exits.

Credentials: user `miniouser`, password `miniopassword`.  
Service account: key `AAAAAAAAAAAAAAAAAAAA` / secret `BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB`.

## Cluster (`docker-compose-cluster.yml`)

3-node distributed MinIO cluster.

### Services

| Service | Container | Ports |
|---------|-----------|-------|
| **minio1** | `minio1` | `9000:9000` (S3), `9001:9001` (console) |
| **minio2** | `minio2` | `9002:9001` (console) |
| **minio3** | `minio3` | `9003:9001` (console) |

Credentials: user `minioadmin`, password `minioadmin123`.

### Ports

| Port | Service | Access |
|------|---------|--------|
| `9000` | S3 API (via minio1) | http://localhost:9000 |
| `9001` | Console (minio1) | http://localhost:9001 |
| `9002` | Console (minio2) | http://localhost:9002 |
| `9003` | Console (minio3) | http://localhost:9003 |

## Usage

```bash
# Single-node + init container
docker compose -f docker-compose.yml up -d

# 3-node cluster
docker compose -f docker-compose-cluster.yml up -d

# Or with Makefile
make start
```
