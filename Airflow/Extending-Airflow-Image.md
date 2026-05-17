# Extending Docker Image

The Airflow setup uses a custom `Dockerfile` that extends the official image with Iran-friendly mirrors, timezone, and additional Python packages.

## Dockerfile

`Dockerfile` at the root of the Airflow folder:

```dockerfile
FROM docker.arvancloud.ir/apache/airflow:3.2.1
USER root
RUN echo "deb http://mirror.arvancloud.ir/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://mirror.arvancloud.ir/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && ln -fs /usr/share/zoneinfo/Asia/Tehran /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
USER airflow
RUN pip install --trusted-host mirror-pypi.runflare.com \
    -i https://mirror-pypi.runflare.com/simple/ \
    --no-cache-dir pandas jdatetime openpyxl faker
```

## Build

`docker-compose.yml` has `build: .` so `docker compose up` builds automatically. To build manually:

```bash
docker build -t my-airflow:3.2.1 .
```

Then set in `.env`:

```bash
AIRFLOW_IMAGE_NAME=my-airflow:3.2.1
```

## Customisation

Edit the `Dockerfile` to add more system packages (via `apt-get`) or Python packages (via `pip`). Rebuild and restart:

```bash
docker compose build
docker compose up -d
```
