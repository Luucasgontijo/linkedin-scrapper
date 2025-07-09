#!/bin/bash

# LinkedIn Scraper API Deployment Script

echo "🚀 Deploying LinkedIn Scraper API..."

# Stop existing containers
echo "Stopping existing containers..."
docker-compose down

# Build and start containers
echo "Building and starting containers..."
docker-compose up -d --build

# Wait for services to be ready
echo "Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "Checking service status..."
docker-compose ps

# Test API
echo "Testing API endpoint..."
curl -f http://localhost:8080/ || echo "❌ API not responding"

echo "✅ Deployment complete!"
echo "API is available at: http://localhost:8080"
echo "With nginx: http://localhost"

# Show logs
echo "📋 Recent logs:"
docker-compose logs --tail=20 linkedin-scraper
