# Makefile for Grader project management

.PHONY: help build up down rebuild-services rebuild-all logs clean dev

help: ## Show this help message
	@echo "🎯 Grader Project Commands"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build all services
	docker-compose build

up: ## Start all services
	docker-compose up -d

down: ## Stop all services
	docker-compose down

rebuild-services: ## Rebuild only frontend and backend (keeps DB running)
	@echo "🔄 Rebuilding frontend and backend services..."
	docker-compose stop django fastapi
	docker-compose rm -f django fastapi
	docker-compose up --build -d django fastapi
	@echo "✅ Services rebuilt!"
	@make status

rebuild-all: ## Rebuild everything from scratch
	docker-compose down
	docker-compose up --build -d

logs: ## Show logs for all services
	docker-compose logs -f

logs-django: ## Show Django logs
	docker-compose logs -f django

logs-fastapi: ## Show FastAPI logs
	docker-compose logs -f fastapi

logs-db: ## Show database logs
	docker-compose logs -f db

status: ## Show service status
	@echo "📊 Service Status:"
	@docker-compose ps
	@echo ""
	@echo "🌐 Access Points:"
	@echo "   Frontend:  http://localhost:8000"
	@echo "   Backend:   http://localhost:8001"
	@echo "   pgAdmin:   http://localhost:5050"
	@echo "   Database:  localhost:5432"

dev: ## Start in development mode with hot reload
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build -d

clean: ## Clean up containers, networks, and volumes
	docker-compose down -v
	docker system prune -f

migrate: ## Run Django migrations
	docker-compose exec django python manage.py migrate

shell-django: ## Open Django shell
	docker-compose exec django python manage.py shell

shell-fastapi: ## Open FastAPI container shell
	docker-compose exec fastapi /bin/bash

shell-db: ## Open database shell
	docker-compose exec db psql -U postgres -d postgres

test: ## Run tests
	docker-compose exec fastapi python -m pytest
	docker-compose exec django python manage.py test

backup: ## Create database backup
	./backup-db.sh

restore: ## Restore database from backup (will prompt for file)
	./restore-db.sh

list-backups: ## List available database backups
	@echo "📁 Available backups:"
	@ls -la ./backups/grader_backup_*.sql 2>/dev/null || echo "No backups found"