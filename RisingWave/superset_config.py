# superset_config.py
# Custom Superset configuration for RisingWave Integration

import os
import json

# Get environment variables or use defaults
SUPERSET_SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'SeP@hT@n#123')

# ---------------------------------------------------
# Database Configuration
# ---------------------------------------------------
# Superset's own metadata database
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",
    "postgresql://superset_user@postgres-primary:5432/superset_meta",
)

# ---------------------------------------------------
# Feature Flags
# ---------------------------------------------------
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
    "ALERT_REPORTS": True,
    "DASHBOARD_RBAC": True,
    "OMNIBAR": True,
    "DRILL_TO_DETAIL": True,
    "DRILL_BY": True,
}

# ---------------------------------------------------
# Cache Configuration (using SimpleCache for now)
# ---------------------------------------------------
# Using SimpleCache instead of SupersetCache to avoid complexity
CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}

DATA_CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300
}

# ---------------------------------------------------
# Celery Configuration (disabled for simplicity)
# ---------------------------------------------------
# Comment out Celery for now - can be enabled later
# class CeleryConfig:
#     broker_url = "memory://"
#     result_backend = f"db+{SQLALCHEMY_DATABASE_URI.replace('superset_meta', 'superset_cache')}"
#     worker_prefetch_multiplier = 1
#     task_acks_late = True

# CELERY_CONFIG = CeleryConfig
CELERY_CONFIG = None

# ---------------------------------------------------
# RisingWave Data Source Configuration
# ---------------------------------------------------
# IMPORTANT: Changed port from 4567 to 4566 (internal Docker network)
RISINGWAVE_CONNECTION_URI = 'postgresql+psycopg2://postgres:@haproxy:4566/metadata'

# ---------------------------------------------------
# Security & Authentication
# ---------------------------------------------------
# Enable CORS for embedding
ENABLE_CORS = True
CORS_OPTIONS = {
    'supports_credentials': True,
    'allow_headers': ['*'],
    'resources': ['*'],
    'origins': ['http://localhost:*', 'http://127.0.0.1:*']
}

WTF_CSRF_ENABLED = False
WTF_CSRF_TIME_LIMIT = 3600

# ---------------------------------------------------
# Internationalization
# ---------------------------------------------------
BABEL_DEFAULT_LOCALE = "en"
BABEL_DEFAULT_TIMEZONE = "UTC"
LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'zh': {'flag': 'cn', 'name': 'Chinese'},
}

# ---------------------------------------------------
# File Uploads
# ---------------------------------------------------
UPLOAD_FOLDER = "/var/lib/superset/uploads"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "json", "parquet"}
MAX_CONTENT_LENGTH = 200 * 1024 * 1024  # 200MB

# ---------------------------------------------------
# Dashboard Configuration
# ---------------------------------------------------
GUEST_ROLE_NAME = "Gamma"
GUEST_TOKEN_JWT_EXP_SECONDS = 300
GUEST_TOKEN_JWT_SECRET = SUPERSET_SECRET_KEY
GUEST_TOKEN_JWT_ALGO = "HS256"

# ---------------------------------------------------
# Custom Branding
# ---------------------------------------------------
APP_NAME = "RisingWave Analytics"
APP_ICON = "/static/assets/images/superset-logo-horiz.png"
FAVICONS = [{"href": "/static/assets/images/favicon.png"}]

# ---------------------------------------------------
# Performance Tuning
# ---------------------------------------------------
SUPERSET_WEBSERVER_TIMEOUT = 60
SUPERSET_WEBSERVER_WORKERS = 4
SQLLAB_TIMEOUT = 60
SQLLAB_VALIDATION_TIMEOUT = 10
FILTER_SELECT_ROW_LIMIT = 10000
VIZ_ROW_LIMIT = 10000

# ---------------------------------------------------
# Public Role Permissions (for embedded dashboards)
# ---------------------------------------------------
PUBLIC_ROLE_LIKE = "Gamma"

# ---------------------------------------------------
# SQL Lab Settings
# ---------------------------------------------------
DISPLAY_SQL_MAX_ROW = 100000
SQL_MAX_ROW = 100000
SQLLAB_CTAS_NO_LIMIT = True
SQLLAB_DEFAULT_DBID = None  # Will be set to RisingWave connection
