import sys
import os
import argparse

# Add repo root to sys.path
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from src.entropy.main import run

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Entropy: Repository Sanitation & De-inflation')
    parser.add_argument('--dry-run', action='store_true', help='Simulate actions without modifying files')
    args = parser.parse_args()

    run(dry_run=args.dry_run)
