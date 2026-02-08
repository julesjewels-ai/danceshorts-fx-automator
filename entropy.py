import os
import ast
import json
import logging
import subprocess
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple

# --- Configuration ---
CONFIG = {
    "maxTokenContext": 100, # Lowered threshold to demonstrate detection on small files
    "maxMockDensity": 0.55,
    "minUniqueCoverageThreshold": 5,
    "executionMode": "PR_SUGGESTION",
    "quarantineDir": "tests/quarantine",
    "fixturesDir": "tests/fixtures"
}

# --- Logging ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("Entropy")

# --- Domain Models ---
@dataclass
class TestFileHealth:
    file_path: str
    loc: int = 0
    mock_density: float = 0.0
    token_cost: int = 0
    unique_coverage_lines: int = 0
    is_critical_path: bool = False
    tautology_detected: bool = False

@dataclass
class RotVerdict:
    file_path: str
    score: int
    unique_coverage: int
    tags: List[str] = field(default_factory=list)
    suggested_action: str = "NONE"

# --- Phase 1: Cartography (Coverage) ---
def get_covered_lines(xml_path: str) -> Set[Tuple[str, int]]:
    """Parses coverage XML and returns a set of (filename, line_number) tuples."""
    if not os.path.exists(xml_path):
        return set()

    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        covered = set()

        # Iterate packages -> classes -> lines
        for package in root.findall(".//package"):
            for cls in package.findall(".//class"):
                filename = cls.get("filename")
                # Use filename as unique ID.
                for line in cls.findall("lines/line"):
                    if line.get("hits") != "0":
                        covered.add((filename, int(line.get("number"))))
        return covered
    except Exception as e:
        logger.error(f"Error parsing XML {xml_path}: {e}")
        return set()

def analyze_unique_coverage(test_files: List[str]) -> Dict[str, int]:
    """
    Calculates unique coverage for each test file by running them individually.
    """
    coverage_sets = {} # test_file -> Set[(file, line)]

    for tf in test_files:
        logger.info(f"Measuring coverage for {tf}...")

        # Cleanup
        if os.path.exists(".coverage"):
            try: os.remove(".coverage")
            except: pass
        if os.path.exists("coverage.xml"):
            try: os.remove("coverage.xml")
            except: pass

        try:
            # Run pytest for single file
            # capture_output=True hides stdout/stderr unless error
            subprocess.run(
                ["pytest", "--cov=src", "--cov-report=xml:coverage.xml", tf],
                check=True, capture_output=True
            )
            coverage_sets[tf] = get_covered_lines("coverage.xml")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed coverage run for {tf}. Stderr: {e.stderr.decode() if e.stderr else ''}")
            coverage_sets[tf] = set()
        except Exception as e:
            logger.error(f"Error running coverage for {tf}: {e}")
            coverage_sets[tf] = set()

    # Calculate unique
    unique_counts = {}
    for tf, c_set in coverage_sets.items():
        other_coverage = set()
        for other_tf, other_set in coverage_sets.items():
            if other_tf != tf:
                other_coverage.update(other_set)

        unique = c_set - other_coverage
        unique_counts[tf] = len(unique)
        logger.info(f"{tf} has {len(unique)} unique covered lines.")

    return unique_counts

# --- Phase 2: Rot Scan (AST) ---
class MetricVisitor(ast.NodeVisitor):
    def __init__(self):
        self.mock_count = 0
        self.tautology = False

    def visit_Call(self, node):
        func_name = ""
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
        elif isinstance(node.func, ast.Attribute):
            func_name = node.func.attr

        if func_name in ['mock', 'patch', 'MagicMock', 'spy']:
            self.mock_count += 1
        self.generic_visit(node)

    def visit_Assert(self, node):
        if isinstance(node.test, ast.Constant):
            if node.test.value is True or node.test.value == 1:
                self.tautology = True
        self.generic_visit(node)

def scan_file(file_path: str, unique_cov: int) -> TestFileHealth:
    try:
        with open(file_path, 'r') as f:
            content = f.read()

        loc = len([l for l in content.splitlines() if l.strip() and not l.strip().startswith("#")])
        tokens = len(content) // 4

        tree = ast.parse(content)
        visitor = MetricVisitor()
        visitor.visit(tree)

        mock_density = visitor.mock_count / loc if loc > 0 else 0

        return TestFileHealth(
            file_path=file_path,
            loc=loc,
            mock_density=mock_density,
            token_cost=tokens,
            unique_coverage_lines=unique_cov,
            tautology_detected=visitor.tautology
        )
    except Exception as e:
        logger.error(f"Error scanning {file_path}: {e}")
        return TestFileHealth(file_path)

# --- Phase 3: Verdict ---
def get_verdict(health: TestFileHealth) -> RotVerdict:
    tags = []
    score = 0

    if health.mock_density > CONFIG["maxMockDensity"]:
        tags.append("BRITTLE_MOCKING")
        score += 40

    if health.token_cost > CONFIG["maxTokenContext"]:
        tags.append("CONTEXT_BLOAT")
        score += 30

    if health.tautology_detected:
        tags.append("TAUTOLOGY")
        score += 50

    if health.unique_coverage_lines == 0 and not health.is_critical_path:
        tags.append("REDUNDANT_COVERAGE")
        score += 30

    action = "NONE"

    if "CONTEXT_BLOAT" in tags:
        action = "COMPACT_SNAPSHOTS"

    if (("BRITTLE_MOCKING" in tags or "TAUTOLOGY" in tags) and
        health.unique_coverage_lines == 0):
        action = "DELETE"

    if "BRITTLE_MOCKING" in tags and score > 60:
         action = "QUARANTINE"

    return RotVerdict(
        file_path=health.file_path,
        score=score,
        unique_coverage=health.unique_coverage_lines,
        tags=tags,
        suggested_action=action
    )

