#!/usr/bin/env python3
"""Run all tests for the refactored application"""

import sys
import subprocess
import os


def run_tests():
    """Run pytest with appropriate options"""
    
    # Set environment for testing
    os.environ['FLASK_ENV'] = 'testing'
    
    # Pytest arguments
    args = [
        'pytest',
        '-v',  # Verbose
        '--tb=short',  # Shorter traceback
        '--color=yes',  # Colored output
        'tests/',  # Test directory
    ]
    
    # Add coverage if requested
    if '--coverage' in sys.argv:
        args.extend([
            '--cov=src',
            '--cov-report=term-missing',
            '--cov-report=html'
        ])
    
    # Add specific test file if provided
    if len(sys.argv) > 1 and sys.argv[1] != '--coverage':
        args.append(sys.argv[1])
    
    print(f"Running: {' '.join(args)}")
    return subprocess.call(args)


if __name__ == '__main__':
    sys.exit(run_tests())