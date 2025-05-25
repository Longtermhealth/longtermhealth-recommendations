# LTH Recommendation Service - Refactored Structure

## Overview

This is the refactored version of the LTH Recommendation Service with improved architecture, separation of concerns, and better maintainability.

## Architecture

### Directory Structure

```
src/
├── api/                    # API layer
│   ├── routes/            # Route handlers
│   │   ├── health.py      # Health check endpoint
│   │   ├── webhook.py     # Typeform webhook handler
│   │   └── event.py       # Event handler (recalculate, renew)
│   └── middleware/        # Middleware components
│       └── error_handler.py # Global error handling
├── services/              # Business logic layer
│   ├── action_plan_service.py    # Action plan operations
│   ├── health_score_service.py   # Health score calculations
│   └── routine_service.py        # Routine management
├── models/                # Data models
│   ├── action_plan.py     # Action plan models
│   ├── health_score.py    # Health score models
│   └── routine_stats.py   # Routine statistics models
├── utils/                 # Utilities
│   └── logger.py          # Logging configuration
├── config.py              # Application configuration
├── exceptions.py          # Custom exceptions
└── run.py                 # Application entry point
```

### Key Improvements

1. **Separation of Concerns**
   - Routes only handle HTTP concerns
   - Business logic moved to service layer
   - Data validation using models

2. **Error Handling**
   - Custom exception hierarchy
   - Centralized error handling middleware
   - Proper HTTP status codes

3. **Configuration Management**
   - Environment-specific configurations
   - Clean configuration classes
   - No hardcoded values

4. **Type Safety**
   - Data models with validation
   - Type hints throughout
   - Clear data contracts

5. **Logging**
   - Structured logging
   - Different log levels
   - No print statements

6. **Testability**
   - Services can be tested independently
   - Mock-friendly architecture
   - Clear dependencies

## Usage

### Running the Application

```bash
# Development
export FLASK_ENV=development
python -m src.run

# Production
export FLASK_ENV=production
gunicorn -w 4 -b 0.0.0.0:5003 "src.api:create_app()"
```

### Environment Variables

Required environment variables:
- `FLASK_ENV`: Application environment (development/production)
- `TYPEFORM_API_KEY`: Typeform API key
- `STRAPI_API_KEY`: Strapi API key
- `FORM_ID`: Typeform form ID
- Additional keys as defined in `config.py`

### API Endpoints

- `GET /`: Health check
- `POST /webhook`: Handle Typeform submissions
- `POST /event`: Handle app events (recalculate, renew)

## Development

### Adding New Features

1. **New Route**: Add to `api/routes/`
2. **Business Logic**: Add service to `services/`
3. **Data Model**: Add to `models/`
4. **Configuration**: Update `config.py`

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src

# Type checking
mypy src/

# Linting
flake8 src/
```

## Migration Notes

The refactored code maintains compatibility with existing endpoints while providing:
- Better error messages
- Improved performance
- Easier debugging
- Better maintainability

All existing functionality is preserved with the same API contracts.