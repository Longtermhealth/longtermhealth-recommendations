#!/bin/bash
echo "Checking Azure Web App logs for usertest-dev slot..."
az webapp log tail --name lthrecommendation --slot usertest-dev --resource-group rg-sponsorship --timeout 30