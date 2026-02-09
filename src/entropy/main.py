import argparse
import os
import logging
import json
from typing import List, Dict, Tuple
from .models import EntropyConfig, RotVerdict, SuggestedAction, TestFileHealth, RotTag
from .coverage import CoverageManager
from .scanner import RotScanner
from .actions import ActionEnforcer
from .git_utils import get_file_churn

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger("entropy")

def main():
    parser = argparse.ArgumentParser(description="Entropy: Audit Test Suite Liability")
    parser.add_argument("--dry-run", action="store_true", help="Simulate actions without modifying files")
    parser.add_argument("--report-file", default="entropy_report.md", help="Output report file")
    args = parser.parse_args()

    config = EntropyConfig()

    # 1. Coverage Analysis
    cov_mgr = CoverageManager()
    cov_mgr.run_coverage()
    unique_counts = cov_mgr.analyze_unique_coverage()

    # 2. Scan Files
    scanner = RotScanner(config)
    test_files = _find_test_files("tests")

    analyzed_items: List[Tuple[RotVerdict, TestFileHealth]] = []

    # Check critical paths
    critical_paths = _load_critical_paths()

    for file_path in test_files:
        health, verdict = scanner.scan_file(file_path)

        # 3. Enhance with Coverage Info & Churn
        abs_path = os.path.abspath(file_path)
        unique_lines = unique_counts.get(abs_path, 0)
        health.unique_coverage_lines = unique_lines

        # Calculate Churn
        health.churn_rate = get_file_churn(file_path)

        if file_path in critical_paths or abs_path in critical_paths:
            health.is_critical_path = True
            # Infinite unique coverage effectively
            health.unique_coverage_lines = 999999

        # 4. Decide Action (Strategy Pattern)
        verdict = _decide_action(verdict, health, config)
        analyzed_items.append((verdict, health))

    # 5. Execute Actions
    enforcer = ActionEnforcer(config)
    results = []

    deleted_count = 0
    quarantined_count = 0

    logger.info("Executing actions...")

    for verdict, health in analyzed_items:
        if verdict.suggested_action != SuggestedAction.NONE:
            # Safety Check: > 20 files flagged?
            if (deleted_count + quarantined_count) >= 20:
                logger.error("ABORTING: Too many files flagged for deletion/quarantine (>20). Manual Review Required.")
                break

            action_result = enforcer.execute_action(verdict, dry_run=args.dry_run)

            if verdict.suggested_action == SuggestedAction.DELETE:
                deleted_count += 1
            elif verdict.suggested_action == SuggestedAction.QUARANTINE:
                quarantined_count += 1

            results.append({
                "file": verdict.file,
                "rot_type": ", ".join([t.value for t in verdict.tags]),
                "unique_cov": health.unique_coverage_lines,
                "action": action_result,
                "rationale": verdict.rationale
            })

    # 6. Generate Report
    _generate_report(results, args.report_file)
    logger.info(f"Report generated at {args.report_file}")

def _find_test_files(directory: str) -> List[str]:
    files = []
    if not os.path.exists(directory):
        return files

    for root, _, filenames in os.walk(directory):
        if "quarantine" in root: continue
        for f in filenames:
            if f.startswith("test_") and f.endswith(".py"):
                 files.append(os.path.join(root, f))
    return files

def _load_critical_paths() -> List[str]:
    path = "critical_paths.json"
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            return []
    return []

def _decide_action(verdict: RotVerdict, health: TestFileHealth, config: EntropyConfig) -> RotVerdict:
    # Priority 1: Liability Prune (Delete)
    # Condition: BRITTLE_MOCKING OR TAUTOLOGY detected AND uniqueCoverageLines === 0
    is_brittle = RotTag.BRITTLE_MOCKING in verdict.tags or RotTag.TAUTOLOGY in verdict.tags
    if is_brittle and health.unique_coverage_lines == 0 and not health.is_critical_path:
        verdict.suggested_action = SuggestedAction.DELETE
        verdict.rationale = "Brittle/Tautology & 0 Unique Coverage"
        return verdict

    # Priority 2: Quarantine
    # Condition: High Churn Rate (> 5 changes/month) AND High Rot Score
    # Note: Churn rate is mocked as 0 for now as we don't have git access implementation
    if health.churn_rate > 5 and verdict.score > 50 and not health.is_critical_path:
         verdict.suggested_action = SuggestedAction.QUARANTINE
         verdict.rationale = "High Churn & High Rot Score"
         return verdict

    # Priority 3: Bloat Reducer
    # Condition: CONTEXT_BLOAT detected
    if RotTag.CONTEXT_BLOAT in verdict.tags:
        verdict.suggested_action = SuggestedAction.COMPACT_SNAPSHOTS
        verdict.rationale = "Context Bloat detected (>2000 tokens)"
        return verdict

    return verdict

def _generate_report(results: List[Dict], filepath: str):
    with open(filepath, "w") as f:
        f.write("# [Entropy] Maintenance Report\n\n")
        if not results:
            f.write("No actions taken. System healthy.\n")
            return

        f.write("| File | Rot Type | Unique Cov | Action Taken | Rationale |\n")
        f.write("|---|---|---|---|---|\n")
        for res in results:
            f.write(f"| {res['file']} | {res['rot_type']} | {res.get('unique_cov', 0)} | {res['action']} | {res['rationale']} |\n")

if __name__ == "__main__":
    main()
