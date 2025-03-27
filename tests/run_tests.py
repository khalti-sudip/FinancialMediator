import os
import sys
import django
from django.test.runner import DiscoverRunner
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings')
django.setup()

def run_tests():
    test_runner = DiscoverRunner()
    failures = test_runner.run_tests(['banking_api'])
    sys.exit(bool(failures))

if __name__ == '__main__':
    run_tests()
