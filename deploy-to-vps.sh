#!/bin/bash

# Quick VPS Deployment Script
# Usage: ./deploy-to-vps.sh user@your-vps-ip

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if VPS address is provided
if [ -z "$1" ]; then
    print_error "Usage: $0 user@your-vps-ip"
    print_error "Example: $0 ubuntu@192.168.1.100"
    exit 1
fi

VPS_HOST="$1"
VPS_DIR="/opt/linkedin-scraper"

print_status "Deploying LinkedIn Scraper API to VPS: $VPS_HOST"

# Create directory on VPS
print_status "Creating directory on VPS..."
ssh $VPS_HOST "sudo mkdir -p $VPS_DIR && sudo chown \$USER:\$USER $VPS_DIR"

# Upload files to VPS
print_status "Uploading files to VPS..."
rsync -avz --exclude='.git' \
           --exclude='__pycache__' \
           --exclude='*.pyc' \
           --exclude='venv' \
           --exclude='.DS_Store' \
           --exclude='node_modules' \
           . $VPS_HOST:$VPS_DIR/

# Set executable permissions
print_status "Setting permissions..."
ssh $VPS_HOST "cd $VPS_DIR && chmod +x *.sh"

# Deploy the application
print_status "Deploying application..."
ssh $VPS_HOST "cd $VPS_DIR && ./deploy-production.sh"

print_status "✅ Deployment completed successfully!"
print_status "Your API is now available at:"
print_status "  - Direct: http://$(echo $VPS_HOST | cut -d'@' -f2):8080"
print_status "  - Via nginx: http://$(echo $VPS_HOST | cut -d'@' -f2)"
print_status ""
print_status "To check status: ssh $VPS_HOST 'cd $VPS_DIR && docker-compose ps'"
print_status "To view logs: ssh $VPS_HOST 'cd $VPS_DIR && docker-compose logs -f linkedin-scraper'"