# --- Phase 4: Action (Refactoring) ---
def extract_snapshots(file_path: str) -> bool:
    """
    Parses file, finds large inline dicts/lists, extracts to JSON files.
    """
    try:
        with open(file_path, 'r') as f:
            lines = f.readlines()
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())
    except Exception as e:
        logger.error(f"Failed to parse {file_path}: {e}")
        return False

    final_replacements = []
    os.makedirs(CONFIG["fixturesDir"], exist_ok=True)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and isinstance(node.value, (ast.Dict, ast.List)):
            # Check size threshold (lines)
            if node.value.end_lineno - node.value.lineno > 4:
                try:
                    # Identify variable name
                    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                        var_name = node.targets[0].id
                    else:
                        continue

                    # Safely evaluate the literal value
                    val = ast.literal_eval(node.value)

                    json_name = f"{os.path.basename(file_path).replace('.py','')}_{var_name}.json"
                    json_path = os.path.join(CONFIG["fixturesDir"], json_name)

                    # Write JSON
                    with open(json_path, 'w') as jf:
                        json.dump(val, jf, indent=2)

                    # Calculate indentation
                    start_line_idx = node.lineno - 1
                    indent = lines[start_line_idx][:len(lines[start_line_idx]) - len(lines[start_line_idx].lstrip())]

                    final_replacements.append({
                        "start": node.lineno,
                        "end": node.value.end_lineno, # Assuming simple assignment stmt
                        "indent": indent,
                        "json_name": json_name,
                        "var_name": var_name
                    })
                except Exception as e:
                    logger.warning(f"Skipping extraction for potential candidate: {e}")
                    pass

    if not final_replacements:
        return False

    # Sort reverse to apply bottom-up
    final_replacements.sort(key=lambda x: x["start"], reverse=True)

    new_lines = list(lines)

    for rep in final_replacements:
        s = rep["start"] - 1
        e = rep["end"]

        # Replacement code block
        # Using context manager to load data
        blk = f"{rep['indent']}with open(os.path.join(os.path.dirname(__file__), 'fixtures', '{rep['json_name']}'), 'r') as f:\n"
        blk += f"{rep['indent']}    {rep['var_name']} = json.load(f)\n"

        # This replaces lines s to e (exclusive of e if slicing, but e is inclusive line no)
        # new_lines[s:e] replaces lines s, s+1, ... e-1.
        # So we need new_lines[s:e] if e is exclusive.
        # AST lineno are 1-based inclusive.
        # So lines are indices s to e-1.
        # new_lines[s:e] covers indices s, s+1, ..., e-1.
        new_lines[s:e] = [blk]

    # Add imports if missing
    if not any("import json" in l for l in new_lines):
        new_lines.insert(0, "import json\n")
    if not any("import os" in l for l in new_lines):
        new_lines.insert(0, "import os\n")

    with open(file_path, 'w') as f:
        f.writelines(new_lines)

    return True

def execute_actions(verdicts: List[RotVerdict]):
    report_lines = [
        "# Entropy Report",
        "",
        "| File | Rot Type | Unique Coverage | Action Taken | Rationale |",
        "|---|---|---|---|---|"
    ]

    for v in verdicts:
        action_taken = v.suggested_action
        rationale = ", ".join(v.tags)

        if v.suggested_action == "COMPACT_SNAPSHOTS":
            if CONFIG["executionMode"] == "PR_SUGGESTION":
                if extract_snapshots(v.file_path):
                     action_taken = "REFACTORED"
                     rationale += " (Extracted JSON)"
                else:
                    action_taken = "FAILED_REFACTOR"

        elif v.suggested_action == "DELETE" and CONFIG["executionMode"] == "PR_SUGGESTION":
             try:
                 os.remove(v.file_path)
                 action_taken = "DELETED"
             except: pass

        elif v.suggested_action == "QUARANTINE" and CONFIG["executionMode"] == "PR_SUGGESTION":
             try:
                 os.makedirs(CONFIG["quarantineDir"], exist_ok=True)
                 shutil.move(v.file_path, os.path.join(CONFIG["quarantineDir"], os.path.basename(v.file_path)))
                 action_taken = "QUARANTINED"
             except: pass

        report_lines.append(f"| {v.file_path} | {', '.join(v.tags)} | {v.unique_coverage} lines | {action_taken} | {rationale} |")

    with open("ENTROPY_REPORT.md", "w") as f:
        f.write("\n".join(report_lines))

# --- Main Workflow ---
def main():
    logger.info("Starting Entropy Protocol...")

    test_files = [os.path.join("tests", f) for f in os.listdir("tests") if f.endswith(".py") and f != "__init__.py"]

    # 1. Phase 1
    unique_cov = analyze_unique_coverage(test_files)

    # 2. Phase 2 & 3
    verdicts = []
    for tf in test_files:
        u_cov = unique_cov.get(tf, 0)
        health = scan_file(tf, u_cov)
        verdict = get_verdict(health)
        verdicts.append(verdict)
        logger.info(f"Analyzed {tf}: Score={verdict.score}, Action={verdict.suggested_action}")

    # 3. Phase 4
    execute_actions(verdicts)

    # Cleanup artifacts
    for f in ["coverage.xml", ".coverage"]:
        if os.path.exists(f):
            try: os.remove(f)
            except: pass

    logger.info("Entropy Protocol Complete. Check ENTROPY_REPORT.md")

if __name__ == "__main__":
    main()
