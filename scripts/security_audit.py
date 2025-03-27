"""
Security audit script for FinancialMediator.

This script performs various security checks on the codebase and configuration.
"""

import os
import re
import subprocess
from typing import List, Dict, Any
import json

# Sensitive patterns to search for
SENSITIVE_PATTERNS = [
    r'(?:password|secret|token|key|pwd|auth)\s*=\s*["\']([^"\']+)\b',
    r'postgresql://[^@]+:[^@]+@',
    r'mysql://[^@]+:[^@]+@',
    r'mongodb://[^@]+:[^@]+@',
]

def scan_for_hardcoded_secrets() -> List[str]:
    """
    Scan codebase for hardcoded secrets.
    
    Returns:
        List of files containing hardcoded secrets
    """
    sensitive_files = []
    
    for root, _, files in os.walk('.'):        
        for file in files:
            if file.endswith(('.py', '.env', '.yaml', '.yml', '.json')):
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                        for pattern in SENSITIVE_PATTERNS:
                            if re.search(pattern, content):
                                sensitive_files.append(filepath)
                                break
                except UnicodeDecodeError:
                    continue
                except Exception as e:
                    print(f"Error reading {filepath}: {str(e)}")
    
    return sensitive_files

def check_environment_variables() -> Dict[str, Any]:
    """
    Check if required environment variables are set.
    
    Returns:
        Dictionary of missing environment variables
    """
    required_env_vars = {
        'SECRET_KEY': 'Django secret key',
        'DATABASE_URL': 'Database connection string',
        'JWT_SECRET_KEY': 'JWT signing key',
        'REDIS_URL': 'Redis connection string',
        'CELERY_BROKER_URL': 'Celery broker URL',
        'CELERY_RESULT_BACKEND': 'Celery result backend',
    }
    
    missing_vars = {}
    for var, description in required_env_vars.items():
        if not os.getenv(var):
            missing_vars[var] = description
    
    return missing_vars

def run_sast_scan() -> Dict[str, Any]:
    """
    Run SAST scan using Bandit.
    
    Returns:
        Scan results
    """
    try:
        result = subprocess.run(
            ['bandit', '-r', '.'],
            capture_output=True,
            text=True
        )
        return {
            'status': 'success' if result.returncode == 0 else 'failure',
            'output': result.stdout
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def check_rate_limiting() -> Dict[str, Any]:
    """
    Check rate limiting configuration.
    
    Returns:
        Rate limiting status
    """
    try:
        from banking_api.middleware.rate_limit import RateLimitMiddleware
        
        return {
            'status': 'enabled',
            'config': {
                'requests': RateLimitMiddleware.REQUESTS,
                'duration': RateLimitMiddleware.DURATION,
                'bucket_size': RateLimitMiddleware.BUCKET_SIZE
            }
        }
    except Exception as e:
        return {
            'status': 'error',
            'error': str(e)
        }

def main():
    """
    Run all security audits.
    """
    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'scans': {
            'hardcoded_secrets': {
                'files_found': scan_for_hardcoded_secrets()
            },
            'environment_variables': {
                'missing': check_environment_variables()
            },
            'sast_scan': run_sast_scan(),
            'rate_limiting': check_rate_limiting()
        }
    }
    
    # Save results to file
    with open('security_audit_results.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    # Print summary
    print("\nSecurity Audit Results:")
    print("=====================")
    
    # Hardcoded secrets
    if results['scans']['hardcoded_secrets']['files_found']:
        print(f"\nWARNING: Hardcoded secrets found in {len(results['scans']['hardcoded_secrets']['files_found'])} files:")
        for file in results['scans']['hardcoded_secrets']['files_found']:
            print(f"- {file}")
    else:
        print("\n✓ No hardcoded secrets found")
    
    # Missing environment variables
    if results['scans']['environment_variables']['missing']:
        print(f"\nWARNING: Missing environment variables:")
        for var, desc in results['scans']['environment_variables']['missing'].items():
            print(f"- {var}: {desc}")
    else:
        print("\n✓ All required environment variables are set")
    
    # SAST scan
    sast_result = results['scans']['sast_scan']
    print(f"\nSAST Scan: {sast_result['status'].upper()}")
    if sast_result['status'] != 'success':
        print(f"Error: {sast_result.get('error', 'Unknown error')}")
    
    # Rate limiting
    rate_limit = results['scans']['rate_limiting']
    print(f"\nRate Limiting: {rate_limit['status'].upper()}")
    if rate_limit['status'] == 'error':
        print(f"Error: {rate_limit.get('error', 'Unknown error')}")
    
    # Save results to file
    with open('security_audit_results.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    main()
