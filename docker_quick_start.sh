#!/bin/bash

echo "=== Docker Quick Start for LTH Recommendation Service ==="
echo ""
echo "This script will help you run the application with Docker."
echo ""

# Step 1: Build the image
echo "Step 1: Building Docker image (this may take a few minutes on first run)..."
echo "Running: docker-compose build"
echo ""
echo "To build, run:"
echo "  docker-compose build"
echo ""

# Step 2: Run the container
echo "Step 2: Running the application..."
echo "To run, use:"
echo "  docker-compose up"
echo ""

# Step 3: Alternative - run in background
echo "Or run in background:"
echo "  docker-compose up -d"
echo "  docker-compose logs -f  # to see logs"
echo ""

# Step 4: Test
echo "Step 3: Test the application"
echo "Once running, test with:"
echo "  curl http://localhost:5003/"
echo ""

echo "=== Complete Docker Commands ==="
echo ""
echo "# 1. Build and run in one command (foreground - see logs):"
echo "docker-compose up --build"
echo ""
echo "# 2. Build and run in background:"
echo "docker-compose up -d --build"
echo ""
echo "# 3. View logs:"
echo "docker-compose logs -f"
echo ""
echo "# 4. Stop the application:"
echo "docker-compose down"
echo ""
echo "# 5. Remove everything and start fresh:"
echo "docker-compose down -v"
echo "docker-compose build --no-cache"
echo "docker-compose up"