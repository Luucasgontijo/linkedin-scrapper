#!/bin/bash

# Production Deployment Script for VPS

echo "🚀 Deploying LinkedIn Scraper API to Production..."

# Update system
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Docker if not already installed
if ! command -v docker &> /dev/null; then
    echo "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Install Docker Compose if not already installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# Create application directory
APP_DIR="/opt/linkedin-scraper"
echo "Creating application directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown $USER:$USER $APP_DIR

# Copy files (assuming you've already uploaded them)
echo "Make sure you've uploaded the application files to $APP_DIR"

# Navigate to app directory
cd $APP_DIR

# Set proper permissions
sudo chown -R $USER:$USER .
chmod +x deploy.sh

# Configure firewall (if UFW is installed)
if command -v ufw &> /dev/null; then
    echo "Configuring firewall..."
    sudo ufw allow 22/tcp
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw allow 8080/tcp
    sudo ufw --force enable
fi

# Deploy with nginx reverse proxy
echo "Deploying with nginx reverse proxy..."
docker-compose --profile production up -d --build

# Wait for services to start
echo "Waiting for services to start..."
sleep 30

# Test the deployment
echo "Testing deployment..."
if curl -f http://localhost:8080/ > /dev/null 2>&1; then
    echo "✅ Direct API access working"
else
    echo "❌ Direct API access failed"
fi

if curl -f http://localhost/ > /dev/null 2>&1; then
    echo "✅ Nginx reverse proxy working"
else
    echo "❌ Nginx reverse proxy failed"
fi

# Show running containers
echo "📋 Running containers:"
docker-compose ps

# Show logs
echo "📋 Recent logs:"
docker-compose logs --tail=20

echo "🎉 Production deployment complete!"
echo "API is available at:"
echo "  - Direct: http://YOUR_VPS_IP:8080"
echo "  - Via nginx: http://YOUR_VPS_IP"
echo ""
echo "To monitor logs: docker-compose logs -f linkedin-scraper"
echo "To restart: docker-compose restart"
echo "To stop: docker-compose down"
