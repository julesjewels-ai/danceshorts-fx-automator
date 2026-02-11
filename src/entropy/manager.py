import os
import json
import ast
from typing import List, Dict
from src.entropy.models import TestFileHealth, RotVerdict, RotType, Action
from src.entropy.scanner import Scanner
from src.entropy.coverage import CoverageManager
from src.entropy.git_utils import get_file_churn
from src.entropy.refactor import RefactorManager

class EntropyManager:
    def __init__(self):
        self.scanner = Scanner()
        self.coverage_manager = CoverageManager()
        self.refactor_manager = RefactorManager()
        self.verdicts: List[RotVerdict] = []
        self.health_records: Dict[str, TestFileHealth] = {}
        self.critical_paths = self._load_critical_paths()
        self.config = {
            "maxTokenContext": 2000,
            "maxMockDensity": 0.55,
            "minUniqueCoverageThreshold": 5,
            "executionMode": "PR_SUGGESTION"
        }

    def _load_critical_paths(self) -> List[str]:
        try:
            with open("critical_paths.json", "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def run(self):
        print("Phase 1: The Cartography...")
        self.coverage_manager.run_coverage()
        unique_coverage_map = self.coverage_manager.analyze_unique_coverage()

        print("Phase 2: The Rot Scan & Verdict...")
        test_files = self._discover_test_files()

        for filepath in test_files:
            self._process_file(filepath, unique_coverage_map)

        print("Phase 3: The Action...")
        self._execute_actions()

        print("Phase 4: The Cleanse...")
        self._generate_report()

    def _discover_test_files(self) -> List[str]:
        test_files = []
        for root, dirs, files in os.walk("tests"):
            # Exclude unwanted directories
            if "quarantine" in dirs:
                dirs.remove("quarantine")
            if "__pycache__" in dirs:
                dirs.remove("__pycache__")

            if "quarantine" in root or "__pycache__" in root:
                continue

            for file in files:
                if (file.startswith("test_") or file.endswith("_test.py")) and file.endswith(".py") and file != "__init__.py":
                    test_files.append(os.path.join(root, file))
        return test_files

    def _process_file(self, filepath: str, unique_map: Dict[str, int]):
        # Calculate metrics
        metrics = self.scanner.scan_file(filepath)
        churn = get_file_churn(filepath)

        # Determine relative path for unique map lookup
        rel_path = os.path.relpath(filepath, os.getcwd())
        unique_lines = unique_map.get(rel_path, 0)

        # Check critical path
        is_critical = rel_path in self.critical_paths

        health = TestFileHealth(
            file_path=filepath,
            associated_source_files=[],
            loc=metrics["loc"],
            mock_density=metrics["mock_density"],
            churn_rate=churn,
            token_cost=metrics["token_cost"],
            unique_coverage_lines=unique_lines,
            is_critical_path=is_critical
        )

        self.health_records[filepath] = health
        verdict = self._verdict(health, metrics)
        self.verdicts.append(verdict)

    def _verdict(self, health: TestFileHealth, metrics: Dict) -> RotVerdict:
        tags = []
        if health.mock_density > self.config["maxMockDensity"]:
            tags.append(RotType.BRITTLE_MOCKING)
        if health.token_cost > self.config["maxTokenContext"]:
            tags.append(RotType.CONTEXT_BLOAT)
        if metrics["has_tautology"]:
            tags.append(RotType.TAUTOLOGY)
        if health.churn_rate > 5:
            tags.append(RotType.HIGH_CHURN)

        action = Action.NONE
        rationale = ""

        # Strategies

        # Strategy A: Bloat Reducer
        if RotType.CONTEXT_BLOAT in tags:
            if metrics["large_literals"]:
                action = Action.COMPACT_SNAPSHOTS
                rationale = f"Externalized {len(metrics['large_literals'])} large literals."

        # Strategy B: Liability Prune
        # Condition: BRITTLE_MOCKING OR TAUTOLOGY detected AND uniqueCoverageLines === 0
        if (RotType.BRITTLE_MOCKING in tags or RotType.TAUTOLOGY in tags) and health.unique_coverage_lines == 0:
            if not health.is_critical_path:
                action = Action.DELETE
                rationale = "Brittle/Tautological and 0 unique coverage."

        # Strategy C: Quarantine
        # Condition: High Churn Rate AND High Rot Score (tags present)
        # Using simple heuristic: High Churn + at least one other rot tag
        if RotType.HIGH_CHURN in tags and len(tags) > 1:
            # Delete takes precedence if valid
            if action != Action.DELETE:
                action = Action.QUARANTINE
                rationale = "High Churn and Rot detected."

        return RotVerdict(
            file=health.file_path,
            score=len(tags) * 10.0,
            tags=tags,
            suggested_action=action,
            rationale=rationale
        )

    def _execute_actions(self):
        # Vibe Check
        flagged_files = [v for v in self.verdicts if v.suggested_action in [Action.DELETE, Action.QUARANTINE]]
        if len(flagged_files) > 20:
            print(f"ABORT: Vibe check failed. {len(flagged_files)} files flagged for removal/quarantine.")
            # We skip execution but still generate report
            return

        for verdict in self.verdicts:
            if verdict.suggested_action == Action.DELETE:
                if self.refactor_manager.delete_file(verdict.file):
                    print(f"Deleted {verdict.file}")
            elif verdict.suggested_action == Action.QUARANTINE:
                if self.refactor_manager.quarantine_file(verdict.file):
                    print(f"Quarantined {verdict.file}")
            elif verdict.suggested_action == Action.COMPACT_SNAPSHOTS:
                # Re-scan to get literals as we didn't store them in verdict
                try:
                    with open(verdict.file, 'r') as f:
                        tree = ast.parse(f.read())
                    literals = self.scanner.find_large_literals(tree)
                    if self.refactor_manager.externalize_snapshots(verdict.file, literals):
                         print(f"Compact snapshots for {verdict.file}")
                except Exception as e:
                    print(f"Error processing snapshots for {verdict.file}: {e}")

    def _generate_report(self):
        lines = ["# Entropy Report", "", "| File | Rot Type | Unique Coverage | Action Taken | Rationale |", "|---|---|---|---|---|"]
        for v in self.verdicts:
            if v.suggested_action != Action.NONE:
                tags_str = ", ".join([t.value for t in v.tags])
                unique_cov = self.health_records[v.file].unique_coverage_lines
                lines.append(f"| {v.file} | {tags_str} | {unique_cov} | {v.suggested_action.value} | {v.rationale} |")

        report_content = "\n".join(lines)
        with open("entropy_report.md", "w") as f:
            f.write(report_content)
        print("Report generated: entropy_report.md")
