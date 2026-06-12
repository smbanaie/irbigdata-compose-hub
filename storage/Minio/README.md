# MinIO

MinIO S3-compatible object storage. Three compose variants:

> Part of the **storage/** folder — see also [RustFS](../rustfs/) and [libreFS](../librefs/).

- **`docker-compose.yml`** — single-node with init container (minio_mc)
- **`docker-compose-cluster.yml`** — 3-node distributed cluster
- **`docker-compose-cluster-lb.yml`** — 3-node distributed cluster + HAProxy load balancer

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
| **minio2** | `minio2` | — |
| **minio3** | `minio3` | — |

Credentials: user `minioadmin`, password `minioadmin123`.

## Cluster with Load Balancer (`docker-compose-cluster-lb.yml`)

3-node distributed MinIO cluster fronted by HAProxy for high availability.

### Services

| Service | Container | Ports |
|---------|-----------|-------|
| **minio-1** | `minio-1` | `9000:9000` (S3), `9001:9001` (console) |
| **minio-2** | `minio-2` | `9002:9000` (S3), `9003:9001` (console) |
| **minio-3** | `minio-3` | `9004:9000` (S3), `9005:9001` (console) |
| **minio-lb** | `minio-lb` | `9010:9000` (S3 via HAProxy), `8404:8404` (stats) |
| **minio-init** | `minio-init` | — |

`minio-init` creates bucket `hummock001` on startup, then exits.  
HAProxy stats available at http://localhost:8404/stats.

Credentials: user `hummockadmin`, password `hummockadmin`.

### Ports

| Port | Service | Access |
|------|---------|--------|
| `9010` | S3 API (via HAProxy) | http://localhost:9010 |
| `8404` | HAProxy stats | http://localhost:8404/stats |
| `9000` | minio-1 S3 | Direct node access |
| `9001` | minio-1 console | |
| `9002` | minio-2 S3 | Direct node access |
| `9003` | minio-2 console | |
| `9004` | minio-3 S3 | Direct node access |
| `9005` | minio-3 console | |

## Usage

```bash
# Single-node + init container
docker compose -f docker-compose.yml up -d

# 3-node cluster
docker compose -f docker-compose-cluster.yml up -d

# 3-node cluster with HAProxy LB
docker compose -f docker-compose-cluster-lb.yml up -d

# Or with Makefile
make start
```
