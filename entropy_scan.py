import os
import sys
import subprocess
import json
import ast
import shutil
import logging

# --- CONFIGURATION ---
MAX_TOKEN_CONTEXT = 2000
MAX_MOCK_DENSITY = 0.55
MIN_UNIQUE_COVERAGE = 5
VIBE_CHECK_THRESHOLD = 20
EXECUTION_MODE = 'PR_SUGGESTION' # 'PR_SUGGESTION' or 'REPORT_ONLY'
QUARANTINE_DIR = 'tests/quarantine'
CRITICAL_PATHS_FILE = 'critical_paths.json'

logging.basicConfig(level=logging.INFO, format='[Entropy] %(message)s')

# --- UTILS ---

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # Ignore errors if file doesn't exist in git yet (for churn)
        return ""

def get_git_churn(file_path):
    # Count commits in last 30 days
    cmd = f'git log --since="30 days ago" --oneline -- "{file_path}" | wc -l'
    output = run_cmd(cmd)
    try:
        return int(output)
    except ValueError:
        return 0

def get_file_stats(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.splitlines()
    loc = len(lines)
    token_cost = len(content) // 4 # Rough estimate

    mock_lines = 0
    tautology_detected = False

    # AST Analysis
    try:
        tree = ast.parse(content)

        # Mock counting: look for unittest.mock or pytest-mock patterns
        # Simple line scan for now based on prompt: "Count lines starting with mock(, spyOn(, or .mockReturnValue(."
        # In Python: patch(, Mock(, MagicMock(, return_value=

        for line in lines:
            l = line.strip()
            if 'mock' in l.lower() or 'patch' in l or 'spy' in l:
                mock_lines += 1
            if 'return_value=' in l or 'side_effect=' in l:
                mock_lines += 1

        # Tautology Detection: assert True, assert 1==1
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                if isinstance(node.test, ast.Constant):
                    if node.test.value is True:
                        tautology_detected = True
                elif isinstance(node.test, ast.Compare):
                    # Check for 1==1 etc. (simplified)
                    if isinstance(node.test.left, ast.Constant) and isinstance(node.test.comparators[0], ast.Constant):
                        if node.test.left.value == node.test.comparators[0].value:
                            tautology_detected = True

    except Exception as e:
        logging.error(f"Error parsing {file_path}: {e}")

    mock_density = mock_lines / loc if loc > 0 else 0

    return {
        'loc': loc,
        'token_cost': token_cost,
        'mock_density': mock_density,
        'tautology': tautology_detected
    }

def get_unique_coverage(test_files):
    # Map: file -> set of (source_file, line_no)
    coverage_map = {}

    logging.info("Calculating Unique Coverage...")

    for tf in test_files:
        logging.info(f"  Scanning {tf}...")
        # Run coverage for this file
        # Check if pytest is used
        cmd = f"coverage run --source=src -m pytest {tf} > /dev/null 2>&1"
        subprocess.run(cmd, shell=True) # Ignore output

        # Export to JSON
        subprocess.run("coverage json -o temp_cov.json", shell=True)

        try:
            with open("temp_cov.json", 'r') as f:
                data = json.load(f)

            covered_lines = set()
            for filename, file_data in data['files'].items():
                for line in file_data['executed_lines']:
                    covered_lines.add((filename, line))

            coverage_map[tf] = covered_lines

        except FileNotFoundError:
            coverage_map[tf] = set()

    # Calculate Unique
    unique_counts = {}
    for tf in test_files:
        other_coverage = set()
        for other in test_files:
            if other != tf:
                other_coverage.update(coverage_map[other])

        unique = coverage_map[tf] - other_coverage
        unique_counts[tf] = len(unique)

    # Clean up
    if os.path.exists("temp_cov.json"):
        os.remove("temp_cov.json")
    if os.path.exists(".coverage"):
        os.remove(".coverage")

    return unique_counts

def get_critical_paths():
    critical_paths = set()
    if os.path.exists(CRITICAL_PATHS_FILE):
        try:
            with open(CRITICAL_PATHS_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    critical_paths.update(data)
                elif isinstance(data, dict) and 'paths' in data:
                     critical_paths.update(data['paths'])
        except json.JSONDecodeError:
            pass
    return critical_paths

def get_global_coverage():
    cmd = "coverage run --source=src -m pytest > /dev/null 2>&1"
    subprocess.run(cmd, shell=True)
    subprocess.run("coverage json -o temp_cov_global.json", shell=True)

    try:
        with open("temp_cov_global.json", 'r') as f:
            data = json.load(f)
            return data['totals']['percent_covered']
    except (FileNotFoundError, KeyError):
        return 0
    finally:
        if os.path.exists("temp_cov_global.json"):
            os.remove("temp_cov_global.json")

def main():
    # 0. Initial Global Coverage
    initial_coverage = get_global_coverage()
    logging.info(f"Initial Global Coverage: {initial_coverage}%")

    # 1. Discovery
    test_files = []
    for root, dirs, files in os.walk("tests"):
        if 'quarantine' in root: continue
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                test_files.append(os.path.join(root, file))

    if not test_files:
        logging.info("No test files found.")
        return

    # 2. Coverage Analysis
    unique_coverage = get_unique_coverage(test_files)
    critical_paths = get_critical_paths()

    # 3. Process Files
    results = []
    flagged_count = 0

    for tf in test_files:
        stats = get_file_stats(tf)
        churn = get_git_churn(tf)
        unique = unique_coverage.get(tf, 0)

        rot_type = []
        if stats['mock_density'] > MAX_MOCK_DENSITY:
            rot_type.append('BRITTLE_MOCKING')
        if stats['token_cost'] > MAX_TOKEN_CONTEXT:
            rot_type.append('CONTEXT_BLOAT')
        if stats['tautology']:
            rot_type.append('TAUTOLOGY')
        if churn > 5: # Threshold from prompt
            rot_type.append('HIGH_CHURN') # Added tag for logic

        action = 'NONE'
        rationale = ''

        # Check Critical Path Immunity
        is_critical = tf in critical_paths

        if is_critical:
            rationale = "Immune (Critical Path)"
            action = 'NONE'
        else:
            # Strategy A: Bloat Reducer
            if 'CONTEXT_BLOAT' in rot_type:
                action = 'REFACTOR (SUGGESTED)'
                rationale = 'High token cost, consider externalizing snapshots.'

            # Strategy B: Liability Prune
            if unique == 0 and (('BRITTLE_MOCKING' in rot_type) or ('TAUTOLOGY' in rot_type)):
                action = 'DELETE'
                rationale = 'Brittle/Useless test with 0 unique coverage.'

            # Strategy C: Quarantine
            if churn > 5 and (len(rot_type) > 1 or (len(rot_type) == 1 and 'HIGH_CHURN' not in rot_type)):
                 action = 'QUARANTINE'
                 rationale = 'High churn and rot detected.'

        if action != 'NONE':
            flagged_count += 1

        results.append({
            'file': tf,
            'rot_type': ", ".join(rot_type),
            'unique_coverage': unique,
            'action': action,
            'rationale': rationale
        })

    # Vibe Check
    if flagged_count > VIBE_CHECK_THRESHOLD:
        logging.error(f"[VIBE CHECK] Aborting! Too many flagged files ({flagged_count} > {VIBE_CHECK_THRESHOLD}). Tagging Lead Architect.")
        sys.exit(1)

    # 4. Execute Actions
    logging.info("\n--- ENTROPY REPORT ---")
    print(f"{'File':<30} | {'Rot Type':<20} | {'Unique':<10} | {'Action':<15} | {'Rationale'}")
    print("-" * 100)

    actions_taken = False

    for r in results:
        print(f"{r['file']:<30} | {r['rot_type']:<20} | {r['unique_coverage']:<10} | {r['action']:<15} | {r['rationale']}")

        if r['action'] == 'DELETE':
            os.remove(r['file'])
            logging.info(f"  [EXEC] Deleted {r['file']}")
            actions_taken = True

        elif r['action'] == 'QUARANTINE':
            if not os.path.exists(QUARANTINE_DIR):
                os.makedirs(QUARANTINE_DIR)
            new_path = os.path.join(QUARANTINE_DIR, os.path.basename(r['file']))
            shutil.move(r['file'], new_path)
            logging.info(f"  [EXEC] Moved {r['file']} to {QUARANTINE_DIR}")
            actions_taken = True

    # 5. Coverage Cliff Check
    if actions_taken:
        final_coverage = get_global_coverage()
        logging.info(f"Final Global Coverage: {final_coverage}%")

        drop = initial_coverage - final_coverage
        if drop > 0.5:
             logging.error(f"[COVERAGE CLIFF] Coverage dropped by {drop:.2f}% (> 0.5%). Rollback recommended!")
             # In a real CI, we'd revert. Here we just warn.
             sys.exit(1)

if __name__ == "__main__":
    main()
