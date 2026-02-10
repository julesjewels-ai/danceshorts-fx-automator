import coverage
import subprocess
import os
import json
from pathlib import Path
from collections import defaultdict

def run_coverage():
    """Runs pytest with coverage context enabled."""
    cmd = [
        'pytest',
        '--cov=src',
        '--cov-context=test',
        '--cov-report=json'
    ]
    # We rely on .coverage being generated in the current directory.
    print(f"Running coverage command: {' '.join(cmd)}")
    subprocess.run(cmd, check=False)

def get_unique_coverage(test_files: list[str]) -> dict[str, int]:
    """
    Returns a dict mapping test file path -> unique lines covered.
    It expects .coverage to exist and contain context data.
    """
    normalized_test_files = {os.path.abspath(f): f for f in test_files}
    # Also map relative paths just in case
    for f in test_files:
        normalized_test_files[os.path.normpath(f)] = f

    unique_counts = {f: 0 for f in test_files}

    cov = coverage.Coverage()
    try:
        cov.load()
    except coverage.misc.CoverageException:
        print("Warning: No .coverage data found.")
        return unique_counts

    data = cov.get_data()
    measured_files = data.measured_files()

    for src_file in measured_files:
        if not src_file:
            continue

        try:
            contexts_by_lineno = data.contexts_by_lineno(src_file)
        except AttributeError:
            print(f"Warning: Coverage data does not support contexts for {src_file}.")
            continue

        if not contexts_by_lineno:
             continue

        for lineno, contexts in contexts_by_lineno.items():
            covering_files = set()
            for ctx in contexts:
                # Context is typically "tests/test_foo.py::test_func"
                if '::' in ctx:
                    fpath = ctx.split('::')[0]
                    # Handle relative vs absolute
                    abs_fpath = os.path.abspath(fpath)
                    covering_files.add(abs_fpath)
                elif ctx.endswith('.py'):
                    covering_files.add(os.path.abspath(ctx))
                # Ignore 'run' or empty contexts

            # If all contexts map to the SAME file, it is unique coverage for that file
            if len(covering_files) == 1:
                unique_file = list(covering_files)[0]
                # Check if this file is in our list of test files
                if unique_file in normalized_test_files:
                    original_path = normalized_test_files[unique_file]
                    unique_counts[original_path] += 1
                else:
                    # Try looking up by relative path
                    rel_path = os.path.relpath(unique_file)
                    if rel_path in normalized_test_files:
                         original_path = normalized_test_files[rel_path]
                         unique_counts[original_path] += 1
                    # Or try simpler matching
                    elif os.path.basename(unique_file) in [os.path.basename(k) for k in normalized_test_files]:
                        # Weak match, but better than nothing? No, safer to skip.
                        pass

    return unique_counts
