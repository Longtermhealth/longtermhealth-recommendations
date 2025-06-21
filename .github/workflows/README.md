# GitHub Actions Workflows (Disabled)

The GitHub Actions workflows in this directory have been disabled because this project uses Azure Pipelines for deployment.

## Disabled Workflows:
- `deploy-recommendation-service.yml.disabled` - Was for deploying the main recommendation service
- `deploy-user-test-service.yml.disabled` - Was for deploying the user test service

## Active Deployment Method:
This project uses **Azure Pipelines** (configured in `azure-pipelines.yml`) for all deployments.

To deploy:
- Push to `development` branch for dev deployment
- Push to `main` branch for production deployment
- Use `[user-test]` in commit message to deploy user test service
- Use `[deploy-all]` in commit message to deploy all services

## Re-enabling GitHub Actions:
If you want to switch to GitHub Actions in the future:
1. Set up the `AZURE_CREDENTIALS` secret in GitHub repository settings
2. Rename the `.yml.disabled` files back to `.yml`
3. Configure all required secrets as documented in DEPLOYMENT.md