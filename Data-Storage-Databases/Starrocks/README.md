# StarRocks 4.0.5 Production Cluster

Production-ready StarRocks cluster with embedded 3-node MinIO + HAProxy load balancer.

## Architecture

- **3 FE nodes**: SQL parsing, query planning, metadata management
- **3 CN nodes**: Distributed query execution
- **HAProxy (FE)**: Load balancing for SQL queries
- **3-node MinIO cluster + HAProxy LB**: S3-compatible object storage
- **Monitoring**: Prometheus + Grafana

## Quick Start

```bash
docker compose -f docker-compose.yml up -d

# Wait for initialization (2-3 min)
docker compose logs -f starrocks-init

# Verify
mysql -h localhost -P 9031 -u root
```

## Access Points

| Service | URL | Description |
|---------|-----|-------------|
| StarRocks SQL | `localhost:9031` | Load-balanced SQL queries |
| StarRocks Web UI | `localhost:8031` | Cluster management |
| MinIO S3 (via LB) | `localhost:9100` | S3-compatible API |
| MinIO Console | `localhost:9001` | Object storage UI (minio-1) |
| Prometheus | `localhost:9501` | Metrics |
| Grafana | `localhost:3002` | Dashboards (admin/admin123) |
| HAProxy Stats | `localhost:8404/stats` | Load balancer stats |

## MinIO Integration

- **Internal endpoint**: `minio-lb:9000`
- **External endpoint**: `localhost:9100`
- **Bucket**: `starrocks`
- **Credentials**: `hummockadmin` / `hummockadmin`
- **Region**: `us-east-1`

## Services

| Service | Container | Ports |
|---------|-----------|-------|
| **minio-1** | `minio-1` | `9000:9000`, `9001:9001` |
| **minio-2** | `minio-2` | `9002:9000`, `9003:9001` |
| **minio-3** | `minio-3` | `9004:9000`, `9005:9001` |
| **minio-lb** | `minio-lb` | `9100:9000`, `8404:8404` |
| **starrocks-fe-1** | `starrocks-fe-1` | `8030:8030`, `9030:9030` |
| **starrocks-fe-2** | `starrocks-fe-2` | `8032:8030`, `9032:9030` |
| **starrocks-fe-3** | `starrocks-fe-3` | `8033:8030`, `9033:9030` |
| **haproxy-fe** | `haproxy-fe` | `9031:9030`, `8031:8030` |
| **starrocks-cn-{1..3}** | `starrocks-cn-{1..3}` | `8040-8042:8040` |
| **prometheus-starrocks** | `prometheus-starrocks` | `9501:9090` |
| **grafana-starrocks** | `grafana-starrocks` | `3002:3000` |
| **starrocks-init** | `starrocks-init` | — (one-time init) |

## Configuration

FE config is generated inline in the compose file via shell commands appended to `fe.conf`. Key settings:

- `run_mode = shared_data`
- `cloud_native_storage_type = S3`
- `aws_s3_endpoint = minio-lb:9000`
