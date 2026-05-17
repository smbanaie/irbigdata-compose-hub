# PostgreSQL Production Security Guide

This guide covers securing your RisingWave cluster's PostgreSQL setup for production environments, addressing the security concerns with the current development configuration.

## Current Development Setup Issues

### 1. Authentication Security Risk

**Problem**: The current setup uses `POSTGRES_HOST_AUTH_METHOD: trust`, which allows **any client with network access** to connect to PostgreSQL without authentication.

**Risks**:
- Unauthorized access to metadata database
- Potential data breaches
- Compliance violations (GDPR, HIPAA, etc.)

### 2. Network Exposure

**Problem**: PostgreSQL ports are exposed without proper access controls.

**Current Exposed Ports**:
- Primary: `5432:5432`
- Replica: `5433:5432`
- HAProxy: `5430:5432`

## Production Security Configuration

### Step 1: Remove Trust Authentication

**Current Configuration** (Development):
```yaml
environment:
  POSTGRES_HOST_AUTH_METHOD: trust
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: postgres
```

**Production Configuration**:
```yaml
environment:
  POSTGRES_USER: postgres
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}  # Use environment variable
```

### Step 2: Create Custom pg_hba.conf

Create a `pg_hba.conf` file in your cluster directory:

```bash
# pg_hba.conf - PostgreSQL Host-Based Authentication
# TYPE  DATABASE        USER            ADDRESS                 METHOD

# Local connections (container internal)
local   all             postgres                                md5
local   all             postgres                                peer

# Docker network connections
host    all             postgres        postgres-replica.rw-network    md5
host    all             postgres        postgres-proxy.rw-network      md5

# Replication connections
host    replication     postgres        postgres-replica.rw-network    md5

# RisingWave service connections (through proxy)
host    metadata        postgres        meta-node-0.rw-network         md5
host    metadata        postgres        meta-node-1.rw-network         md5
host    metadata        postgres        risingwave-console.rw-network  md5

# External connections (if needed - restrict IP ranges)
# host    metadata        postgres        10.0.0.0/8                    md5
# host    metadata        postgres        172.16.0.0/12                md5
# host    metadata        postgres        192.168.0.0/16               md5

# Reject all other connections
host    all             all             0.0.0.0/0                      reject
```

### Step 3: Create Custom postgresql.conf

Create a `postgresql.conf` file for production settings:

```bash
# postgresql.conf - Production Configuration

# Security Settings
listen_addresses = '*'
ssl = on
ssl_cert_file = '/var/lib/postgresql/server.crt'
ssl_key_file = '/var/lib/postgresql/server.key'

# Logging
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_statement = 'ddl'
log_duration = on
log_lock_waits = on

# Performance (adjust based on your hardware)
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100

# Replication
wal_level = replica
max_wal_senders = 10
max_replication_slots = 10
hot_standby = on
```

### Step 4: Update Docker Compose Configuration

**Updated postgres-primary service**:
```yaml
postgres-primary:
  image: "docker.arvancloud.ir/postgres:18"
  container_name: postgres-primary
  environment:
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    POSTGRES_DB: metadata
    POSTGRES_INITDB_ARGS: --encoding=UTF-8 --lc-collate=C --lc-ctype=C
  volumes:
    - postgres-primary-data:/var/lib/postgresql/18/data
    - ./pg_hba.conf:/var/lib/postgresql/18/data/pg_hba.conf:ro
    - ./postgresql.conf:/var/lib/postgresql/18/data/postgresql.conf:ro
    - ./ssl/server.crt:/var/lib/postgresql/server.crt:ro
    - ./ssl/server.key:/var/lib/postgresql/server.key:ro
  ports:
    - "127.0.0.1:5432:5432"  # Bind to localhost only
  command: >
    postgres
    -c config_file=/var/lib/postgresql/18/data/postgresql.conf
    -c hba_file=/var/lib/postgresql/18/data/pg_hba.conf
    -c wal_level=replica
    -c max_wal_senders=10
    -c max_replication_slots=10
    -c hot_standby=on
```

