# MinIO

Standalone MinIO S3-compatible object storage.

## Services

| Service | Container | Image | Ports |
|---------|-----------|-------|-------|
| **minio** | `minio` | `docker.arvancloud.ir/minio/minio:latest` | `9000`, `9001` |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `sepahram` | Network name suffix |

Credentials are hardcoded: user `sepahram`, password `sepahram`.

## Ports

| Port | Service | Access |
|------|---------|--------|
| `9000` | S3 API | http://localhost:9000 |
| `9001` | Console UI | http://localhost:9001 |

## Usage

```bash
# Start MinIO (uses --profile minio)
docker compose -f docker-compose.yml --profile minio up -d

# Or with Makefile
make start
```

## Volumes

| Volume | Path (container) | Purpose |
|--------|------------------|---------|
| `minio-data` (named) | `/data` | Object storage data |
