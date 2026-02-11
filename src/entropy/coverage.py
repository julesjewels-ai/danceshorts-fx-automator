import subprocess
import os
import coverage
from typing import Dict, Set, List

class CoverageManager:
    def __init__(self, data_file=".coverage"):
        self.data_file = data_file
        self.cov = coverage.Coverage(data_file=self.data_file)

    def run_coverage(self):
        """
        Runs pytest with context recording.
        """
        # Remove existing coverage data
        if os.path.exists(self.data_file):
            try:
                os.remove(self.data_file)
            except OSError:
                pass

        # Run pytest
        # Use --cov-context=test
        # We assume pytest-cov is installed.
        cmd = [
            "pytest",
            "--cov=src", # Cover src directory
            "--cov-context=test",
            "--cov-report=json" # Generate JSON report
        ]

        print("Running coverage analysis...")
        try:
            subprocess.run(cmd, check=False) # Tests might fail, but coverage should run.
        except subprocess.CalledProcessError as e:
            print(f"Coverage run failed: {e}")

    def analyze_unique_coverage(self) -> Dict[str, int]:
        """
        Returns a map of {test_file_path: unique_lines_count}.
        The test_file_path keys will be relative paths as reported by pytest context (e.g., 'tests/test_core.py').
        """
        self.cov.load()
        data = self.cov.get_data()

        unique_counts = {} # test_file -> count

        measured_files = data.measured_files()

        for measured_file in measured_files:
            contexts_by_lineno = data.contexts_by_lineno(measured_file)

            for lineno, contexts in contexts_by_lineno.items():
                covering_test_files = set()
                for ctx in contexts:
                    # Handle context format.
                    # Standard pytest-cov context: "tests/test_foo.py::test_bar|run"
                    # But sometimes just "tests/test_foo.py::test_bar".
                    # We want the file path.

                    if not ctx:
                        continue

                    tf = ctx
                    if "::" in tf:
                        tf = tf.split("::")[0]

                    # Clean up "|run" suffix if present
                    if "|" in tf:
                        tf = tf.split("|")[0]

                    # Determine if it's an empty string after split
                    if tf:
                        covering_test_files.add(tf)

                if len(covering_test_files) == 1:
                    single_test_file = list(covering_test_files)[0]
                    unique_counts[single_test_file] = unique_counts.get(single_test_file, 0) + 1

        return unique_counts
