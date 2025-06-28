# Host-Based Environment Handling

## Overview

The LTH Recommendation Service uses host-based environment detection to ensure that the correct Strapi routines file is loaded based on the deployment environment. This prevents development data from being used in production and vice versa.

## How It Works

### 1. Host Detection

When a webhook is received, the system detects the host from the request:

```python
# In webhook_route.py
host = request.host
logger.info(f"Received webhook on host: {host}")
```

### 2. Environment Determination

The host is passed to the scheduler, which determines the environment:

```python
# In scheduler.py main() function
if host == "lthrecommendation-dev-g2g0hmcqdtbpg8dw.germanywestcentral-01.azurewebsites.net":
    app_env = "development"
else:
    app_env = "production"
```

### 3. Environment-Specific Routine Loading

Based on the environment, different routine files are loaded:

```python
# In filter_service.py main() function
if app_env == "development":
    routines = load_routines_dev()  # Loads from ./data/environments/dev/strapi_all_routines_dev.json
else:
    routines = load_routines_staging()  # Loads from ./data/environments/staging/strapi_all_routines_staging.json
```

### 4. Flask Configuration

The Flask application also uses environment-based configuration:

```python
# Environment is determined by FLASK_ENV environment variable
config_name = os.getenv('FLASK_ENV', 'production')

# Different config classes for each environment
- DevelopmentConfig: Uses dev routines file
- ProductionConfig: Uses staging routines file
```

## File Structure

```
data/
├── strapi_all_routines.json          # Legacy/fallback file
├── environments/
│   ├── dev/
│   │   └── strapi_all_routines_dev.json    # Development routines
│   └── staging/
│       └── strapi_all_routines_staging.json # Staging/Production routines
```

## Flow Diagram

```
1. Typeform Webhook → Flask App
   ↓
2. Extract host from request
   ↓
3. Pass host to scheduler.main(host)
   ↓
4. Determine app_env based on host
   ↓
5. Pass app_env to filter_service.main(app_env)
   ↓
6. Load appropriate routines file
   ↓
7. Process action plan with correct data
```

## Environment Mapping

| Host | Environment | Routines File |
|------|-------------|---------------|
| lthrecommendation-dev-*.azurewebsites.net | development | strapi_all_routines_dev.json |
| Any other host | production | strapi_all_routines_staging.json |

## Key Functions

### webhook_route.py
- Receives webhook
- Extracts host
- Calls `process_action_plan(host)`

### scheduler.py
- `main(host)`: Determines environment from host
- Passes environment to filter service

### filter_service.py
- `main(app_env)`: Loads environment-specific routines
- `load_routines_dev()`: Loads development routines
- `load_routines_staging()`: Loads staging/production routines

### config.py
- `DevelopmentConfig`: Points to dev routines file
- `ProductionConfig`: Points to staging routines file

## Testing

To test different environments locally:

1. Set FLASK_ENV environment variable:
   ```bash
   export FLASK_ENV=development  # For dev routines
   export FLASK_ENV=production   # For staging routines
   ```

2. Or simulate different hosts in testing by passing the host parameter directly to scheduler.main()

## Important Notes

1. The staging routines file is used for both staging and production environments
2. The old `strapi_all_routines.json` file is kept as a fallback but should not be actively used
3. Always ensure the correct environment files are up to date before deployment
4. The host detection is case-sensitive and must match exactly