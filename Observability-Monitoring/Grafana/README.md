# Grafana

Grafana observability stacks with Prometheus, Loki, Postgres monitoring, and microservices demo.

## Variants

| Folder | Compose | Description |
|--------|---------|-------------|
| **Step1-Observability** | `docker-compose.yml` | Prometheus + Loki + Promtail + Grafana + Custom app + TNS-DB |
| **Step2-Postgres-Monitoring** | `docker-compose.yml` | Grafana + Prometheus + PostgreSQL + Postgres-Exporter |
| **Step3-Microservices** | `docker-compose.yaml` | Prometheus + Grafana + cAdvisor + HAProxy + 2 sample microservices |

## Step1-Observability

Full observability stack with logs (Loki), metrics (Prometheus), and dashboards (Grafana).

### Services

| Service | Image | Port |
|---------|-------|------|
| prometheus | `docker.arvancloud.ir/prom/prometheus:latest` | `9090` |
| loki | `docker.arvancloud.ir/grafana/loki:latest` | `3100` |
| promtail | `docker.arvancloud.ir/grafana/promtail:latest` | — |
| grafana | `docker.arvancloud.ir/grafana/grafana:latest` | `3000` |
| app | build (`./app`) | `8081:80` |
| db | `docker.arvancloud.ir/grafana/tns-db:latest` | `8082:80` |

Grafana is pre-configured with anonymous admin access and auto-provisioned datasources/dashboards.

## Step2-Postgres-Monitoring

PostgreSQL monitoring with Prometheus scraping via postgres-exporter.

### Services

| Service | Image | Port |
|---------|-------|------|
| grafana | `docker.arvancloud.ir/grafana/grafana:11.0.0` | `3000` |
| prometheus | `docker.arvancloud.ir/prom/prometheus:v2.49.0` | `9090` |
| postgres | `docker.arvancloud.ir/library/postgres:16-alpine` | `5432` |
| postgres-exporter | `quay.io/prometheuscommunity/postgres-exporter` | `9187` |

Grafana with pre-installed plugins (clock, piechart, gantt, worldmap, gauge, plotly).

## Step3-Microservices

Microservices monitoring demo with HAProxy load balancer and cAdvisor.

### Services

| Service | Image | Port |
|---------|-------|------|
| prometheus | `docker.arvancloud.ir/prom/prometheus:v2.49.0` | `9090` |
| grafana | `docker.arvancloud.ir/grafana/grafana:11.0.0` | `3000` |
| cadvisor | `docker.arvancloud.ir/google/cadvisor:latest` | — |
| haproxy | `docker.arvancloud.ir/library/haproxy:latest` | `11000` |
| haproxy-exporter | `docker.arvancloud.ir/prom/haproxy-exporter` | — |
| svc-greeter | `docker.arvancloud.ir/spaceuptech/greeter` | — |
| svc-math | `docker.arvancloud.ir/spaceuptech/basic-service` | — |

## Usage

```bash
# Pick a variant
cd Step1-Observability
docker compose up -d
```
