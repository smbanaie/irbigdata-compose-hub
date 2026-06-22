- - # RisingWave High Availability Cluster Setup

    This is a production-ready RisingWave HA cluster with proper load balancing and fault tolerance.

    ## Architecture Overview

    ### Components

    1. **PostgreSQL HA** (Primary + Replica with HAProxy)
       - Primary: Port 5432
       - Replica: Port 5433
       - HAProxy Proxy: Port 5430 (write: 5432, read: 5433)
       - Stats: Port 7000
    2. **RisingWave Cluster**
       - 2x Meta Nodes (metadata management)
       - 2x Compute Nodes (query processing)
       - 2x Frontend Nodes (client connections)
       - 2x Compactor Nodes (data compaction)
    3. **HAProxy Load Balancer**
       - RisingWave frontend load balancer: Port 4566
       - PostgreSQL proxy (writes): Port 5430
       - PostgreSQL proxy (reads): Port 5433
       - HAProxy stats: Port 7000
    4. **Storage & Messaging**
       - MinIO (S3-compatible): Ports 9000 (API), 9001 (Console)
       - Redpanda (Kafka): Ports 9092, 9644
    5. **Monitoring**
       - Prometheus: Port 9090
       - Grafana: Port 3000
    6. **Analytics & BI**
       - Apache Superset: Port 8088 (data visualization on RisingWave)
    7. **Management Consoles**
       - RisingWave Console: Port 8020 (cluster management)
       - Redpanda Console: Port 8080 (Kafka management)
       - MinIO Console: Port 9001 (storage management)
  
    ## Directory Structure

    ```
    risingwave-ha/
    ├── docker-compose.yml (or compose-cluster.yml)
    ├── risingwave.toml
    ├── haproxy.cfg                    # Combined load balancer (PostgreSQL + RisingWave)
    ├── pg_hba.conf                    # PostgreSQL authentication config
    ├── prometheus.yaml
    ├── northwind.sql                  # Sample data
    ├── dev/
    │   └── init.yaml                  # RisingWave console initialization
    ├── grafana/
    │   ├── grafana.ini
    │   └── provisioning/
    │       └── datasources/
    │           └── prometheus.yml
    └── dashboards/                    # Grafana dashboards
        ├── risingwave-dev-dashboard.json
        └── risingwave-user-dashboard.json
    ```
  
    ## Prerequisites
  
    - Docker Engine 20.10+
    - Docker Compose 2.0+
    - At least 32GB RAM
    - 100GB available disk space

    ## Quick Start

    ### 1. Create Directory Structure
  
    ```bash
    mkdir -p risingwave-ha/{grafana/provisioning/datasources,dashboards,dev}
    cd risingwave-ha
    ```

    ### 2. Create Required Files

    Save the provided files with these exact names:

    - `docker-compose.yml` (or `compose-cluster.yml` if you prefer)
    - `risingwave.toml` (RisingWave cluster configuration)
    - `haproxy.cfg` (Combined load balancer for PostgreSQL and RisingWave)
    - `pg_hba.conf` (PostgreSQL authentication configuration)
    - `prometheus.yaml` (monitoring configuration)
    - `risingwave.toml` (RisingWave cluster configuration)
    - `northwind.sql` (optional sample data)
  
    **Important**: Make sure all files are in the same directory as your docker-compose file.
  
    ### 3. Create Grafana Datasource Configuration
  
    Create `grafana/provisioning/datasources/prometheus.yml`:
  
    ```yaml
    apiVersion: 1
    
    datasources:
      - name: Prometheus
        type: prometheus
        access: proxy
        url: http://prometheus:9090
        isDefault: true
        editable: true
    ```
  
    ### 4. Create Grafana Configuration
  
    Create `grafana/grafana.ini`:
  
    ```ini
    [server]
    http_port = 3000
    domain = localhost
    
    [security]
    admin_user = admin
    admin_password = admin
    
    [paths]
    provisioning = /etc/grafana/provisioning
    ```
  
    ### 5. Start the Cluster
  
    ```bash
    # If your file is named docker-compose.yml:
    docker-compose up -d
    
    # If your file is named compose-cluster.yml:
    docker-compose -f compose-cluster.yml up -d
    
    # Check service health
    docker-compose ps
    
    # View logs (use -f flag if using compose-cluster.yml)
    docker-compose logs -f
    ```
  
    **Troubleshooting startup issues:**

    ```bash
    # If you get "depends on undefined service" errors:
    # Make sure all service names match in your compose file

    # If you get variable warning for CONSOLE_CONFIG_FILE:
    # This is just a warning and can be ignored - it's used by redpanda-console

    # Check which services are unhealthy:
    docker-compose ps | grep -v "healthy"

    # View specific service logs:
    docker-compose logs service-name
    ```

    ## PostgreSQL Configuration & Testing

    ### Production PostgreSQL Architecture

    This cluster uses a **production-ready PostgreSQL setup** with separate services for replica initialization:

    #### Services:
    - **`postgres-primary`**: Main PostgreSQL server (writes)
    - **`postgres-replica-setup`**: One-time replica data initialization
    - **`postgres-replica`**: PostgreSQL replica (reads, persistent data)

    #### Architecture Benefits:
    - **Persistent replica data**: Survives container restarts
    - **One-time setup**: No rebuilding on every restart
    - **Production security**: Proper authentication and permissions
    - **Clean separation**: Setup logic isolated from runtime

    ### PostgreSQL Setup Steps

    #### 1. Initial Replica Setup (One-time)

    ```bash
    # Start only the replica setup service
    docker compose -f compose-cluster.yml up postgres-replica-setup

    # Wait for completion - you'll see:
    # postgres-replica-setup | Replication setup complete
    # postgres-replica-setup exited with code 0
    ```

    **What happens during setup:**
    - Creates replica data directory structure
    - Sets proper file permissions (postgres:postgres, 0700)
    - Runs `pg_basebackup` to copy data from primary
    - Configures streaming replication

    #### 2. Start Full Cluster

    ```bash
    # Start the complete cluster
    docker compose -f compose-cluster.yml up -d

    # Or start specific services
    docker compose -f compose-cluster.yml up postgres-primary postgres-replica
    ```

    #### 3. Verify PostgreSQL Health

    ```bash
    # Check all services are healthy
    docker compose ps

    # Should show:
    # postgres-primary    Up (healthy)    0.0.0.0:5432->5432/tcp
    # postgres-replica    Up (healthy)    0.0.0.0:5433->5432/tcp
    ```

    #### 4. Test Replication

    ```bash
    # Test primary connection
    docker exec postgres-primary psql -U postgres -d metadata -c "SELECT pg_is_in_recovery();"
    # Should return: f (false - primary is not in recovery)

    # Test replica connection
    docker exec postgres-replica psql -U postgres -d metadata -c "SELECT pg_is_in_recovery();"
    # Should return: t (true - replica is in recovery)

    # Test replication status
    docker exec postgres-primary psql -U postgres -c "SELECT * FROM pg_stat_replication;"
    # Should show replica streaming connection
    ```

    #### 5. Test Load Balancing

    ```bash
    # Test PostgreSQL HAProxy (writes go to primary, reads can use replica)
    psql -h localhost -p 5430 -U postgres -d metadata -c "SELECT 1"

    # Test direct connections
    psql -h localhost -p 5432 -U postgres -d metadata -c "SELECT 1"  # Primary
    psql -h localhost -p 5433 -U postgres -d metadata -c "SELECT 1"  # Replica (read-only)
    ```

    ### PostgreSQL Troubleshooting

    #### Common Issues:

    **Replica setup fails:**
    ```bash
    # Clean and retry setup
    docker compose down -v
    docker compose up postgres-replica-setup
    ```

    **Permission errors:**
    ```bash
    # Check file permissions
    docker exec postgres-replica ls -la /var/lib/postgresql/18/data/pgdata/
    # Should show postgres:postgres ownership
    ```

    **Replication not working:**
    ```bash
    # Check replica logs
    docker compose logs postgres-replica

    # Check primary replication status
    docker exec postgres-primary psql -U postgres -c "SELECT * FROM pg_stat_replication;"

    # Check replica recovery status
    docker exec postgres-replica psql -U postgres -c "SELECT pg_is_in_recovery(), pg_last_wal_receive_lsn(), pg_last_wal_replay_lsn();"
    ```

    **Connection refused:**
    ```bash
    # Test basic connectivity
    docker exec postgres-primary psql -U postgres -c "SELECT version();"
    docker exec postgres-replica psql -U postgres -c "SELECT version();"

    # Check HAProxy stats
    curl http://localhost:7000/stats
    ```

    #### PostgreSQL Security Features:

    - **Custom pg_hba.conf**: Allows specific network access patterns
    - **User isolation**: PostgreSQL runs as dedicated postgres user
    - **Replication authentication**: Secure WAL streaming
    - **Network restrictions**: No external access without explicit configuration

    ### Production PostgreSQL Operations

    #### Restarting Services:

    ```bash
    # Restart replica (data persists)
    docker compose restart postgres-replica

    # Restart primary (requires replica reinitialization)
    docker compose restart postgres-primary
    # Note: Primary restart requires re-running postgres-replica-setup
    ```

    #### Backup & Recovery:

    ```bash
    # Backup primary metadata
    docker exec postgres-primary pg_dump -U postgres metadata > backup_$(date +%Y%m%d).sql

    # Restore backup
    docker exec -i postgres-primary psql -U postgres metadata < backup_20241201.sql
    ```

    #### Monitoring PostgreSQL:

    ```bash
    # Check replication lag
    docker exec postgres-primary psql -U postgres -c "
      SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn
      FROM pg_stat_replication;"

    # Check WAL receiver status (on replica)
    docker exec postgres-replica psql -U postgres -c "SELECT * FROM pg_stat_wal_receiver;"

    # Check PostgreSQL logs
    docker compose logs postgres-primary
    docker compose logs postgres-replica
    ```

    ## Accessing Services

    | Service                      | URL                           | Credentials       |
    | ---------------------------- | ----------------------------- | ----------------- |
    | **RisingWave** (via HAProxy) | `postgresql://localhost:4566` | -                 |
    | **RisingWave Console**       | http://localhost:8020         | root/123456       |
    | Frontend Node 0 (direct)     | `postgresql://localhost:4566` | -                 |
    | Frontend Node 1 (direct)     | `postgresql://localhost:4566` | -                 |
    | PostgreSQL Primary           | `postgresql://localhost:5432` | postgres/postgres |
    | PostgreSQL Replica           | `postgresql://localhost:5433` | postgres/postgres |
    | PostgreSQL Proxy (writes)    | `postgresql://localhost:5430` | postgres/postgres |
    | PostgreSQL Proxy (reads)     | `postgresql://localhost:5433` | postgres/postgres |
    | HAProxy Stats                | http://localhost:7000/stats   | -                 |
    | rustfs Console               | http://localhost:9001         | admin/admin       |
    | Meta Dashboard               | http://localhost:5691         | -                 |
    | Prometheus                   | http://localhost:9090         | -                 |
    | Grafana                      | http://localhost:3000         | admin/admin       |
    | Apache Superset              | http://localhost:8088         | admin/admin       |
    | Redpanda Console             | http://localhost:8080         | -                 |
    | Frontend Stats               | http://localhost:8404/stats   | -                 |
  
    ## Connecting to RisingWave
  
    ### Using psql

    ```bash
    # Via load balancer (recommended)
    psql -h localhost -p 4566 -U root -d dev

    # Direct to frontend nodes (both use same port through HAProxy)
    psql -h localhost -p 4566 -U root -d dev  # Frontend 0 (via HAProxy)
    psql -h localhost -p 4566 -U root -d dev  # Frontend 1 (via HAProxy)
    ```
  
    ### Connection String
  
    ```
    postgresql://root@localhost:4566/dev
    ```
  
    ## High Availability Features
  
    ### 1. PostgreSQL Replication
  
    - **Primary node** handles all writes
    - **Replica node** provides read redundancy
    - **HAProxy** routes writes to primary, reads can use replica
    - Automatic health checking and failover detection
  
    ### 2. RisingWave Component Redundancy
  
    - **2 Meta nodes**: Leader election for metadata management
    - **2 Compute nodes**: Distributed query processing
    - **2 Frontend nodes**: Load balanced client connections
    - **2 Compactor nodes**: Parallel data compaction
  
    ### 3. Load Balancing

    - **HAProxy for RisingWave**: Distributes SQL queries across frontend-node-0 and frontend-node-1
    - **HAProxy for PostgreSQL**: Routes writes to primary, reads to replica with primary fallback
    - Round-robin load balancing with automatic health checking
    - Combined stats dashboard on port 7000
  
    ### 4. Storage Reliability
  
    - rustfs with multiple data volumes
    - S3-compatible object storage
    - Data replication across volumes
  
    ## Testing High Availability
  
    ### 1. Test Frontend Failover
  
    ```bash
    # Check current connection
    psql -h localhost -p 4566 -U root -d dev -c "SELECT 1"
    
    # Stop one frontend node
    docker stop frontend-node-0
    
    # Connection should still work through frontend-node-1
    psql -h localhost -p 4566 -U root -d dev -c "SELECT 1"
    
    # Restart the node
    docker start frontend-node-0
    ```
  
    ### 2. Test Meta Node Failover
  
    ```bash
    # Stop one meta node
    docker stop meta-node-0
    
    # Cluster should continue operating
    psql -h localhost -p 4566 -U root -d dev -c "CREATE TABLE test(id INT)"
    
    # Restart
    docker start meta-node-0
    ```
  
    ### 3. Monitor Load Distribution

    ```bash
    # Check combined HAProxy stats (both PostgreSQL and RisingWave)
    curl http://localhost:7000/stats

    # Check frontend node stats directly
    curl http://localhost:8404/stats

    # Or visit in browser
    open http://localhost:7000/stats  # Main HAProxy stats
    open http://localhost:8404/stats  # Frontend node stats
    ```
  
    ## Monitoring
  
    ### Prometheus Queries
  
    ```promql
    # Check all RisingWave components status
    up{job=~"risingwave-.*"}
    
    # Frontend request rate
    rate(frontend_request_total[5m])
    
    # Compute node CPU usage
    process_cpu_seconds_total{component="compute"}
    
    # Meta node leader status
    meta_is_leader
    ```
  
    ### Grafana Dashboards
  
    1. Access Grafana: http://localhost:3000
    2. Login: admin/admin
    3. Import RisingWave dashboards from the community
  
    ### RisingWave Console
  
    The RisingWave Console provides a web-based UI for cluster management:
  
    1. **Access**: http://localhost:8020
    2. **Login**: root/123456
    3. **Features**:
       - Cluster overview and health status
       - Query execution and monitoring
       - Table and materialized view management
       - Source and sink configuration
       - Performance metrics and debugging
  
    **Note**: The console connects to the cluster via the PostgreSQL proxy, ensuring HA access to metadata.
  
    ### Apache Superset (Analytics & Dashboards)
  
    Apache Superset is deployed as a separate service in `compose-cluster.yml` for interactive analytics and dashboards on top of RisingWave data:
  
    1. **Access**: http://localhost:8088
    2. **Login** (default): `admin` / `admin` (created by `superset-init.sh` on first start)
    3. **How it is wired in the cluster**:
       - The `superset` service is built from `Dockerfile.superset`, which installs the `sqlalchemy-risingwave` driver and a custom config.
       - A dedicated PostgreSQL database (`superset_meta` and `superset_cache`) is created and initialized by the `superset-db-init` service.
       - Superset connects to RisingWave through the HAProxy frontend (`haproxy:4566` inside the Docker network, exposed as `localhost:4567` on the host) using the RisingWave SQLAlchemy dialect.
    4. **Usage**:
       - Use Superset to build dashboards on RisingWave materialized views such as `vehicle_telemetry_full` (validated telemetry) and `vehicle_telemetry_dlq` (DLQ analytics).
       - For detailed connection and dashboard setup, see `apache-superset-guide.md` in the same directory.
  
    ## Scaling
  
    ### Adding More Compute Nodes
  
    ```yaml
    compute-node-2:
      <<: *image
      command:
        - compute-node
        - "--listen-addr"
        - "0.0.0.0:5688"
        - "--advertise-addr"
        - "compute-node-2:5688"
        - "--prometheus-listener-addr"
        - "0.0.0.0:1222"
        - "--meta-address"
        - "http://meta-node-0:5690,http://meta-node-1:5690"
        - "--config-path"
        - "/risingwave.toml"
      # ... rest of config
    ```
  
    ### Adding More Frontend Nodes

    1. Add new frontend node to `docker-compose.yml`
    2. Update the `risingwave_frontend_backend` section in `haproxy.cfg`:

    ```conf
    # In the risingwave_frontend_backend section, add:
    server frontend-node-2 frontend-node-2:4566 check inter 3s fall 3 rise 2
    ```
  
    ## Maintenance
  
    ### Backup Metadata
  
    ```bash
    # Backup PostgreSQL
    docker exec postgres-primary pg_dump -U postgres metadata > backup.sql
    ```

    ### Update RisingWave Version
  
    ```bash
    # Set new version
    export RW_IMAGE=docker.arvancloud.ir/risingwavelabs/risingwave:v2.8.0
    
    # Rolling update
    docker-compose up -d --no-deps frontend-node-0
    docker-compose up -d --no-deps frontend-node-1
    docker-compose up -d --no-deps compute-node-0
    docker-compose up -d --no-deps compute-node-1
    ```
  
    ### Check Cluster Health
  
    ```bash
    # All services status
    docker-compose ps
    
    # Specific service logs
    docker-compose logs -f meta-node-0
    
    # Resource usage
    docker stats
    
    # Health checks
    docker-compose ps | grep healthy
    ```
  
    ## Troubleshooting
  
    ### Service Won't Start
  
    ```bash
    # Check logs
    docker-compose logs service-name
    
    # Check dependencies
    docker-compose ps
    
    # Restart service
    docker-compose restart service-name
    ```
  
    ### Connection Issues

    ```bash
    # Test PostgreSQL connection
    psql -h localhost -p 5430 -U postgres -d metadata -c "SELECT 1"

    # Test RisingWave connection
    psql -h localhost -p 4566 -U root -d dev -c "SELECT 1"

    # Check HAProxy status
    curl http://localhost:7000/stats
    ```
  
    ### Performance Issues
  
    ```bash
    # Check resource usage
    docker stats
    
    # Check Prometheus metrics
    curl http://localhost:9090/api/v1/query?query=up
    
    # View slow queries in meta dashboard
    open http://localhost:5691
    ```
  
    ## Shutdown
  
    ```bash
    # Graceful shutdown
    docker-compose down
    
    # Remove volumes (WARNING: deletes all data)
    docker-compose down -v
    ```
  
    ## Production Considerations
  
    1. **Resource Allocation**: Adjust memory limits based on workload
    2. **Network Configuration**: Use dedicated network in production
    3. **Secrets Management**: Use Docker secrets or external secret manager
    4. **Backup Strategy**: Implement automated backup for PostgreSQL and rustfs
    5. **Monitoring Alerts**: Configure Prometheus alerting rules
    6. **SSL/TLS**: Enable encryption for production traffic
    7. **Persistent Storage**: Use named volumes or external storage
  
    ## Support
  
    - RisingWave Documentation: https://docs.risingwave.com
    - GitHub Issues: https://github.com/risingwavelabs/risingwave
    - Community Slack: https://risingwave.com/slack
  