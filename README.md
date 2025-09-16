# Arcodify Backend Assessment

A comprehensive FastAPI backend application featuring authentication, user management, posts integration with caching, background tasks, and gRPC services.

## 🚀 Features

- **Authentication & Authorization**: JWT-based auth with access/refresh tokens
- **User Management**: Registration, login, profile management
- **Admin Panel**: User administration with role-based access control
- **Posts Integration**: External API integration with Redis caching
- **Background Tasks**: Celery-powered async email sending
- **gRPC Service**: Token validation microservice
- **Database**: PostgreSQL with SQLAlchemy ORM and Alembic migrations
- **Caching**: Redis for performance optimization
- **API Documentation**: Automatic OpenAPI/Swagger documentation

## 🏗️ Architecture

```
├── app/
│   ├── api/v1/          # API endpoints
│   │   ├── auth/        # Authentication endpoints
│   │   ├── admin/       # Admin-only endpoints
│   │   ├── profile/     # User profile endpoints
│   │   └── posts/       # Posts endpoints
│   ├── core/            # Core configuration
│   │   ├── config.py    # Application settings
│   │   ├── database.py  # Database configuration
│   │   ├── security.py  # JWT & password utilities
│   │   ├── dependencies.py # Auth dependencies
│   │   └── celery_app.py   # Celery configuration
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   ├── grpc/           # gRPC server implementation
│   └── main.py         # FastAPI application
├── alembic/            # Database migrations
├── protos/             # Protocol buffer definitions
├── tests/              # Test suite
└── docker/             # Docker configurations
```

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.104+
- **Database**: PostgreSQL 15+ with SQLAlchemy
- **Cache**: Redis 7+
- **Task Queue**: Celery
- **Authentication**: JWT with python-jose
- **API Client**: httpx for external API calls
- **Validation**: Pydantic v2
- **Migration**: Alembic
- **Package Manager**: UV (ultra-fast Python package manager)
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- UV package manager
- Docker & Docker Compose (optional)
- PostgreSQL 15+ (if running locally)
- Redis 7+ (if running locally)

### Installation with UV

1. **Clone the repository**
```bash
git clone <repository-url>
cd arcodify-backend-assessment
```

2. **Install UV** (if not already installed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Install dependencies**
```bash
uv sync
```

4. **Environment setup**
```bash
cp .env.example .env
# Edit .env with your configurations
```

5. **Generate gRPC code**
```bash
uv run python -m grpc_tools.protoc -I./protos --python_out=./app/grpc --grpc_python_out=./app/grpc ./protos/auth.proto
```

6. **Database setup**
```bash
# Initialize Alembic (if not already done)
uv run alembic init alembic

# Generate and run migrations
uv run alembic revision --autogenerate -m "Initial migration"
uv run alembic upgrade head
```

7. **Run the application**
```bash
# Start Redis (if running locally)
redis-server

# Start Celery worker in another terminal
uv run celery -A app.core.celery_app worker --loglevel=info

# Start the FastAPI server
uv run uvicorn app.main:app --reload
```

### Docker Setup (Recommended)

1. **Clone and setup**
```bash
git clone <repository-url>
cd arcodify-backend-assessment
cp .env.example .env
```

2. **Start all services**
```bash
docker-compose up --build
```

This will start:
- PostgreSQL database on port 5432
- Redis on port 6379
- FastAPI API on port 8000
- gRPC server on port 50051
- Celery worker
- Flower (Celery monitoring) on port 5555

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

### Authentication Flow

1. **Register a new user**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "securepassword123"
  }'
```

2. **Login to get tokens**
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

3. **Use access token for protected endpoints**
```bash
curl -X GET "http://localhost:8000/api/v1/profile/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Admin Setup

To create an admin user, you can modify the user in the database:
```sql
UPDATE users SET is_admin = true WHERE email = 'admin@example.com';
```

## 🧪 Testing

### Run Tests
```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_auth.py -v
```

### Manual Testing Script
```bash
# Create a test script
cat > test_api.sh << 'EOF'
#!/bin/bash

BASE_URL="http://localhost:8000"

# Test registration
echo "Testing user registration..."
REGISTER_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123"
  }')
echo "Registration response: $REGISTER_RESPONSE"

# Test login
echo "Testing user login..."
LOGIN_RESPONSE=$(curl -s -X POST "${BASE_URL}/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }')
echo "Login response: $LOGIN_RESPONSE"

# Extract access token
ACCESS_TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

# Test protected endpoint
echo "Testing protected profile endpoint..."
PROFILE_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/v1/profile/me" \
  -H "Authorization: Bearer $ACCESS_TOKEN")
echo "Profile response: $PROFILE_RESPONSE"

# Test posts endpoint
echo "Testing posts endpoint..."
POSTS_RESPONSE=$(curl -s -X GET "${BASE_URL}/api/v1/posts?page=1&per_page=5")
echo "Posts response: $POSTS_RESPONSE"
EOF

chmod +x test_api.sh
./test_api.sh
```

## 🔧 Development

### Database Operations

```bash
# Create new migration
uv run alembic -c app/alembic.ini revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic -c app/alembic.ini upgrade head

# Rollback migration
uv run alembic -c app/alembic.ini -1

# View migration history
uv run alembic history
```

### Celery Operations

```bash
# Start worker
uv run celery -A app.core.celery_app worker --loglevel=info

# Start beat scheduler
uv run celery -A app.core.celery_app beat --loglevel=info

# Monitor with Flower
uv run celery -A app.core.celery_app flower

# Purge all tasks
uv run celery -A app.core.celery_app purge
```

### gRPC Testing

```bash
# Install grpcurl for testing
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Test token validation
grpcurl -plaintext -d '{"token": "YOUR_JWT_TOKEN"}' \
  localhost:50051 auth.AuthService/ValidateToken
```

## 🐳 Docker Commands

```bash
# Build and start all services
docker-compose up --build

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Run migrations in container
docker-compose exec api uv run alembic upgrade head

# Access database
docker-compose exec db psql -U arcodify -d arcodify_db

# Access Redis CLI
docker-compose exec redis redis-cli

# Stop all services
docker-compose down

# Clean up volumes
docker-compose down -v
```

## 📝 Environment Variables

Key environment variables (see `.env.example`):

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` |
| `SECRET_KEY` | JWT secret key | Required |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT access token expiry | `30` |
| `POSTS_API_URL` | External posts API URL | JSONPlaceholder |
| `CELERY_BROKER_URL` | Celery message broker | Redis |
| `DEBUG` | Enable debug mode | `False` |

## 🔍 Monitoring

- **Health Check**: `GET /health`
- **API Metrics**: Built-in request/response logging
- **Celery Monitoring**: Flower UI at http://localhost:5555
- **Database**: Standard PostgreSQL monitoring tools
- **Redis**: Redis CLI and monitoring commands

## 📋 Acceptance Tests Checklist

- [x] POST /auth/register creates user in DB, triggers Celery task
- [x] POST /auth/login issues access + refresh tokens
- [x] GET /profile/me fails without JWT, succeeds with token
- [x] GET /posts caches results in Redis, supports pagination + search
- [x] GET /admin/users requires admin token, returns paginated users
- [x] POST /admin/users/{id}/deactivate sets user inactive
- [x] gRPC ValidateToken returns valid/invalid response for JWT

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🔗 Links

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [UV Package Manager](https://github.com/astral-sh/uv)
