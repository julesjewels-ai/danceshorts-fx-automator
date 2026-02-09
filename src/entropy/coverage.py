import coverage
import os
import subprocess
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)

class CoverageManager:
    def __init__(self, source_dir: str = "src", test_dir: str = "tests"):
        self.source_dir = source_dir
        self.test_dir = test_dir
        self.cov_file = ".coverage"

    def run_coverage(self):
        """Runs pytest with coverage and dynamic contexts."""
        logger.info("Running coverage analysis...")
        # Clean previous coverage
        if os.path.exists(self.cov_file):
            try:
                os.remove(self.cov_file)
            except OSError:
                pass

        cmd = [
            "coverage", "run",
            "--source", self.source_dir,
            "--context", "test_function",
            "-m", "pytest",
            self.test_dir
        ]

        try:
            # We want to capture output to avoid clutter, but let it fail gracefully
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                logger.warning(f"Tests failed during coverage run. Output:\n{result.stderr}")
            else:
                logger.info("Coverage run complete.")
        except Exception as e:
            logger.error(f"Coverage execution failed: {e}")

    def analyze_unique_coverage(self) -> Dict[str, int]:
        """
        Returns a map of test_file_path -> count of unique lines covered.
        """
        if not os.path.exists(self.cov_file):
            logger.warning("No coverage file found.")
            return {}

        cov = coverage.Coverage(data_file=self.cov_file)
        cov.load()

        measured_files = cov.get_data().measured_files()

        # Map: filename -> lineno -> set of test files
        line_coverage_map: Dict[str, Dict[int, Set[str]]] = {}

        abs_source_dir = os.path.abspath(self.source_dir)

        for filename in measured_files:
            # We only care about coverage of source files
            if not os.path.abspath(filename).startswith(abs_source_dir):
                continue

            contexts_by_line = cov.get_data().contexts_by_lineno(filename)

            for lineno, contexts in contexts_by_line.items():
                test_files = set()
                for ctx in contexts:
                    if not ctx: continue
                    # context example: tests.test_core.test_initialization
                    resolved_file = self._resolve_context_to_file(ctx)
                    if resolved_file:
                        test_files.add(resolved_file)

                if filename not in line_coverage_map:
                    line_coverage_map[filename] = {}

                line_coverage_map[filename][lineno] = test_files

        # Count unique lines
        unique_counts: Dict[str, int] = {}

        for filename, lines in line_coverage_map.items():
            for lineno, covering_files in lines.items():
                if len(covering_files) == 1:
                    unique_file = list(covering_files)[0]
                    unique_counts[unique_file] = unique_counts.get(unique_file, 0) + 1

        return unique_counts

    def _resolve_context_to_file(self, context: str) -> str:
        """
        Resolves a coverage context (e.g. 'tests.test_core.test_func')
        to a file path (e.g. 'tests/test_core.py').
        """
        parts = context.split('.')

        current_path = ""
        for i, part in enumerate(parts):
            if i == 0:
                current_path = part
            else:
                current_path = os.path.join(current_path, part)

            # Check if directory exists
            if os.path.isdir(current_path):
                continue

            # Check if file exists (with .py)
            candidate = current_path + ".py"
            if os.path.isfile(candidate):
                return candidate

        return ""
