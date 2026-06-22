# Sairo - Universal S3 Object Browser

Sairo is a **universal S3 object browser** that provides a web-based interface to search and browse S3-compatible storage. It runs as a single Docker container with no external dependencies.

## Overview

Sairo quickly indexes S3-compatible buckets and provides a powerful search and browsing interface. It supports AWS S3, MinIO, Cloudflare R2, Wasabi, Backblaze B2, Ceph, and more S3-compatible endpoints.

## Features

- 🔍 **Advanced Search** - Search across all objects with powerful filtering
- 📂 **Bucket Browsing** - Navigate through S3 buckets and folders
- ⚡ **Fast Indexing** - Starts indexing immediately on startup
- 🔐 **Secure Authentication** - Admin authentication with strong password
- 📊 **Real-time Updates** - Search results improve as indexing progresses
- 🎨 **Clean UI** - Modern, user-friendly interface

## Prerequisites

- Docker Engine 20.10+ installed and running

## S3 Credentials

You need:
- S3-compatible endpoint URL
- Access key
- Secret key

Works with:
- AWS S3
- MinIO
- Cloudflare R2
- Wasabi
- Backblaze B2
- Ceph
- And more!

## Quickstart

### Docker Run (Recommended)

The fastest way to get started:

```bash
docker run -d --name sairo -p 8000:8000 \
  -e S3_ENDPOINT=https://your-s3-endpoint.com \
  -e S3_ACCESS_KEY=your-access-key \
  -e S3_SECRET_KEY=your-secret-key \
  -e ADMIN_PASS=choose-a-strong-password \
  -e JWT_SECRET=$(openssl rand -hex 32) \
  -v sairo-data:/data \
  stephenjr002/sairo:latest
```

Replace the placeholder values with your actual S3 credentials.

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  sairo:
    image: stephenjr002/sairo:latest
    container_name: sairo
    ports:
      - "8000:8000"
    environment:
      S3_ENDPOINT: "https://your-s3-endpoint.com"
      S3_ACCESS_KEY: "your-access-key"
      S3_SECRET_KEY: "your-secret-key"
      ADMIN_PASS: "choose-a-strong-password"
      JWT_SECRET: "$(openssl rand -hex 32)"
      SECURE_COOKIE: "false"
    volumes:
      - sairo-data:/data
    networks:
      - sairo-net

networks:
  sairo-net:
    driver: bridge

volumes:
  sairo-data:
```

Then start:

```bash
docker compose up -d
```

## Usage

### Open the UI

Navigate to `http://localhost:8000` in your browser.

### Sign In

Use the default admin credentials:

| Field | Value |
|-------|-------|
| Username | `admin` |
| Password | The `ADMIN_PASS` value you set above |

### Running without HTTPS?

If you are running over plain HTTP (no TLS), add `-e SECURE_COOKIE=false` to your Docker command. Without this, authentication cookies will silently fail.

See the Configuration reference for details.

## Important Notes

- **Initial Indexing**: Sairo starts indexing your buckets immediately on startup. Depending on your object count, the initial crawl may take from a few seconds to a few minutes.
- **UI Availability**: The UI is usable right away — search results improve as indexing progresses.
- **Data Persistence**: The `sairo-data` volume persists your indexed data across container restarts.

## Configuration

Refer to the official Sairo documentation for advanced configuration options, including:

- Custom authentication
- Advanced search settings
- Indexing behavior
- Security configurations

## Integration

Sairo integrates well with your data infrastructure:

- Connect to **Data Storage & Databases** buckets
- Browse **Data Lakes & Integration** object stores
- Monitor **Data Processing & Streaming** data streams
- Visualize **Observability & Monitoring** logs and metrics stored in S3

## Stopping

```bash
docker compose down
```

## Learn More

- [Sairo GitHub Repository](https://github.com/stephenjr002/sairo)
- [Sairo Documentation](https://docs.sairo.dev)

## Alternatives

If Sairo doesn't meet your needs, consider:

- **MinIO Console** (`Data-Lakes-Integration/Minio/`)
- **LakeFS UI** (`Data-Lakes-Integration/LakeFS/`)  
- **RustFS Console** (`Data-Lakes-Integration/RustFS/`)
