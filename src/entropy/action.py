import os
import shutil
import ast
import json
from pathlib import Path
from .models import RotVerdict

def delete_file(filepath: str, dry_run: bool = False):
    if dry_run:
        print(f"[DRY-RUN] Deleting {filepath}")
        return
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"Deleted {filepath}")

def quarantine_file(filepath: str, dry_run: bool = False):
    if dry_run:
        print(f"[DRY-RUN] Quarantining {filepath}")
        return

    # Assuming tests are in tests/
    # If filepath is tests/foo.py, move to tests/quarantine/foo.py
    # If filepath is src/foo/test_bar.py, move to src/foo/quarantine/test_bar.py?
    # The prompt says: "Move to tests/quarantine."
    # I'll use a fixed directory `tests/quarantine`.

    quarantine_dir = 'tests/quarantine'
    if not os.path.exists(quarantine_dir):
        os.makedirs(quarantine_dir, exist_ok=True)
        # Create __init__.py so it is a package
        with open(os.path.join(quarantine_dir, '__init__.py'), 'w') as f:
            pass

    new_path = os.path.join(quarantine_dir, os.path.basename(filepath))

    if os.path.exists(filepath):
        shutil.move(filepath, new_path)
        print(f"Moved {filepath} to {new_path}")

def execute_strategy(verdict: RotVerdict, dry_run: bool = False):
    if verdict.suggested_action == 'DELETE':
        delete_file(verdict.file, dry_run)
    elif verdict.suggested_action == 'QUARANTINE':
        quarantine_file(verdict.file, dry_run)
    elif verdict.suggested_action == 'COMPACT_SNAPSHOTS':
        print(f"Skipping automated refactor for {verdict.file} (COMPACT_SNAPSHOTS not fully implemented)")
    elif verdict.suggested_action == 'NONE':
        pass
