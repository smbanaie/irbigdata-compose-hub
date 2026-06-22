# Kafka

Apache Kafka 4.2.0 (KRaft mode, no Zookeeper). Two compose variants:

- **`docker-compose.yml`** — single-node (combined controller+broker) with management UIs
- **`docker-compose-cluster.yml`** — multi-node cluster (3 controllers + 3 brokers)

## Single-node (`docker-compose.yml`)

### Services

| Service | Container | Image | Port |
|---------|-----------|-------|------|
| **broker** | `kafka-node` | `docker.arvancloud.ir/apache/kafka:4.2.0` | `9092`, `29092`, `9093` |
| **console** | `redpanda-console` | `docker.arvancloud.ir/redpandadata/console:latest` | `9300:8080` |
| **kafkaHQ** | `kafkaHQ` | `docker.arvancloud.ir/tchiotludo/akhq` | `9100:8080` |
| **kafka-ui** | `kafbat-ui` | `docker.arvancloud.ir/kafbat/kafka-ui:latest` | `9200:8080` |

### Ports

| Port | Listener | Access |
|------|----------|--------|
| `9092` | EXTERNAL (PLAINTEXT) | Applications on host |
| `29092` | INTERNAL (PLAINTEXT) | Docker network |
| `9093` | CONTROLLER | Internal KRaft quorum |
| `9300` | Redpanda Console | http://localhost:9300 |
| `9100` | KafkaHQ | http://localhost:9100 |
| `9200` | Kafka-UI | http://localhost:9200 |

## Cluster (`docker-compose-cluster.yml`)

3 dedicated controllers + 3 brokers with separate KRaft roles.

### Services

| Service | Container | Internal ports | External port |
|---------|-----------|----------------|---------------|
| **controller-1** | `controller-1` | `9093` | — |
| **controller-2** | `controller-2` | `9093` | — |
| **controller-3** | `controller-3` | `9093` | — |
| **broker-1** | `broker-1` | `19092` (INTERNAL), `9092` (EXTERNAL) | `29092` |
| **broker-2** | `broker-2` | `19092` (INTERNAL), `9092` (EXTERNAL) | `39092` |
| **broker-3** | `broker-3` | `19092` (INTERNAL), `9092` (EXTERNAL) | `49092` |

### Ports

| Port | Broker | Access |
|------|--------|--------|
| `29092` | broker-1 | Applications on host |
| `39092` | broker-2 | Applications on host |
| `49092` | broker-3 | Applications on host |

## Usage

```bash
# Single-node with UIs
docker compose -f docker-compose.yml up -d

# Multi-node cluster
docker compose -f docker-compose-cluster.yml up -d

# Or with Makefile
make start
```
