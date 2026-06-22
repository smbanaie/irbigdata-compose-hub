# Start from the official Airflow image
FROM docker.arvancloud.ir/apache/airflow:3.2.1

# Switch to root to install system packages
USER root

# Configure Debian mirrors for Iran (Bookworm) and disable repository expiry checks
RUN echo "deb http://mirror.arvancloud.ir/debian bookworm main" > /etc/apt/sources.list && \
    echo "deb http://mirror.arvancloud.ir/debian-security bookworm-security main" >> /etc/apt/sources.list && \
    echo 'Acquire::Check-Valid-Until "false";' > /etc/apt/apt.conf.d/99no-check-valid-until

# Install timezone data and configure Asia/Tehran
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && ln -fs /usr/share/zoneinfo/Asia/Tehran /etc/localtime \
    && dpkg-reconfigure -f noninteractive tzdata \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to the airflow user (important!)
USER airflow

# Install additional Python dependencies using Iran mirror
RUN pip install --trusted-host mirror-pypi.runflare.com \
    -i https://mirror-pypi.runflare.com/simple/ \
    --no-cache-dir pandas jdatetime openpyxl faker
