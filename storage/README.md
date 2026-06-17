# Storage

S3-compatible object storage servers for development and testing.

## Contents

| Project | Folder | Compose | GitHub |
|---------|--------|---------|--------|
| **MinIO** | `Minio/` | `docker-compose.yml` (3 variants) | https://github.com/minio/minio |
| **RustFS** | `rustfs/` | `docker-compose.yml` | https://github.com/rustfs/rustfs |
| **libreFS** | `librefs/` | `docker-compose.yml` + `Dockerfile.librefs` (build from source) | https://github.com/libreFS/libreFS |
| **SeaweedFS** | `SeaweedFS/` | `docker-compose.yml` (3-node cluster with healthchecks) | https://github.com/seaweedfs/seaweedfs |

## Quick Start

```bash
# MinIO single-node
docker compose -f Minio/docker-compose.yml up -d

# RustFS single-node
docker compose -f rustfs/docker-compose.yml up -d

# RustFS 3-node cluster
docker compose -f rustfs/docker-compose-rustfs.yml up -d

# SeaweedFS 3-node cluster
cd SeaweedFS && mkdir -p data-volume{1,2,3} && docker compose up -d

# libreFS (build image first)
cd librefs
docker build -f Dockerfile.librefs -t librefs:local .
docker compose up -d
```

Each project has its own README with credentials, ports, and configuration details.