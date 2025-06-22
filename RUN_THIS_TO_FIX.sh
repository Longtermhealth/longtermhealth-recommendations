#!/bin/bash
echo "=== FIXING AZURE DEPLOYMENT ==="

# 1. Commit and push changes
cd /Users/janoschgrellner/PycharmProjects/lth-rec
git add -A
git commit --no-gpg-sign -m "Fix deployment configuration and add startup scripts"
git push origin development

# 2. Update Azure startup command
echo "Updating startup command..."
az webapp config set \
  --name lthrecommendation \
  --slot usertest-dev \
  --resource-group rg-sponsorship \
  --startup-file "cd /home/site/wwwroot && export PYTHONPATH=/home/site/wwwroot/src && pip install -r requirements.txt && gunicorn --bind 0.0.0.0:8000 --timeout 600 app:app"

# 3. Restart the app
echo "Restarting webapp..."
az webapp restart \
  --name lthrecommendation \
  --slot usertest-dev \
  --resource-group rg-sponsorship

echo "Done! Waiting 30 seconds for service to start..."
sleep 30

# 4. Test the service
echo "Testing service..."
curl -I https://lthrecommendation-usertest-dev-h4cxg6cmfbfbgwc3.germanywestcentral-01.azurewebsites.net/health

echo ""
echo "Service URL: https://lthrecommendation-usertest-dev-h4cxg6cmfbfbgwc3.germanywestcentral-01.azurewebsites.net/"
echo "Webhook URL: https://lthrecommendation-usertest-dev-h4cxg6cmfbfbgwc3.germanywestcentral-01.azurewebsites.net/survey"