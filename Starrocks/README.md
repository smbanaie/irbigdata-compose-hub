# StarRocks

StarRocks v4 cluster in shared-data mode with 3 MinIO nodes, 3 FE (Frontend) nodes, and 3 CN (Compute Node) nodes.

## Architecture

| Layer | Nodes | IPs | Ports (host:container) |
|-------|-------|-----|----------------------|
| **MinIO** | minio1, minio2, minio3 | `.10–.12` | `9000:9000`, `9001–9003:9001` |
| **FE** | fe1 (leader), fe2, fe3 (followers) | `.20–.22` | `8031–8033:8030`, `9021–9023:9020`, `9031–9033:9030` |
| **CN** | cn1, cn2, cn3 | `.30–.32` | `8041–8043:8040`, `9051–9053:9050` |

- Network: `starrocks-net` (bridge, `172.20.0.0/16`)
- Run mode: `shared_data` (S3-backed via MinIO)
- MinIO credentials: `minioadmin` / `minioadmin123`

## Usage

```bash
# Automated setup (recommended)
chmod +x setup.sh
./setup.sh

# Or step by step
docker compose -f docker-compose.yml up -d minio1 minio2 minio3
docker compose -f docker-compose.yml up -d fe1
docker compose -f docker-compose.yml up -d fe2 fe3
docker compose -f docker-compose.yml up -d cn1 cn2 cn3

# Add FE followers
docker exec starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root \
  -e "ALTER SYSTEM ADD FOLLOWER 'fe2:9010';"
docker exec starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root \
  -e "ALTER SYSTEM ADD FOLLOWER 'fe3:9010';"

# Add compute nodes
docker exec starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root \
  -e "ALTER SYSTEM ADD COMPUTE NODE 'cn1:9050';"
docker exec starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root \
  -e "ALTER SYSTEM ADD COMPUTE NODE 'cn2:9050';"
docker exec starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root \
  -e "ALTER SYSTEM ADD COMPUTE NODE 'cn3:9050';"

# Create default storage volume
docker exec -i starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root << 'EOF'
CREATE STORAGE VOLUME IF NOT EXISTS default_storage_volume
TYPE = S3
LOCATIONS = ('s3://starrocks/')
PROPERTIES (
    "enabled" = "true",
    "aws.s3.region" = "us-east-1",
    "aws.s3.endpoint" = "http://minio1:9000",
    "aws.s3.use_instance_profile" = "false",
    "aws.s3.use_aws_sdk_default_behavior" = "false"
);
SET default_storage_volume = default_storage_volume;
EOF
```

## Config files (`config/`)

| File | Purpose |
|------|---------|
| `fe1.conf`, `fe2.conf`, `fe3.conf` | Frontend node configs |
| `cn1.conf`, `cn2.conf`, `cn3.conf` | Compute node configs |

Each config mounts as read-only into the container's `conf/` directory.

## Kafka Connectivity

See `kafka-network-settings.yaml` for connecting StarRocks to Kafka — covers `extra_hosts`, shared Docker networks, remote brokers, and SSL auth.

## Port Reference

| Port | Service |
|------|---------|
| `9000` | MinIO S3 API |
| `9001–9003` | MinIO Console (per node) |
| `8031–8033` | FE HTTP (web UI) |
| `9021–9023` | FE RPC |
| `9031–9033` | FE MySQL query |
| `8041–8043` | CN HTTP |
| `9051–9053` | CN heartbeat |
