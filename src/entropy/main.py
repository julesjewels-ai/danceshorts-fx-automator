import os
import json
from .config import EntropyConfig
from .models import TestFileHealth, RotVerdict
from . import scanner, git_utils, coverage, action, reporting

def discover_test_files(root_dir='.'):
    test_files = []
    # Search for test_*.py in tests/ and src/
    for root, dirs, files in os.walk(root_dir):
        # Skip hidden dirs
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.startswith('test_') and file.endswith('.py'):
                path = os.path.join(root, file)
                # Ignore quarantine
                path_parts = path.split(os.sep)
                if 'quarantine' in path_parts:
                    continue
                test_files.append(path)
    return test_files

def run(dry_run=False):
    print("Phase 1: The Cartography (Mapping & Coverage)...")
    coverage.run_coverage()
    test_files = discover_test_files()
    unique_cov_map = coverage.get_unique_coverage(test_files)

    # Normalize map to absolute paths for reliable lookup
    abs_unique_cov_map = {os.path.abspath(k): v for k, v in unique_cov_map.items()}

    print(f"Found {len(test_files)} test files.")

    verdicts = []

    print("Phase 2: The Rot Scan (AST Analysis)...")
    for file in test_files:
        scan_data = scanner.scan_file(file)
        churn = git_utils.get_churn_rate(file)

        abs_path = os.path.abspath(file)
        unique_cov = abs_unique_cov_map.get(abs_path, 0)

        # Determine Criticality
        is_critical = False
        if os.path.exists(EntropyConfig.CRITICAL_PATHS_FILE):
             try:
                 with open(EntropyConfig.CRITICAL_PATHS_FILE, 'r') as f:
                     critical_paths = json.load(f)
                     # Check if file is in critical paths list (exact match or list of files)
                     # Assuming list of strings
                     if isinstance(critical_paths, list):
                         # Normalize paths
                         norm_critical = [os.path.abspath(p) for p in critical_paths]
                         if abs_path in norm_critical:
                             is_critical = True
             except:
                 pass

        health = TestFileHealth(
            file_path=file,
            associated_source_files=scan_data['imports'],
            loc=scan_data['loc'],
            mock_density=scan_data['mock_density'],
            churn_rate=churn,
            token_cost=scan_data['token_cost'],
            unique_coverage_lines=unique_cov,
            is_critical_path=is_critical
        )

        # Phase 3: Verdict
        tags = []
        suggested_action = 'NONE'
        rationale = ""

        # Check for Rot Patterns
        if health.mock_density > EntropyConfig.MAX_MOCK_DENSITY:
            tags.append('BRITTLE_MOCKING')

        if health.token_cost > EntropyConfig.MAX_TOKEN_CONTEXT:
            tags.append('CONTEXT_BLOAT')

        if scan_data['tautologies'] > 0:
            tags.append('TAUTOLOGY')

        # Strategy A: Bloat Reducer
        if 'CONTEXT_BLOAT' in tags:
            suggested_action = 'COMPACT_SNAPSHOTS'
            rationale = f"Token cost {health.token_cost} > {EntropyConfig.MAX_TOKEN_CONTEXT}"

        # Strategy B: Liability Prune
        # Condition: (BRITTLE_MOCKING OR TAUTOLOGY) AND uniqueCoverageLines === 0
        if ('BRITTLE_MOCKING' in tags or 'TAUTOLOGY' in tags) and health.unique_coverage_lines == 0:
            suggested_action = 'DELETE'
            rationale = "Brittle/Tautological & No unique coverage."

        # Strategy C: Quarantine
        # Condition: High Churn (> 5) AND High Rot Score (Any tag present)
        is_rotten = len(tags) > 0
        if health.churn_rate > EntropyConfig.CHURN_THRESHOLD and is_rotten:
             # Only quarantine if not already deleting
             if suggested_action != 'DELETE':
                 suggested_action = 'QUARANTINE'
                 rationale = f"High churn ({health.churn_rate}) & Rot detected."

        # Safety: Critical Path Immunity
        if is_critical:
            if suggested_action == 'DELETE':
                suggested_action = 'NONE'
                rationale = "Critical Path Immunity."

        # Safety: Immune if unique coverage > 0 (Override Delete)
        if suggested_action == 'DELETE' and health.unique_coverage_lines > 0:
             suggested_action = 'NONE' # Or just remove DELETE action, keep tags?
             # The prompt says: "Constraint: If uniqueCoverageLines > 0, the file is IMMUNE to deletion"
             rationale = f"Immune (Unique Coverage: {health.unique_coverage_lines})"

        verdicts.append(RotVerdict(
            file=file,
            score=0.0,
            unique_coverage=health.unique_coverage_lines,
            tags=tags,
            suggested_action=suggested_action,
            rationale=rationale
        ))

    # Vibe Check
    actions_count = len([v for v in verdicts if v.suggested_action in ['DELETE', 'QUARANTINE']])
    if actions_count > 20:
        print(f"ABORT: Too many actions ({actions_count} > 20). Tagging Lead Architect.")
        return

    # Execute Actions
    print("Phase 3: The Verdict & Action...")
    for v in verdicts:
        if v.suggested_action != 'NONE':
            print(f"Action: {v.suggested_action} on {v.file} ({v.rationale})")
            action.execute_strategy(v, dry_run=dry_run)

    # Phase 4: Cleanse (Report)
    report = reporting.generate_report(verdicts)
    print("\n" + report)

    with open('entropy_report.md', 'w') as f:
        f.write(report)
