# MinIO

Standalone MinIO S3-compatible object storage with client init container.

## Services

| Service | Container | Image | Ports |
|---------|-----------|-------|-------|
| **minio** | `minio` | `docker.arvancloud.ir/minio/minio:latest` | `9000`, `9001` |
| **minio_mc** | — | `docker.arvancloud.ir/minio/mc:latest` | — |

`minio_mc` is a short-lived init container that creates a service account access key pair on startup, then exits.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `sepahram` | Network name suffix |

Hardcoded credentials: user `miniouser`, password `miniopassword`.  
Service account created by `minio_mc`: access key `AAAAAAAAAAAAAAAAAAAA`, secret key `BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB`.

## Ports

| Port | Service | Access |
|------|---------|--------|
| `9000` | S3 API | http://localhost:9000 |
| `9001` | Console UI | http://localhost:9001 |

## Usage

```bash
docker compose -f docker-compose.yml up -d

# Or with Makefile
make start
```

## Volumes

Data is stored inside the container at `/minio_data` (no named volume — use a bind mount for persistence).
