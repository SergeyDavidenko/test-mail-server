# 📧 Test Mail Server 

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

Modern FastAPI-based test mail server with SMTP support. A complete replacement for the deprecated Python `smtpd` module with enhanced features, REST API, and production-ready architecture.

## 🚀 Features

- **Modern Architecture**: Built with FastAPI and aiosmtpd
- **REST API**: Full REST API with automatic documentation
- **Authentication**: Secure API key authentication
- **Real-time Email Capture**: Capture and store emails in memory
- **Domain Filtering**: Accept emails only for configured domains
- **Automatic Cleanup**: Configurable email retention and cleanup
- **Health Monitoring**: Health checks and service monitoring
- **Docker Ready**: Complete Docker setup for development and production
- **Comprehensive Testing**: Full test suite with pytest
- **Type Safety**: Full type hints and Pydantic models

## 📁 Project Structure

```
test-mail-server/
├── app/                         # Main application package
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application
│   ├── config.py                # Configuration management
│   ├── models.py                # Pydantic models
│   ├── services/                # Business logic services
│   │   ├── __init__.py
│   │   ├── smtp_server.py       # SMTP server service
│   │   ├── email_storage.py     # Email storage service
│   │   └── cleanup.py           # Cleanup service
│   └── routers/                 # API route handlers
│       ├── __init__.py
│       ├── auth.py              # Authentication routes
│       ├── emails.py            # Email management routes
│       └── health.py            # Health check routes
├── tests/                       # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Pytest configuration
│   └── test_*.py                # Test modules
├── docker/                      # Docker configuration
│   ├── Dockerfile               # Production Dockerfile
│   ├── Dockerfile.prod          # Optimized production Dockerfile
│   ├── docker-compose.yml       # Production compose
│   └── docker-compose.dev.yml   # Development compose
├── scripts/                     # Utility scripts
│   └── test_email_sender.py     # Email testing script
├── docs/                        # Documentation
│   └── README.md                # Detailed documentation
├── requirements.txt             # Production dependencies
├── requirements-dev.txt         # Development dependencies
├── pyproject.toml               # Modern Python project configuration
├── Makefile                     # Docker management commands
└── .dockerignore                # Docker ignore file
```

## 🛠 Installation

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/SergeyDavidenko/test-mail-server.git
cd test-mail-server

# Start with Docker Compose
make run

# Or for development
make dev
```

### Option 2: Local Development

```bash
# Clone and setup
git clone https://github.com/SergeyDavidenko/test-mail-server.git
cd test-mail-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run the server
python -m app.main
```

## 🚀 Quick Start

1. **Start the server**:
   ```bash
   make run
   ```

2. **Get API key** (development mode):
   ```bash
   make api-key
   ```

3. **Access the API documentation**:
   - Swagger UI: http://localhost:3000/docs
   - ReDoc: http://localhost:3000/redoc

4. **Send test emails**:
   ```bash
   python scripts/test_email_sender.py
   ```

## 🔧 Configuration

Configure the server using environment variables:

```bash
# Server Configuration
HOST=0.0.0.0                    # Server host
SMTP_PORT=25                    # SMTP server port
API_PORT=3000                   # API server port
MAIL_DOMAIN=test-mail.example.com  # Email domain

# Email Settings
RETENTION_HOURS=4               # Email retention time
MAX_EMAILS_PER_ADDRESS=100      # Max emails per address
CLEANUP_INTERVAL_MINUTES=30     # Cleanup interval

# Authentication
API_KEY=your-secret-key         # API key (auto-generated if not set)

# Environment
APP_ENV=development             # development/production/testing
DEBUG=true                      # Debug mode
LOG_LEVEL=INFO                  # Logging level
```

## 📡 API Endpoints

### Authentication Required

All endpoints except `/health` and `/docs` require authentication:

```bash
# Using Bearer token
curl -H "Authorization: Bearer YOUR_API_KEY" http://localhost:3000/api/v1/addresses

# Using query parameter
curl "http://localhost:3000/api/v1/addresses?api_key=YOUR_API_KEY"
```

### Available Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check (no auth required) |
| `GET` | `/api/v1/addresses` | Get all email addresses |
| `GET` | `/api/v1/email/{address}` | Get emails for address |
| `DELETE` | `/api/v1/email/{address}` | Delete emails for address |
| `GET` | `/api/v1/status` | Get server status |
| `GET` | `/api/v1/services` | Get detailed service status |
| `POST` | `/api/v1/cleanup` | Force cleanup |
| `GET` | `/api/v1/stats` | Get storage statistics |
| `GET` | `/api/v1/auth/info` | Get auth information |
| `GET` | `/api/v1/auth/config` | Get server configuration |

## 🐳 Docker Commands

Use the provided Makefile for easy Docker management:

```bash
# Development
make dev          # Start development server with live reload
make build-dev    # Build development image

# Production
make run          # Start production server
make build        # Build production image

# Management
make stop         # Stop all containers
make restart      # Restart containers
make logs         # View logs
make shell        # Enter container shell
make clean        # Clean up Docker resources

# Testing
make test         # Run tests in container
make quick-test   # Send a test email

# Monitoring
make status       # Show container status
make health       # Check service health
make api-key      # Get API key from logs
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test types
pytest -m unit
pytest -m integration
```

### Send Test Emails

```bash
# Basic test
python scripts/test_email_sender.py

# Custom configuration
python scripts/test_email_sender.py \
  --host localhost \
  --port 25 \
  --domain test-mail.example.com \
  --test stress \
  --count 20
```

## 🔍 Monitoring

### Health Checks

```bash
# Basic health check
curl http://localhost:3000/api/v1/health

# Detailed status (requires auth)
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:3000/api/v1/status
```

### Logs

```bash
# View logs
make logs

# Follow logs in development
make logs-dev

# Docker logs directly
docker logs test-mail-server -f
```

## 🛡 Security

- **API Key Authentication**: All endpoints (except health checks) require API keys
- **Domain Filtering**: Only accepts emails for configured domains
- **Input Validation**: Comprehensive input validation with Pydantic
- **Error Handling**: Secure error handling without information leakage
- **Docker Security**: Non-root user, minimal attack surface
