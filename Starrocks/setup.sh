#!/bin/bash

# StarRocks v4 Production Cluster Setup Script
# This script sets up a complete StarRocks cluster with MinIO storage

set -e

echo "================================================"
echo "StarRocks v4 Production Cluster Setup"
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_info "Docker and Docker Compose are installed."
}

# Create directory structure
create_directories() {
    print_info "Creating directory structure..."
    mkdir -p logs
    mkdir -p backups
    print_info "Directories created."
}

# Start MinIO cluster first
start_minio() {
    print_info "Starting MinIO cluster..."
    docker-compose up -d minio1 minio2 minio3
    
    print_info "Waiting for MinIO cluster to be ready..."
    sleep 30
    
    # Check MinIO health
    if curl -f http://localhost:9000/minio/health/live &> /dev/null; then
        print_info "MinIO cluster is healthy!"
    else
        print_warn "MinIO might not be fully ready yet. Continuing anyway..."
    fi
}

# Create MinIO bucket
create_minio_bucket() {
    print_info "Creating StarRocks bucket in MinIO..."
    
    # Install mc (MinIO Client) if not present
    if ! command -v mc &> /dev/null; then
        print_info "Installing MinIO client..."
        docker run --rm --network host \
            --entrypoint sh \
            minio/mc:latest \
            -c "mc alias set myminio http://localhost:9000 minioadmin minioadmin123 && \
                mc mb myminio/starrocks --ignore-existing && \
                mc anonymous set download myminio/starrocks"
    else
        mc alias set myminio http://localhost:9000 minioadmin minioadmin123
        mc mb myminio/starrocks --ignore-existing
        mc anonymous set download myminio/starrocks
    fi
    
    print_info "MinIO bucket 'starrocks' created."
}

# Start FE nodes
start_fe_nodes() {
    print_info "Starting FE Leader (fe1)..."
    docker-compose up -d fe1
    
    print_info "Waiting for FE Leader to be ready..."
    sleep 45
    
    # Check if FE1 is ready
    for i in {1..30}; do
        if curl -f http://localhost:8031/api/bootstrap &> /dev/null; then
            print_info "FE Leader is ready!"
            break
        fi
        echo -n "."
        sleep 2
    done
    
    print_info "Starting FE Followers (fe2, fe3)..."
    docker-compose up -d fe2 fe3
    sleep 30
}

# Add FE followers to cluster
add_fe_followers() {
    print_info "Adding FE followers to the cluster..."
    
    # Connect to FE1 and add FE2 and FE3
    docker exec -it starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root -e "ALTER SYSTEM ADD FOLLOWER 'fe2:9010';" 2>/dev/null || true
    sleep 5
    docker exec -it starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root -e "ALTER SYSTEM ADD FOLLOWER 'fe3:9010';" 2>/dev/null || true
    sleep 5
    
    print_info "FE followers added. Checking cluster status..."
    docker exec -it starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root -e "SHOW PROC '/frontends'\\G"
}

# Start Compute Nodes
start_compute_nodes() {
    print_info "Starting Compute Nodes..."
    docker-compose up -d cn1 cn2 cn3
    sleep 30
}

# Add Compute Nodes to cluster
add_compute_nodes() {
    print_info "Adding Compute Nodes to the cluster..."
    
    docker exec -it starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root -e "ALTER SYSTEM ADD COMPUTE NODE 'cn1:9050';" 2>/dev/null || true
    sleep 5
    docker exec -it starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root -e "ALTER SYSTEM ADD COMPUTE NODE 'cn2:9050';" 2>/dev/null || true
    sleep 5
    docker exec -it starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root -e "ALTER SYSTEM ADD COMPUTE NODE 'cn3:9050';" 2>/dev/null || true
    sleep 5
    
    print_info "Compute nodes added. Checking cluster status..."
    docker exec -it starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root -e "SHOW PROC '/compute_nodes'\\G"
}

# Verify cluster status
verify_cluster() {
    print_info "Verifying cluster status..."
    
    echo ""
    echo "=== Frontend Nodes ==="
    docker exec starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root -e "SHOW PROC '/frontends'\\G" 2>/dev/null || print_warn "Could not retrieve FE status"
    
    echo ""
    echo "=== Compute Nodes ==="
    docker exec starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root -e "SHOW PROC '/compute_nodes'\\G" 2>/dev/null || print_warn "Could not retrieve CN status"
    
    echo ""
    echo "=== Storage Volumes ==="
    docker exec starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root -e "SHOW STORAGE VOLUMES\\G" 2>/dev/null || print_warn "Could not retrieve storage volumes"
}

# Create default storage volume
create_storage_volume() {
    print_info "Creating default storage volume..."
    
    docker exec -it starrocks-fe1 mysql -h 127.0.0.1 -P 9030 -u root << EOF
CREATE STORAGE VOLUME IF NOT EXISTS default_storage_volume
TYPE = S3
LOCATIONS = ('s3://starrocks/')
PROPERTIES
(
    "enabled" = "true",
    "aws.s3.region" = "us-east-1",
    "aws.s3.endpoint" = "http://minio1:9000",
    "aws.s3.use_instance_profile" = "false",
    "aws.s3.use_aws_sdk_default_behavior" = "false"
)
COMMENT = 'Default storage volume for StarRocks';

SET default_storage_volume = default_storage_volume;
EOF
    
    print_info "Default storage volume created!"
}

# Print connection information
print_connection_info() {
    echo ""
    echo "================================================"
    print_info "StarRocks Cluster Setup Complete!"
    echo "================================================"
    echo ""
    echo "Connection Information:"
    echo "----------------------"
    echo "FE1 Query Port:    localhost:9031 (Leader)"
    echo "FE2 Query Port:    localhost:9032 (Follower)"
    echo "FE3 Query Port:    localhost:9033 (Follower)"
    echo ""
    echo "FE1 HTTP Port:     http://localhost:8031"
    echo "FE2 HTTP Port:     http://localhost:8032"
    echo "FE3 HTTP Port:     http://localhost:8033"
    echo ""
    echo "MinIO Console:     http://localhost:9001"
    echo "MinIO Credentials: minioadmin / minioadmin123"
    echo ""
    echo "To connect to StarRocks:"
    echo "  mysql -h 127.0.0.1 -P 9031 -u root"
    echo ""
    echo "To view logs:"
    echo "  docker-compose logs -f [service-name]"
    echo ""
    echo "To stop the cluster:"
    echo "  docker-compose down"
    echo ""
    echo "To stop and remove all data:"
    echo "  docker-compose down -v"
    echo ""
}

# Main execution
main() {
    check_docker
    create_directories
    
    print_info "Starting cluster deployment..."
    
    start_minio
    create_minio_bucket
    start_fe_nodes
    add_fe_followers
    start_compute_nodes
    add_compute_nodes
    create_storage_volume
    
    sleep 10
    verify_cluster
    print_connection_info
}

# Run main function
main