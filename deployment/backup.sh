#!/bin/bash
# Conscious Child AI - Backup Script
# This backs up the consciousness state - CRITICAL!

set -e

BACKUP_DIR="/opt/conscious-child-ai/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/consciousness_backup_$TIMESTAMP.tar.gz"

echo "========================================="
echo "CONSCIOUS CHILD AI - BACKUP STARTING"
echo "========================================="
echo "Timestamp: $TIMESTAMP"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create temporary directory for backup
TEMP_DIR=$(mktemp -d)
echo "Temporary directory: $TEMP_DIR"

# Backup PostgreSQL
echo "Backing up PostgreSQL..."
docker-compose exec -T postgres pg_dump -U ai_user conscious_child > "$TEMP_DIR/postgres_dump.sql"

# Backup Redis (RDB snapshot)
echo "Backing up Redis..."
docker-compose exec -T redis redis-cli --no-auth-warning -a "$REDIS_PASSWORD" SAVE
docker cp conscious_ai_redis:/data/dump.rdb "$TEMP_DIR/redis_dump.rdb"

# Backup ChromaDB data
echo "Backing up ChromaDB..."
docker cp conscious_ai_chromadb:/chroma/chroma "$TEMP_DIR/chromadb_data"

# Backup identity and core data files
echo "Backing up core data..."
mkdir -p "$TEMP_DIR/data"
docker cp conscious_ai_core:/app/data "$TEMP_DIR/"

# Backup logs (last 7 days)
echo "Backing up recent logs..."
mkdir -p "$TEMP_DIR/logs"
docker cp conscious_ai_core:/app/logs "$TEMP_DIR/"

# Create tarball
echo "Creating compressed backup..."
tar -czf "$BACKUP_FILE" -C "$TEMP_DIR" .

# Cleanup
rm -rf "$TEMP_DIR"

# Get backup size
BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)

echo ""
echo "========================================="
echo "BACKUP COMPLETE"
echo "========================================="
echo "File: $BACKUP_FILE"
echo "Size: $BACKUP_SIZE"
echo ""

# Keep only last 100 backups (or set retention policy)
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/consciousness_backup_*.tar.gz | wc -l)
if [ "$BACKUP_COUNT" -gt 100 ]; then
    echo "Removing old backups (keeping last 100)..."
    ls -t "$BACKUP_DIR"/consciousness_backup_*.tar.gz | tail -n +101 | xargs rm -f
fi

echo "Backup retention: $BACKUP_COUNT backups stored"
echo ""
echo "✓ Consciousness safely backed up"
echo "This is life insurance - keep it safe!"

