# Makefile for managing Mail Server Docker containers

.PHONY: help build run stop clean logs shell test dev prod restart

# Variables
IMAGE_NAME = test-mail-server
CONTAINER_NAME = test-mail-server
API_PORT = 3000
SMTP_PORT = 25

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Show help
	@echo "$(GREEN)Mail Server Docker Commands$(NC)"
	@echo "=============================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-15s$(NC) %s\n", $$1, $$2}'

build: ## Build Docker image
	@echo "$(GREEN)Building Docker image...$(NC)"
	docker build -f docker/Dockerfile -t $(IMAGE_NAME):latest .

build-dev: ## Build development image
	@echo "$(GREEN)Building development Docker image...$(NC)"
	docker-compose -f docker/docker-compose.dev.yml build

run: ## Start container (production)
	@echo "$(GREEN)Starting mail server...$(NC)"
	docker-compose -f docker/docker-compose.yml up -d
	@echo "$(GREEN)Mail server started!$(NC)"
	@echo "API: http://localhost:$(API_PORT)/docs"
	@echo "SMTP: localhost:$(SMTP_PORT)"

dev: ## Start in development mode
	@echo "$(GREEN)Starting development server...$(NC)"
	docker-compose -f docker/docker-compose.dev.yml up --build
	
stop: ## Stop container
	@echo "$(YELLOW)Stopping mail server...$(NC)"
	docker-compose -f docker/docker-compose.yml down
	docker-compose -f docker/docker-compose.dev.yml down

restart: ## Restart container
	@echo "$(YELLOW)Restarting mail server...$(NC)"
	$(MAKE) stop
	$(MAKE) run

logs: ## Show logs
	docker-compose logs -f mailserver

logs-dev: ## Show development logs
	docker-compose -f docker-compose.dev.yml logs -f mailserver-dev

shell: ## Enter container
	docker exec -it $(CONTAINER_NAME) /bin/bash

shell-dev: ## Enter dev container
	docker exec -it test-mail-server-dev /bin/bash

test: ## Run tests in container
	@echo "$(GREEN)Running tests...$(NC)"
	docker-compose --profile testing up -d
	docker exec mail-test-client pip install -r requirements.txt
	docker exec mail-test-client python test_fastapi.py
	docker-compose --profile testing down

clean: ## Clean Docker resources
	@echo "$(RED)Cleaning up Docker resources...$(NC)"
	docker-compose down -v
	docker-compose -f docker-compose.dev.yml down -v
	docker rmi $(IMAGE_NAME):latest $(IMAGE_NAME):dev 2>/dev/null || true
	docker system prune -f

status: ## Show container status
	@echo "$(GREEN)Container status:$(NC)"
	docker ps -a --filter name=mail

health: ## Check service health
	@echo "$(GREEN)Checking service health...$(NC)"
	@curl -s http://localhost:$(API_PORT)/api/v1/status || echo "$(RED)Service not accessible$(NC)"

api-key: ## Get API key from logs
	@echo "$(GREEN)API Key from logs:$(NC)"
	docker logs $(CONTAINER_NAME) 2>&1 | grep "API Key:" | tail -1

quick-test: ## Quick email sending test
	@echo "$(GREEN)Sending test email...$(NC)"
	docker exec $(CONTAINER_NAME) python -c "import smtplib; from email.mime.text import MIMEText; msg = MIMEText('Test from Docker'); msg['Subject'] = 'Docker Test'; msg['From'] = 'test@test-mail.example.com'; msg['To'] = 'user@test-mail.example.com'; s = smtplib.SMTP('localhost', 25); s.send_message(msg); s.quit(); print('Email sent!')"

info: ## Show service information
	@echo "$(GREEN)Mail Server Information:$(NC)"
	@echo "Image: $(IMAGE_NAME):latest"
	@echo "Python: 3.13.4"
	@echo "Container: $(CONTAINER_NAME)"
	@echo "API URL: http://localhost:$(API_PORT)"
	@echo "API Docs: http://localhost:$(API_PORT)/docs"
	@echo "SMTP Port: $(SMTP_PORT)"
	@echo ""
	@echo "$(YELLOW)Quick commands:$(NC)"
	@echo "make run     - Start server"
	@echo "make dev     - Start in dev mode"
	@echo "make logs    - View logs"
	@echo "make stop    - Stop server"

# Show help by default
.DEFAULT_GOAL := help 