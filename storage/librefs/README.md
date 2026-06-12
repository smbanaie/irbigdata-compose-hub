# libreFS

Community-maintained S3-compatible object storage server, forked from MinIO.

> Part of the **storage/** folder — see also [MinIO](../Minio/) and [RustFS](../rustfs/).

**GitHub:** https://github.com/libreFS/libreFS

## Quick Start

```bash
# Clone and build
git clone https://github.com/libreFS/libreFS.git
docker build -t librefs:latest libreFS/Dockerfile.release

# Run
docker compose -f docker-compose.yml up -d
```

Default credentials: `minioadmin` / `minioadmin`
