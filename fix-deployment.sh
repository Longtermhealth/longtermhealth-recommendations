#!/bin/bash
echo "Fixing deployment..."

# Update startup command
az webapp config set \
  --name lthrecommendation \
  --slot usertest-dev \
  --resource-group rg-sponsorship \
  --startup-file "cd /home/site/wwwroot && export PYTHONPATH=/home/site/wwwroot/src && pip install -r requirements.txt && gunicorn --bind 0.0.0.0:8000 --timeout 600 --workers 1 --chdir src app:app"

# Restart
az webapp restart \
  --name lthrecommendation \
  --slot usertest-dev \
  --resource-group rg-sponsorship

echo "Done! Waiting for service to start..."
sleep 30

# Test
curl -I https://lthrecommendation-usertest-dev-h4cxg6cmfbfbgwc3.germanywestcentral-01.azurewebsites.net/health