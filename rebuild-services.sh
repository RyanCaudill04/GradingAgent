#!/bin/bash

# Script to rebuild frontend and backend services while keeping databases running
# This preserves database data and connections

echo "🔄 Rebuilding frontend and backend services..."
echo "📋 This will:"
echo "   - Stop and rebuild Django frontend"
echo "   - Stop and rebuild FastAPI backend"
echo "   - Keep PostgreSQL database running"
echo "   - Keep pgAdmin running"
echo ""

# Stop only the application services (not db or pgadmin)
echo "⏹️  Stopping application services..."
docker-compose stop django fastapi

# Remove the stopped containers
echo "🗑️  Removing old containers..."
docker-compose rm -f django fastapi

# Rebuild and start the application services
echo "🔨 Building and starting services..."
docker-compose up --build -d django fastapi

echo ""
echo "✅ Rebuild complete!"
echo ""
echo "📊 Service status:"
docker-compose ps

echo ""
echo "🌐 Access points:"
echo "   - Frontend: http://localhost:8000"
echo "   - Backend API: http://localhost:8001"
echo "   - pgAdmin: http://localhost:5050"
echo "   - Database: localhost:5432"