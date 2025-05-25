#!/usr/bin/env python3
"""
Migration script to transition from old app.py to refactored structure.

This script helps identify code that needs to be migrated and provides
guidance on how to use the new structure.
"""

import os
import sys


def check_imports():
    """Check if old imports are still being used"""
    print("Checking for old imports...")
    
    old_imports = [
        "from app import",
        "from main_flask import",
        "import app",
        "import main_flask"
    ]
    
    issues = []
    
    # Check Python files
    for root, dirs, files in os.walk("src"):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    for old_import in old_imports:
                        if old_import in content:
                            issues.append(f"{filepath}: Contains '{old_import}'")
    
    if issues:
        print("\n❌ Found old imports:")
        for issue in issues:
            print(f"  - {issue}")
        print("\n✅ Fix: Update imports to use new structure:")
        print("  - from src.api import create_app")
        print("  - from src.services.action_plan_service import ActionPlanService")
        print("  - from src.models.health_score import HealthScores")
    else:
        print("✅ No old imports found")
    
    return len(issues) == 0


def check_environment():
    """Check if environment variables are properly set"""
    print("\nChecking environment variables...")
    
    required_vars = [
        "TYPEFORM_API_KEY",
        "STRAPI_API_KEY",
        "FORM_ID"
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print(f"\n❌ Missing environment variables: {', '.join(missing)}")
        print("✅ Fix: Set these in your .env file or environment")
    else:
        print("✅ All required environment variables are set")
    
    return len(missing) == 0


def check_data_files():
    """Check if required data files exist"""
    print("\nChecking data files...")
    
    required_files = [
        "./data/strapi_all_routines.json"
    ]
    
    missing = []
    for file in required_files:
        if not os.path.exists(file):
            missing.append(file)
    
    if missing:
        print(f"\n❌ Missing data files: {', '.join(missing)}")
        print("✅ Fix: Ensure these files exist before running")
    else:
        print("✅ All required data files exist")
    
    return len(missing) == 0


def migration_guide():
    """Print migration guide"""
    print("\n" + "="*60)
    print("MIGRATION GUIDE")
    print("="*60)
    
    print("\n1. UPDATE YOUR CODE:")
    print("   - Replace direct function calls with service methods")
    print("   - Use models for data validation")
    print("   - Handle exceptions properly")
    
    print("\n2. UPDATE DEPLOYMENT:")
    print("   - Update Dockerfile CMD to use new entry point")
    print("   - Update any scripts that reference app.py")
    print("   - Update environment variables if needed")
    
    print("\n3. TESTING:")
    print("   - Run: python -m src.run (development)")
    print("   - Test all endpoints")
    print("   - Check logs for any issues")
    
    print("\n4. EXAMPLE USAGE:")
    print("""
# Old way:
from app import process_action_plan
result = process_action_plan(host)

# New way:
from src.services.action_plan_service import ActionPlanService
service = ActionPlanService()
result = service.create_new_plan(host)
""")


def main():
    """Run migration checks"""
    print("🚀 LTH Recommendation Service Migration Check")
    print("="*60)
    
    all_good = True
    
    all_good &= check_imports()
    all_good &= check_environment()
    all_good &= check_data_files()
    
    migration_guide()
    
    if all_good:
        print("\n✅ Ready to use refactored structure!")
    else:
        print("\n❌ Please fix the issues above before proceeding")
        sys.exit(1)


if __name__ == "__main__":
    main()