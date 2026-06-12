# Storage

S3-compatible object storage servers for development and testing.

## Contents

| Project | Folder | Compose | GitHub |
|---------|--------|---------|--------|
| **MinIO** | `Minio/` | `docker-compose.yml` (3 variants) | https://github.com/minio/minio |
| **RustFS** | `rustfs/` | `docker-compose.yml` | https://github.com/rustfs/rustfs |
| **libreFS** | `librefs/` | `docker-compose.yml` (WIP) | https://github.com/libreFS/libreFS |

## Quick Start

```bash
# MinIO single-node
docker compose -f Minio/docker-compose.yml up -d

# RustFS
docker compose -f rustfs/docker-compose.yml up -d
```

Each project has its own README with credentials, ports, and configuration details.