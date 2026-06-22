# Data Storage & Databases

**Core data persistence and retrieval solutions**

This category contains **21 projects** focused on database technologies and data storage infrastructure. These solutions provide the foundation for any data engineering pipeline with support for various data types, scaling requirements, and consistency models.

## Key Projects

- **StarRocks** (`Starrocks/`) - High-performance analytical database with columnar storage
- **PostgreSQL** (`Postgres/`) - Advanced, open-source relational database with powerful features
- **MariaDB** (`Mariadb/`) - Drop-in replacement for MySQL with enhanced performance
- **ClickHouse** (`ClickHouse/`) - Column-oriented database for real-time analytics
- **MongoDB** (`mongo/`) - Document-oriented NoSQL database for flexible schemas
- **Redis** (`Rredis/`) - In-memory data structure store for caching and sessions

## Usage Examples

```bash
# Start PostgreSQL
docker compose -f Postgres/docker-compose.yml up -d

# Start MongoDB
docker compose -f mongo/docker-compose.yml up -d

# Start ClickHouse for analytics
docker compose -f ClickHouse/docker-compose.yml up -d
```

## Configuration

Each database project includes:
- Optimized container configuration for production use
- Port mappings for external access
- Data persistence through volume mounts
- Common management utilities via Makefile

## Integration

These databases can be combined with other categories:
- Connect to **Data Processing & Streaming** projects (e.g., Spark, Kafka)
- Integrate with **Observability & Monitoring** (Grafana dashboards, Prometheus metrics)
- Work with **Data Lakes & Integration** (Airflow, LakeFS)

## Key Features

- ✅ ACID compliance (PostgreSQL, MariaDB, ClickHouse)
- ✅ Horizontal and vertical scaling
- ✅ High availability configurations
- ✅ Backup and disaster recovery
- ✅ Monitoring and alerting capabilities