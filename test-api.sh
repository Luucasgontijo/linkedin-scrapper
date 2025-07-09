#!/bin/bash

# API Test Script
# Tests all endpoints to ensure the API is working correctly

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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Default API URL
API_URL=${1:-"http://localhost:8080"}

print_status "Testing LinkedIn Scraper API at: $API_URL"

# Test 1: Health Check
print_status "Testing health check endpoint..."
if curl -s -f "$API_URL/" > /dev/null; then
    print_status "✅ Health check passed"
    curl -s "$API_URL/" | jq .
else
    print_error "❌ Health check failed"
    exit 1
fi

echo ""

# Test 2: Profile endpoint (with a sample profile)
print_status "Testing profile endpoint..."
PROFILE_RESPONSE=$(curl -s "$API_URL/api/profile/williamhgates" || echo "error")
if echo "$PROFILE_RESPONSE" | jq . > /dev/null 2>&1; then
    print_status "✅ Profile endpoint is accessible"
    echo "$PROFILE_RESPONSE" | jq '.status'
else
    print_warning "⚠️ Profile endpoint may require authentication"
fi

echo ""

# Test 3: Search people endpoint
print_status "Testing search people endpoint..."
SEARCH_RESPONSE=$(curl -s "$API_URL/api/search/people?keywords=developer" || echo "error")
if echo "$SEARCH_RESPONSE" | jq . > /dev/null 2>&1; then
    print_status "✅ Search people endpoint is accessible"
    echo "$SEARCH_RESPONSE" | jq '.status'
else
    print_warning "⚠️ Search people endpoint may require authentication"
fi

echo ""

# Test 4: Search companies endpoint
print_status "Testing search companies endpoint..."
COMPANY_RESPONSE=$(curl -s "$API_URL/api/search/companies?keywords=technology" || echo "error")
if echo "$COMPANY_RESPONSE" | jq . > /dev/null 2>&1; then
    print_status "✅ Search companies endpoint is accessible"
    echo "$COMPANY_RESPONSE" | jq '.status'
else
    print_warning "⚠️ Search companies endpoint may require authentication"
fi

echo ""

# Test 5: URN to URL conversion endpoint
print_status "Testing URN to URL conversion endpoint..."
URN_RESPONSE=$(curl -s "$API_URL/api/urn-to-url?urn=urn:li:person:ACoAABKZp4kBjGQKMGJ-MnOKUTtWwx6wPkZkGUU" || echo "error")
if echo "$URN_RESPONSE" | jq . > /dev/null 2>&1; then
    print_status "✅ URN to URL conversion endpoint is accessible"
    echo "$URN_RESPONSE" | jq '.status'
    if [ "$(echo "$URN_RESPONSE" | jq -r '.status')" = "success" ]; then
        echo "URL: $(echo "$URN_RESPONSE" | jq -r '.data.url')"
    fi
else
    print_warning "⚠️ URN to URL conversion endpoint error"
fi

echo ""

# Test 6: Accounts status endpoint
print_status "Testing accounts status endpoint..."
ACCOUNTS_RESPONSE=$(curl -s "$API_URL/api/accounts/status" || echo "error")
if echo "$ACCOUNTS_RESPONSE" | jq . > /dev/null 2>&1; then
    print_status "✅ Accounts status endpoint is accessible"
    echo "$ACCOUNTS_RESPONSE" | jq '.status'
    if [ "$(echo "$ACCOUNTS_RESPONSE" | jq -r '.status')" = "success" ]; then
        echo "Total accounts: $(echo "$ACCOUNTS_RESPONSE" | jq -r '.data.total_accounts')"
        echo "Active accounts: $(echo "$ACCOUNTS_RESPONSE" | jq -r '.data.active_accounts')"
        echo "Current account: $(echo "$ACCOUNTS_RESPONSE" | jq -r '.data.current_account')"
    fi
else
    print_warning "⚠️ Accounts status endpoint error"
fi

echo ""

print_status "API testing completed!"
print_status "Note: Some endpoints may require LinkedIn authentication to return data."
print_status "If you see authentication errors, check your .env file configuration."
