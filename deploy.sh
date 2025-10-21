#!/bin/bash
set -e

echo "🚀 Starting EPG Merger deployment..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
fi

# Check if Docker Compose is installed (plugin version)
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Installing Docker Compose..."
    apt-get update
    apt-get install -y docker-compose-plugin
fi

# Use docker compose (with space) - new plugin version
DOCKER_COMPOSE="docker compose"

# Pull latest changes
echo "📥 Pulling latest changes from GitHub..."
git pull origin main

# Stop existing containers
echo "🛑 Stopping existing containers..."
$DOCKER_COMPOSE -f docker-compose.prod.yml down || true

# Build and start containers
echo "🔨 Building and starting containers..."
$DOCKER_COMPOSE -f docker-compose.prod.yml up --build -d

# Wait for container to be healthy
echo "⏳ Waiting for container to be healthy..."
sleep 10

# Show status
echo "📊 Container status:"
$DOCKER_COMPOSE -f docker-compose.prod.yml ps

# Show logs
echo "📝 Recent logs:"
$DOCKER_COMPOSE -f docker-compose.prod.yml logs --tail=20

# Get container IP
CONTAINER_IP=$(docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' epg-merger-prod 2>/dev/null || echo "localhost")

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Access your EPG Merger at:"
echo "   http://$(hostname -I | awk '{print $1}'):5000"
echo "   http://${CONTAINER_IP}:5000"
echo ""
echo "📡 EPG URLs will be:"
echo "   http://$(hostname -I | awk '{print $1}'):5000/api/epg-files/[EPG_ID]/download"
echo ""
echo "📊 View logs: docker compose -f docker-compose.prod.yml logs -f"
echo "🛑 Stop: docker compose -f docker-compose.prod.yml down"
echo "🔄 Restart: docker compose -f docker-compose.prod.yml restart"

