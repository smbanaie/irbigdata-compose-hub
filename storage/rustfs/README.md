# RustFS

S3-compatible object storage server written in Rust.

> Part of the **storage/** folder — see also [MinIO](../Minio/) and [libreFS](../librefs/).

## Services

| Service | Container | Image | Ports |
|---------|-----------|-------|-------|
| **rustfs** | `rustfs` | `docker.arvancloud.ir/rustfs/rustfs:latest` | `9000`, `9001` |
| **volume-permission-helper** | `volume-permission-helper` | `docker.arvancloud.ir/library/alpine` | — |

`volume-permission-helper` is a one-time init container that sets correct ownership on data volumes before RustFS starts.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `sepahram` | Network name suffix |

Hardcoded credentials: access key `admin`, secret key `admin`.

## Ports

| Port | Service | Access |
|------|---------|--------|
| `9000` | S3 API | http://localhost:9000 |
| `9001` | Console UI | http://localhost:9001 |

## Usage

```bash
docker compose -f docker-compose.yml up -d
```

## Volumes

| Volume | Path (container) | Purpose |
|--------|------------------|---------|
| `rustfs_data_{0..3}` | `/data/rustfs{0..3}` | Data storage (4 volumes) |
| `logs` | `/app/logs` | Application logs |
