#!/bin/bash

echo "=== LTH Recommendation Service - Docker Runner ==="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${RED}Error: .env file not found!${NC}"
    echo "Please create a .env file with your environment variables"
    exit 1
fi

# Kill any existing process on port 5003
echo -e "${YELLOW}Checking port 5003...${NC}"
if lsof -i :5003 > /dev/null 2>&1; then
    echo "Port 5003 is in use. Stopping existing processes..."
    docker-compose down 2>/dev/null || true
    lsof -i :5003 | grep LISTEN | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    sleep 2
fi

# Build and run with docker-compose
echo -e "${GREEN}Building Docker image...${NC}"
docker-compose build

echo -e "${GREEN}Starting application...${NC}"
docker-compose up -d

# Wait for app to start
echo -e "${YELLOW}Waiting for application to start...${NC}"
sleep 5

# Test the health endpoint
echo -e "${GREEN}Testing health endpoint...${NC}"
if curl -s http://localhost:5003/ | jq '.' 2>/dev/null; then
    echo -e "${GREEN}✓ Application is running successfully!${NC}"
else
    echo -e "${RED}✗ Application health check failed${NC}"
    echo "Showing logs:"
    docker-compose logs --tail=50
fi

echo ""
echo "=== Quick Reference ==="
echo "View logs:           docker-compose logs -f"
echo "Stop application:    docker-compose down"
echo "Restart:            docker-compose restart"
echo "Enter container:     docker-compose exec web bash"
echo ""
echo "Test endpoints:"
echo "  curl http://localhost:5003/"
echo "  curl -X POST http://localhost:5003/event -H 'Content-Type: application/json' -d '{...}'"