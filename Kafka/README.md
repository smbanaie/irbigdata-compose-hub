# Kafka

Apache Kafka 4.2.0 (KRaft mode, no Zookeeper) with management UIs.

## Services

| Service | Container | Image | Port |
|---------|-----------|-------|------|
| **broker** | `kafka-node` | `docker.arvancloud.ir/apache/kafka:4.2.0` | `9092`, `29092`, `9093` |
| **console** | `redpanda-console` | `docker.arvancloud.ir/redpandadata/console:latest` | `9300:8080` |
| **kafkaHQ** | `kafkaHQ` | `docker.arvancloud.ir/tchiotludo/akhq` | `9100:8080` |
| **kafka-ui** | `kafbat-ui` | `docker.arvancloud.ir/kafbat/kafka-ui:latest` | `9200:8080` |

## Usage

```bash
docker compose -f docker-compose.yml up -d
# or
make start
```

## Ports

| Port | Listener | Access |
|------|----------|--------|
| `9092` | EXTERNAL (PLAINTEXT) | Applications on host |
| `29092` | INTERNAL (PLAINTEXT) | Docker network |
| `9093` | CONTROLLER | Internal KRaft quorum |
| `9300` | Redpanda Console | http://localhost:9300 |
| `9100` | KafkaHQ | http://localhost:9100 |
| `9200` | Kafka-UI | http://localhost:9200 |
