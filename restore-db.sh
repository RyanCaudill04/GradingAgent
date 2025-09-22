#!/bin/bash

# Database restore script for CSCE-247 Grading System
BACKUP_DIR="./backups"

if [ $# -eq 0 ]; then
    echo "🔍 Available backups:"
    ls -la "$BACKUP_DIR"/grader_backup_*.sql 2>/dev/null | awk '{print $9}' | sed 's|.*/||'
    echo ""
    echo "Usage: $0 <backup_filename>"
    echo "Example: $0 grader_backup_20240922_143000.sql"
    exit 1
fi

BACKUP_FILE="$BACKUP_DIR/$1"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup file not found: $BACKUP_FILE"
    exit 1
fi

echo "⚠️  WARNING: This will replace ALL current data!"
echo "📁 Restoring from: $BACKUP_FILE"
read -p "Are you sure? (y/N): " -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔄 Stopping services..."
    docker-compose stop django fastapi

    echo "🗄️  Restoring database..."
    docker-compose exec -T db psql -U postgres -d postgres -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
    cat "$BACKUP_FILE" | docker-compose exec -T db psql -U postgres -d postgres

    echo "🚀 Starting services..."
    docker-compose start django fastapi

    echo "✅ Database restored successfully!"
else
    echo "❌ Restore cancelled"
fi