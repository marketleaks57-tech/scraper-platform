# Deployment Fix Guide

## Quick Start (TL;DR)

If you just want to get the server running NOW:

```bash
cd /opt/scraper-platform

# Fix git
git config pull.rebase true
git pull origin main

# Create .env file
chmod +x scripts/create_env.sh
./scripts/create_env.sh

# Deploy
sudo docker compose down
sudo docker compose build --no-cache
sudo docker compose up -d

# Wait 30 seconds
sleep 30

# Verify
curl http://localhost:8000/health
sudo docker compose ps
```

---

## Issues Identified

1. **Git divergent branches** - preventing code pull
2. **Missing `.env` file** - API requires `DB_URL` and `SCRAPER_SECRET_KEY`
3. **Dockerfile missing scraper-deps** - Build fails because requirements.txt references scraper-deps/requirements.txt
4. **API health endpoint** - Fixed (now available at both `/health` and `/api/health`)
5. **Connection reset** - API startup failing due to missing environment variables

## Step-by-Step Fix

### 1. Resolve Git Divergence

```bash
cd /opt/scraper-platform

# Option A: Rebase (recommended - cleaner history)
git config pull.rebase true
git pull origin main

# Option B: If rebase fails, use merge
git config pull.rebase false
git pull origin main

# Option C: If you want to discard local changes
git fetch origin
git reset --hard origin/main
```

### 2. Create Missing `.env` File

The API requires environment variables. Create `.env` file:

```bash
cd /opt/scraper-platform

cat > .env << 'EOF'
# Database Configuration
DB_URL=postgresql://scraper:scraper123@postgres:5432/scraperdb
DB_HOST=postgres
DB_USER=scraper
DB_PASSWORD=scraper123
DB_NAME=scraperdb

# API Security
SCRAPER_SECRET_KEY=your-secret-key-change-this-in-production

# Optional: Additional Configuration
LOG_LEVEL=INFO
PYTHONPATH=/app
EOF

chmod 600 .env
```

**IMPORTANT**: Change `SCRAPER_SECRET_KEY` to a strong random value in production:

```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Add Healthcheck to docker-compose.yml

Add healthcheck configuration to the API service:

```yaml
# Edit docker-compose.yml, update the api service:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    command: uvicorn src.api.app:app --host 0.0.0.0 --port 8000
    env_file:
      - .env
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./:/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 5
      start_period: 30s
```

Also add healthchecks to postgres and redis if not present:

```yaml
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-scraper}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-scraper123}
      POSTGRES_DB: ${POSTGRES_DB:-scraperdb}
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U scraper"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7
    ports:
      - "6379:6379"
    volumes:
      - redisdata:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
```

### 4. Complete Deployment

```bash
cd /opt/scraper-platform

# Pull latest code (after fixing git)
git pull origin main

# Run migrations
sudo docker compose run --rm \
  -e DB_HOST=postgres \
  -e DB_USER=scraper \
  -e DB_PASSWORD=scraper123 \
  -e DB_NAME=scraperdb \
  api sh -c "chmod +x /app/scripts/migrate.sh && /app/scripts/migrate.sh"

# Rebuild API with latest code
sudo docker compose build api

# Start services with healthcheck
sudo docker compose up -d

# Wait for services to be healthy (30-60 seconds)
sleep 30

# Check status
sudo docker compose ps

# Check API logs
sudo docker compose logs api | tail -n 50

# Verify health endpoints
curl -v http://localhost:8000/health
curl -v http://localhost:8000/api/health

# Test API endpoints
curl http://localhost:8000/api/source-health
curl http://localhost:8000/api/runs
```

### 5. Troubleshooting

If API still fails to start:

```bash
# Check API logs for errors
sudo docker compose logs api --tail=100 --follow

# Check environment variables inside container
sudo docker compose exec api env | grep -E '(DB_|SCRAPER_)'

# Test database connectivity
sudo docker compose exec postgres psql -U scraper -d scraperdb -c '\dt'

# Restart services
sudo docker compose restart api

# If all else fails, clean restart
sudo docker compose down
sudo docker compose up -d
```

### 6. Verify Deployment Success

✅ All containers should show as "healthy":
```bash
sudo docker compose ps
# api-1        Up (healthy)
# postgres-1   Up (healthy)
# redis-1      Up (healthy)
```

✅ Health endpoints should return 200 OK:
```bash
curl http://localhost:8000/health
# {"status":"ok"}

curl http://localhost:8000/api/health
# {"status":"ok"}
```

✅ API endpoints should work:
```bash
curl http://localhost:8000/api/source-health
# [...health data...]
```

## Quick Reference Commands

```bash
# Code-only deploy (no DB changes)
git pull origin main
sudo docker compose build api
sudo docker compose up -d api

# Full deploy with migrations
git pull origin main
sudo docker compose run --rm api sh -c "chmod +x /app/scripts/migrate.sh && /app/scripts/migrate.sh"
sudo docker compose build api
sudo docker compose up -d

# Check logs
sudo docker compose logs -f api

# Restart single service
sudo docker compose restart api

# Full restart
sudo docker compose down && sudo docker compose up -d
```

## Common Issues

### "Connection reset by peer"
- API is starting but not ready yet (wait 30s)
- Missing environment variables (check `.env` file)
- Startup checks failing (check logs)

### "fatal: Need to specify how to reconcile divergent branches"
- Run: `git config pull.rebase true` then `git pull origin main`
- Or discard local changes: `git reset --hard origin/main`

### "Missing required environment variables"
- Create `.env` file with `DB_URL` and `SCRAPER_SECRET_KEY`
- Verify with: `docker compose config` (shows resolved env vars)

### API shows "unhealthy"
- Check healthcheck endpoint: `curl http://localhost:8000/health`
- Increase `start_period` in healthcheck (API may need more time)
- Check logs: `docker compose logs api`
