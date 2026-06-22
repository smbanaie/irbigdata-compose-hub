# EK (Elasticsearch + Kibana)

Elastic stack with single-node and 3-node cluster variants.

## Variants

| Compose | Topology | Components |
|---------|----------|------------|
| `docker-compose.yml` | Single-node | ES + Kibana |
| `docker-compose-logstash.yml` | Single-node | ES + Logstash + Kibana |
| `docker-compose-cluster.yml` | 3-node cluster | ES (x3) + Kibana + APM Server |

## Cluster variant

The 3-node cluster uses full TLS/mTLS security with auto-generated certificates.

**Requires `cluster.env`** — copy to `.env` or use with `--env-file`:
```bash
cp cluster.env .env
# or
docker compose -f docker-compose-cluster.yml --env-file cluster.env up -d
```
Environment variables:
- `ELASTIC_PASSWORD` / `KIBANA_PASSWORD`
- `STACK_VERSION` (default: `9.1.4`)
- `MEM_LIMIT` (default: `2GB`)
- `CLUSTER_NAME` (default: `Sepahram`)

**Linux prerequisite:** Set `vm.max_map_count`:
```bash
sudo sysctl -w vm.max_map_count=262144
```

```bash
# Start single-node
docker compose -f docker-compose.yml up -d

# Start 3-node cluster
docker compose -f docker-compose-cluster.yml up -d
```

## Access

| Service | URL |
|---------|-----|
| Kibana | http://localhost:5601 |
| ES API | https://localhost:9200 |
| APM Server | http://localhost:8200 |
