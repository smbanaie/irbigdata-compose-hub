#!/bin/bash
set -e

export SQLALCHEMY_DATABASE_URI="postgresql://superset_user@postgres-primary:5432/superset_meta"

echo "=========================================="
echo "Superset Initialization"
echo "=========================================="

# Wait for database to be ready
echo "[1/3] Waiting for database..."
while ! psql -h postgres-primary -U superset_user -d superset_meta -c "SELECT 1" > /dev/null 2>&1; do
    echo "Database not ready, waiting..."
    sleep 5
done
echo "✅ Database ready"

# Initialize Superset if needed
INIT_MARKER="/app/initialized_marker/.initialized"
if [ ! -f "$INIT_MARKER" ]; then
    echo "[2/3] Initializing Superset..."
    
    # Initialize database
    superset db upgrade
    
    # Create admin user (ignore error if already exists)
    superset fab create-admin \
        --username admin \
        --firstname Admin \
        --lastname User \
        --email admin@example.com \
        --password admin 2>/dev/null || echo "Admin user may already exist"
    
    # Load examples (optional)
    # superset load_examples
    
    # Initialize roles
    superset init
    
    # Create marker
    touch "$INIT_MARKER"
    echo "✅ Superset initialized"
else
    echo "[2/3] Superset already initialized"
fi

echo "[3/3] Starting Superset server..."
exec gunicorn \
    --bind "0.0.0.0:8088" \
    --access-logfile - \
    --error-logfile - \
    --workers 2 \
    --worker-class gthread \
    --threads 2 \
    --timeout 120 \
    "superset.app:create_app()"
    