**Updated postgres-replica service**:
```yaml
postgres-replica:
  image: "docker.arvancloud.ir/postgres:18"
  container_name: postgres-replica
  environment:
    POSTGRES_USER: postgres
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    PGDATA: /var/lib/postgresql/18/data/pgdata
  volumes:
    - postgres-replica-data:/var/lib/postgresql/18/data
    - ./pg_hba.conf:/var/lib/postgresql/18/data/pgdata/pg_hba.conf:ro
    - ./postgresql.conf:/var/lib/postgresql/18/data/pgdata/postgresql.conf:ro
    - ./ssl/server.crt:/var/lib/postgresql/server.crt:ro
    - ./ssl/server.key:/var/lib/postgresql/server.key:ro
  ports:
    - "127.0.0.1:5433:5432"  # Bind to localhost only
  command: >
    bash -c "
    if [ ! -f /var/lib/postgresql/18/data/pgdata/PG_VERSION ]; then
      rm -rf /var/lib/postgresql/18/data/pgdata/*
      until pg_basebackup -h postgres-primary -U postgres -D /var/lib/postgresql/18/data/pgdata -Fp -Xs -R; do
        echo 'Waiting for primary to be ready...'
        sleep 2
      done
    fi
    postgres -c config_file=/var/lib/postgresql/18/data/pgdata/postgresql.conf -c hba_file=/var/lib/postgresql/18/data/pgdata/pg_hba.conf -c hot_standby=on
    "
```

### Step 5: SSL/TLS Configuration

**Generate SSL certificates**:

```bash
# Create SSL directory
mkdir -p ssl
cd ssl

# Generate CA private key
openssl genrsa -des3 -out ca.key 4096

# Generate CA certificate
openssl req -new -x509 -days 3650 -key ca.key -sha256 -out ca.crt -subj "/C=US/ST=State/L=City/O=Organization/CN=PostgreSQL-CA"

# Generate server private key
openssl genrsa -out server.key 4096

# Generate certificate signing request
openssl req -subj "/C=US/ST=State/L=City/O=Organization/CN=postgres-primary" -new -key server.key -out server.csr

# Create extensions file for server certificate
echo "subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer
basicConstraints=CA:FALSE
keyUsage = digitalSignature, nonRepudiation, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = postgres-primary
DNS.2 = postgres-replica
DNS.3 = postgres-proxy
IP.1 = 127.0.0.1" > server.ext

# Sign server certificate
openssl x509 -req -days 365 -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -sha256 -extfile server.ext

# Set proper permissions
chmod 600 server.key
chmod 644 server.crt
```

### Step 6: Environment Variables and Secrets

**Create .env file**:
```bash
# .env - Production Environment Variables
POSTGRES_PASSWORD=your-secure-password-here
POSTGRES_REPLICATION_PASSWORD=your-replication-password-here
```

**Use Docker secrets** (recommended for production):
```yaml
secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt
  postgres_replication_password:
    file: ./secrets/postgres_replication_password.txt
```

### Step 7: Network Security

**Update HAProxy configuration** (`haproxy.cfg`):
```haproxy
# Restrict admin access
listen stats
    bind 127.0.0.1:7000  # Bind to localhost only
    mode http
    stats enable
    stats uri /stats
    stats refresh 10s
    stats auth admin:secure-password-here  # Add authentication
```

**Docker network security**:
```yaml
networks:
  rw-network:
    driver: bridge
    internal: true  # Prevent external access to internal network
```

### Step 8: Monitoring and Auditing

**Add PostgreSQL monitoring**:
```yaml
# Add to prometheus.yml
scrape_configs:
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-primary:9187', 'postgres-replica:9187']
```

**Enable audit logging**:
```sql
-- Create audit schema and tables
CREATE SCHEMA audit;
CREATE TABLE audit.access_log (
    timestamp timestamp with time zone default now(),
    user_name text,
    database_name text,
    client_addr inet,
    command_tag text,
    query text
);

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger() RETURNS trigger AS $$
BEGIN
    INSERT INTO audit.access_log (user_name, database_name, client_addr, command_tag, query)
    VALUES (session_user, current_database(), inet_client_addr(), TG_OP, current_query());
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply to metadata table
CREATE TRIGGER metadata_audit AFTER INSERT OR UPDATE OR DELETE ON metadata FOR EACH STATEMENT EXECUTE FUNCTION audit_trigger();
```

### Step 9: Backup and Recovery

**Automated backup script** (`backup.sh`):
```bash
#!/bin/bash
BACKUP_DIR="/backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup primary database
pg_dump -h postgres-primary -U postgres -d metadata -F c -f $BACKUP_DIR/metadata_$TIMESTAMP.backup

# Backup configuration files
tar -czf $BACKUP_DIR/config_$TIMESTAMP.tar.gz pg_hba.conf postgresql.conf ssl/

# Clean old backups (keep last 7 days)
find $BACKUP_DIR -name "*.backup" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $TIMESTAMP"
```

**Add backup service to compose**:
```yaml
backup-service:
  image: postgres:18
  volumes:
    - ./backup.sh:/backup.sh:ro
    - postgres-primary-data:/var/lib/postgresql/18/data:ro
    - ./backups:/backups
    - ./ssl:/ssl:ro
  environment:
    PGPASSWORD: ${POSTGRES_PASSWORD}
  command: /backup.sh
  deploy:
    restart_policy:
      condition: none
```

### Step 10: Security Testing and Validation

**Test authentication**:
```bash
# Test local connection
docker exec -it postgres-primary psql -U postgres -d metadata -c "SELECT version();"

# Test replication connection
docker exec -it postgres-replica psql -U postgres -d metadata -c "SELECT * FROM pg_stat_replication;"

# Test HAProxy connection
docker exec -it postgres-proxy psql -h postgres-proxy -p 5432 -U postgres -d metadata -c "SELECT 1;"
```

**Security audit commands**:
```sql
-- Check current connections
SELECT usename, client_addr, state FROM pg_stat_activity;

-- Check authentication methods
SELECT * FROM pg_hba_file_rules;

-- Check SSL status
SELECT * FROM pg_stat_ssl;

-- Check replication status
SELECT * FROM pg_stat_replication;
```

## Migration Strategy

### From Development to Production

1. **Backup all data**:
   ```bash
   docker exec postgres-primary pg_dumpall -U postgres > full_backup.sql
   ```

2. **Stop all services**:
   ```bash
   docker-compose down
   ```

3. **Update configuration files** with production settings

4. **Remove existing volumes** (for fresh start):
   ```bash
   docker volume rm risingwave-cluster_postgres-primary-data risingwave-cluster_postgres-replica-data
   ```

5. **Start services with new configuration**:
   ```bash
   docker-compose up -d postgres-primary postgres-replica
   ```

6. **Restore data**:
   ```bash
   docker exec -i postgres-primary psql -U postgres < full_backup.sql
   ```

7. **Verify replication**:
   ```bash
   docker exec postgres-replica psql -U postgres -c "SELECT * FROM pg_stat_wal_receiver;"
   ```

## Monitoring and Alerts

### Key Metrics to Monitor

- **Connection counts**: `pg_stat_activity`
- **Replication lag**: `pg_stat_replication`
- **SSL connections**: `pg_stat_ssl`
- **Failed authentication attempts**: PostgreSQL logs
- **Lock waits**: `pg_locks`

### Alert Rules (Prometheus)

```yaml
groups:
  - name: postgresql
    rules:
      - alert: PostgreSQLDown
        expr: pg_up == 0
        for: 1m
        labels:
          severity: critical

      - alert: PostgreSQLReplicationLag
        expr: pg_replication_lag > 300
        for: 5m
        labels:
          severity: warning

      - alert: PostgreSQLHighConnections
        expr: pg_stat_activity_count > 80
        for: 5m
        labels:
          severity: warning
```

## Compliance Considerations

### GDPR Compliance
- Implement data minimization
- Enable audit logging
- Regular security assessments
- Data encryption at rest and in transit

### Security Best Practices
- Regular password rotation
- Principle of least privilege
- Network segmentation
- Regular security updates
- Backup encryption

## Troubleshooting

### Common Issues

**Replication not working after security changes**:
```sql
-- Check replication user permissions
GRANT pg_read_all_data TO postgres;
GRANT pg_write_all_data TO postgres;

-- Verify replication slot exists
SELECT * FROM pg_replication_slots;
```

**SSL connection errors**:
```bash
# Verify certificate permissions
ls -la ssl/
# Should be: server.crt (644), server.key (600)

# Test SSL connection
openssl s_client -connect localhost:5432 -starttls postgres
```

**Authentication failures**:
```sql
-- Check HBA configuration
SELECT * FROM pg_hba_file_rules;

-- Test specific connection
psql -h postgres-primary -U postgres -d metadata
```

This guide provides a comprehensive security hardening process for your RisingWave PostgreSQL cluster. Start with the basic authentication changes and gradually implement additional security measures based on your security requirements and compliance needs.