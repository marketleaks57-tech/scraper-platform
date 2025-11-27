#!/usr/bin/env bash
# Deployment script for scraper-platform
# Usage: ./scripts/deploy.sh [code-only|full]

set -euo pipefail

cd "$(dirname "$0")/.."

DEPLOY_TYPE="${1:-full}"

echo "=== Scraper Platform Deployment ==="
echo "Deploy type: $DEPLOY_TYPE"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Creating .env from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "IMPORTANT: Edit .env and set SCRAPER_SECRET_KEY to a secure random value!"
        echo "Generate one with: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
        exit 1
    else
        echo "ERROR: .env.example not found either. Cannot proceed."
        exit 1
    fi
fi

# Pull latest code
echo "Pulling latest code from main branch..."
if ! git pull origin main; then
    echo ""
    echo "Git pull failed. Attempting to resolve divergent branches..."
    echo "Setting pull strategy to rebase..."
    git config pull.rebase true
    if ! git pull origin main; then
        echo "ERROR: Git pull still failing. Manual intervention required."
        echo "Options:"
        echo "  1. Merge: git config pull.rebase false && git pull origin main"
        echo "  2. Discard local changes: git reset --hard origin/main"
        exit 1
    fi
fi

# Run migrations if full deploy
if [ "$DEPLOY_TYPE" = "full" ]; then
    echo ""
    echo "Running database migrations..."
    sudo docker compose run --rm \
        -e DB_HOST=postgres \
        -e DB_USER=scraper \
        -e DB_PASSWORD=scraper123 \
        -e DB_NAME=scraperdb \
        api sh -c "chmod +x /app/scripts/migrate.sh && /app/scripts/migrate.sh"
fi

# Rebuild services
echo ""
echo "Rebuilding Docker images..."
if [ "$DEPLOY_TYPE" = "code-only" ]; then
    sudo docker compose build api frontend
else
    sudo docker compose build
fi

# Start services
echo ""
echo "Starting services..."
sudo docker compose up -d

# Wait for services to be healthy
echo ""
echo "Waiting for services to become healthy (max 60s)..."
for i in {1..12}; do
    sleep 5
    if sudo docker compose ps | grep -q "unhealthy"; then
        echo "  Waiting... ($((i*5))s)"
    else
        echo "  Services appear healthy!"
        break
    fi
done

# Check status
echo ""
echo "=== Service Status ==="
sudo docker compose ps

# Check API logs
echo ""
echo "=== Recent API Logs ==="
sudo docker compose logs api --tail=20

# Test health endpoints
echo ""
echo "=== Health Check Tests ==="

sleep 5  # Give API a bit more time

if curl -sf http://localhost:8000/health > /dev/null; then
    echo "✓ /health endpoint: OK"
    curl -s http://localhost:8000/health | jq . || curl -s http://localhost:8000/health
else
    echo "✗ /health endpoint: FAILED"
fi

if curl -sf http://localhost:8000/api/health > /dev/null; then
    echo "✓ /api/health endpoint: OK"
    curl -s http://localhost:8000/api/health | jq . || curl -s http://localhost:8000/api/health
else
    echo "✗ /api/health endpoint: FAILED"
fi

echo ""
echo "=== Deployment Complete ==="
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo ""
echo "Troubleshooting:"
echo "  Logs: sudo docker compose logs -f api"
echo "  Restart: sudo docker compose restart api"
echo "  Status: sudo docker compose ps"
