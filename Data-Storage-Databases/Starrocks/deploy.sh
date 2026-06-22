#!/bin/bash

# StarRocks 4.0.5 Production Deployment Script
# This script helps deploy and manage the StarRocks cluster

set -e

COMPOSE_FILE="docker-compose.yml"
PROJECT_NAME="starrocks"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check if Docker is running
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker first."
        exit 1
    fi

    # Check if Docker Compose is available
    if ! command -v docker-compose >/dev/null 2>&1; then
        print_error "Docker Compose is not installed."
        exit 1
    fi

    # Check if RisingWave cluster is running
    if ! docker network ls | grep -q "rw-network"; then
        print_warning "RisingWave network not found. Make sure RisingWave cluster is running."
        print_info "Run: cd ../RisingWave/cluster && docker-compose up -d"
        exit 1
    fi

    print_success "Prerequisites check passed."
}

# Function to start the cluster
start_cluster() {
    print_info "Starting StarRocks cluster..."

    # Start the cluster
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME up -d

    print_success "StarRocks cluster started."
    print_info "Waiting for cluster to initialize (this may take 2-3 minutes)..."

    # Wait for initialization
    sleep 30

    # Check if initialization completed
    if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs starrocks-init | grep -q "StarRocks MinIO initialization complete"; then
        print_success "Cluster initialization completed."
    else
        print_warning "Cluster initialization may still be in progress."
    fi

    print_access_info
}

# Function to stop the cluster
stop_cluster() {
    print_info "Stopping StarRocks cluster..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down
    print_success "StarRocks cluster stopped."
}

# Function to restart the cluster
restart_cluster() {
    print_info "Restarting StarRocks cluster..."
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME restart
    print_success "StarRocks cluster restarted."
}

# Function to check cluster status
check_status() {
    print_info "Checking cluster status..."

    echo "Container Status:"
    docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME ps

    echo ""
    echo "FE Nodes Status:"
    # Try to connect to FE and show status
    if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T haproxy-fe nc -z 127.0.0.1 9030 2>/dev/null; then
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T starrocks-fe-1 mysql --connect-timeout 5 -h starrocks-fe-1 -P9030 -uroot -e "SHOW FRONTENDS;" 2>/dev/null || echo "FE not ready yet"
    else
        echo "Load balancer not ready"
    fi

    echo ""
    echo "CN Nodes Status:"
    if docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T haproxy-fe nc -z 127.0.0.1 9030 2>/dev/null; then
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME exec -T starrocks-fe-1 mysql --connect-timeout 5 -h starrocks-fe-1 -P9030 -uroot -e "SHOW COMPUTE NODES;" 2>/dev/null || echo "CN not ready yet"
    else
        echo "Load balancer not ready"
    fi
}

# Function to show access information
print_access_info() {
    echo ""
    print_success "StarRocks cluster is ready!"
    echo ""
    echo "Access Information:"
    echo "=================="
    echo "StarRocks SQL:     mysql -h localhost -P 9031 -u root"
    echo "Web UI:            http://localhost:8031"
    echo "MinIO Console:     http://localhost:9001 (hummockadmin/hummockadmin)"
    echo "Prometheus:        http://localhost:9501"
    echo "Grafana:           http://localhost:3002 (admin/admin123)"
    echo "HAProxy Stats:     http://localhost:8404/stats"
    echo ""
    echo "Test connection:"
    echo "mysql -h localhost -P 9031 -u root -e \"SHOW DATABASES;\""
}

# Function to show logs
show_logs() {
    if [ -n "$2" ]; then
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f "$2"
    else
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME logs -f
    fi
}

# Function to clean up
cleanup() {
    print_warning "This will remove all StarRocks data and containers."
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Cleaning up StarRocks cluster..."
        docker-compose -f $COMPOSE_FILE -p $PROJECT_NAME down -v --remove-orphans
        print_success "Cleanup completed."
    fi
}

# Function to show help
show_help() {
    echo "StarRocks 4.0.5 Production Deployment Script"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start     Start the StarRocks cluster"
    echo "  stop      Stop the StarRocks cluster"
    echo "  restart   Restart the StarRocks cluster"
    echo "  status    Show cluster status"
    echo "  logs      Show cluster logs (add service name for specific logs)"
    echo "  cleanup   Remove all containers and volumes (WARNING: destroys data)"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs starrocks-fe-1"
    echo "  $0 status"
}

# Main script logic
case "${1:-help}" in
    start)
        check_prerequisites
        start_cluster
        ;;
    stop)
        stop_cluster
        ;;
    restart)
        restart_cluster
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs "$@"
        ;;
    cleanup)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac