#!/bin/bash

# Database backup script for CSCE-247 Grading System
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/grader_backup_$TIMESTAMP.sql"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "🗄️  Creating database backup..."
echo "📁 Backup location: $BACKUP_FILE"

# Create PostgreSQL dump
docker-compose exec -T db pg_dump -U postgres -d postgres > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE"

    # Keep only last 10 backups
    ls -t "$BACKUP_DIR"/grader_backup_*.sql | tail -n +11 | xargs -r rm
    echo "🧹 Cleaned up old backups (kept 10 most recent)"

    echo "📊 Current backups:"
    ls -la "$BACKUP_DIR"/grader_backup_*.sql
else
    echo "❌ Backup failed!"
    exit 1
fi