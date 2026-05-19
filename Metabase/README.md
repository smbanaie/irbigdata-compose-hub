# Metabase

Custom Metabase BI tool built from Ubuntu + OpenJDK 21.

## Services

| Service | Image | Port |
|---------|-------|------|
| metabase | build (custom Dockerfile) | `3000:3000` |

## Usage

```bash
docker compose -f compose.yml up -d
```

Access at http://localhost:3000.

## Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Metabase from Ubuntu + OpenJDK 21 |
| `data/` | Metabase database storage (H2 file) |
| `plugins/` | Custom JDBC drivers |
