# Redpanda Connect

Redpanda broker with Console and Redpanda Connect for stream processing.

## Services

| Service | Container | Image | Port |
|---------|-----------|-------|------|
| redpanda | `redpanda` | `docker.arvancloud.ir/redpandadata/redpanda:latest` | `9644`, `8082` |
| redpanda_console | `redpanda_console` | `docker.arvancloud.ir/redpandadata/console:latest` | `9100:8080` |
| redpanda_connect | `redpanda_connect` | `docker.arvancloud.ir/redpandadata/connect:latest` | — |

## Usage

```bash
docker compose -f docker-compose-full-sigle-node.yml up -d
```

Requires `./connect-config.yaml` for Redpanda Connect pipeline definition and `./data/` for working data.
