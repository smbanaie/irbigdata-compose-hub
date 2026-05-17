# Redpanda

Kafka-compatible event streaming platform with management UIs.

## Services

| Service | Container | Image | Port |
|---------|-----------|-------|------|
| **redpanda** | `redpanda` | `docker.arvancloud.ir/redpandadata/redpanda:latest` | `9092:9092`, `29092:29092` |
| **console** | `redpanda-console` | `docker.arvancloud.ir/redpandadata/console:latest` | `9300:8080` |
| **kafkaHQ** | `kafkaHQ` | `docker.arvancloud.ir/tchiotludo/akhq` | `9100:8080` |
| **kafka-ui** | `kafka-ui` | `docker.arvancloud.ir/kafbat/kafka-ui:latest` | `9200:8080` |

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `sepahram` | Network name suffix |

## Usage

```bash
# Start Redpanda + all management UIs
docker compose -f docker-compose.yml up -d

# Or with Makefile
make start
```

## Ports

| Port | Service | Access |
|------|---------|--------|
| `9092` | Kafka API (external) | Applications |
| `29092` | Kafka API (internal) | Docker network |
| `9300` | Redpanda Console | http://localhost:9300 |
| `9100` | KafkaHQ | http://localhost:9100 |
| `9200` | Kafka-UI | http://localhost:9200 |
