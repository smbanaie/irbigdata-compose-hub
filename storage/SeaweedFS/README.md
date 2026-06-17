# SeaweedFS

SeaweedFS is a simple and highly scalable distributed file system. This folder contains a 3‑node cluster configuration with RF=2 (Replication Factor 2) for high availability.

## Cluster Overview

- **1 Master**: Coordinates volumes and tracks replication (`port=9333`)
- **3 Volume Nodes**: Store actual data with replication enabled (`port=8080`)
- **1 Filer**: Provides file system interface and metadata management (`port=8888`)
- **1 S3 Gateway**: Exposes S3-compatible API (`port=8333`)

## Configuration Details

### Replication

The master is configured with `-defaultReplication=001`, meaning every file is replicated to 1 other volume node (2 total copies). This gives RF=1. For 3 copies (RF=2), change to `002`.

## Usage

```bash
# Start the 3‑node SeaweedFS cluster
cd storage/SeaweedFS
mkdir -p data-volume{1,2,3}
docker compose up -d

# Check status
docker compose ps
```

## Access the Cluster

- **Filer API**: `http://localhost:8888`
- **S3 Gateway**: `http://localhost:8333`
- **Web UI**: Available at http://localhost:8888/filer (filer interface)

## Credentials

SeaweedFS uses simple authentication. For the S3 gateway, use:

- **Access Key**: `admin`
- **Secret Key**: `admin`

## Testing Replication

To verify RF=2 is working:

1. Upload a test file through the S3 gateway or using the weed CLI
2. Check that the file appears in all three volume data directories:

```bash
# Inside the master container
docker exec -it seaweedfs-master /bin/bash
weed upload -replication=002 /etc/hosts

# Check volume directories
ls -l data-volume1/
ls -l data-volume2/
ls -l data-volume3/
```

You should see the file (or its volume data) appearing on all three nodes.

## Stopping

```bash
# Stop all containers
docker compose down

# Clean up volume data (optional)
docker compose down --rmi all
```

## Performance Tips

- **Resource usage**: Three volume nodes plus master, filer, and S3 gateway require at least 8 GB RAM and moderate CPU
- **Persistence**: Host directories (`./data-volume*`) persist data across container restarts
- **Scaling**: You can add more volume nodes later; the master will automatically redistribute volumes if you increase the replication factor
- **Benchmarking**: Your benchmark script will work out-of-the-box by setting `TARGET = 'seaweedfs'`