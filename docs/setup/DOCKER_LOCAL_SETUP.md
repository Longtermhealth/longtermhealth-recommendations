# Docker Local Setup Guide

## Quick Start

### 1. Build and run with docker-compose

```bash
# Load environment variables from .env file
docker-compose --env-file .env up --build
```

### 2. Or build manually

```bash
# Build the Docker image
docker build -t lth-recommendation .

# Run with environment variables from .env file
docker run --env-file .env -p 5003:5003 lth-recommendation
```

## Step-by-Step Guide

### 1. Prepare your environment

Make sure your `.env` file exists with all required variables:
```bash
# Check if .env exists
ls -la .env

# View environment variable names (without values)
cat .env | grep -E "^[A-Z]" | sed 's/=.*/=<value>/'
```

### 2. Build the Docker image

```bash
# Build with docker-compose (recommended)
docker-compose build

# Or build directly
docker build -t lth-recommendation .
```

### 3. Run the container

**Option A: Using docker-compose (recommended)**
```bash
# Run in foreground to see logs
docker-compose up

# Or run in background
docker-compose up -d

# View logs if running in background
docker-compose logs -f
```

**Option B: Using docker run**
```bash
# Run with .env file
docker run --env-file .env -p 5003:5003 lth-recommendation
```

### 4. Test the endpoints

Once running, test the endpoints:

```bash
# Health check
curl http://localhost:5003/

# Event endpoint
curl -X POST http://localhost:5003/event \
  -H "Content-Type: application/json" \
  -d '{
    "eventEnum": "RECALCULATE_ACTION_PLAN",
    "eventPayload": {
      "actionPlanUniqueId": "test-123",
      "accountId": 12345
    }
  }'
```

## Docker Commands Reference

### Container Management
```bash
# List running containers
docker ps

# Stop the container
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View container logs
docker-compose logs -f web

# Enter the container
docker-compose exec web bash
```

### Debugging
```bash
# Check if port 5003 is available
lsof -i :5003

# View detailed container info
docker-compose ps

# Rebuild without cache
docker-compose build --no-cache
```

## Common Issues

### Port already in use
```bash
# Find what's using port 5003
lsof -i :5003

# Kill the process
kill -9 <PID>
```

### Environment variables not loading
```bash
# Verify .env file is being read
docker-compose config
```

### Permission issues
```bash
# If you get permission errors, try:
sudo docker-compose up
```

## Development Tips

1. **Live reload**: The current setup mounts the local directory, so code changes will be reflected (but you need to restart the container).

2. **Debug mode**: The Dockerfile sets up debug mode when FLASK_ENV=development.

3. **Logs**: Container logs will show all Flask output including request logs.

4. **Stopping**: Use `Ctrl+C` to stop when running in foreground, or `docker-compose down` when running detached.