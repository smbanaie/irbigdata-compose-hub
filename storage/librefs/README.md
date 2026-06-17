# libreFS

Community-maintained S3-compatible object storage server, forked from MinIO.

> Part of the **storage/** folder — see also [MinIO](../Minio/) and [RustFS](../rustfs/).

**GitHub:** https://github.com/libreFS/libreFS

## Build & Run

A standalone `Dockerfile.librefs` is included — no need to clone the libreFS repo separately.

```bash
# Build the image (downloads libreFS source from GitHub)
docker build -f Dockerfile.librefs -t librefs:local .

# Start the container
docker compose up -d
```

Default credentials: `minioadmin` / `minioadmin`
