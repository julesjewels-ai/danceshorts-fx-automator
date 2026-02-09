import ast
import os
from typing import Tuple, Set
from .models import RotVerdict, RotTag, TestFileHealth, EntropyConfig

class RotScanner:
    def __init__(self, config: EntropyConfig):
        self.config = config

    def scan_file(self, filepath: str) -> Tuple[TestFileHealth, RotVerdict]:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                tree = ast.parse(content)
        except Exception as e:
            # If we can't parse, return empty/safe defaults
            # e.g. syntax error in file
            return self._create_error_result(filepath, str(e))

        loc = len(content.splitlines())
        mock_density = self._calculate_mock_density(tree, loc)
        token_cost = len(content) // 4 # heuristic: 4 chars per token

        tags = []
        score = 0

        # Check Mock Abuse
        if mock_density > self.config.max_mock_density:
            tags.append(RotTag.BRITTLE_MOCKING)
            score += 40

        # Check Tautology
        if self._check_tautology(tree):
            tags.append(RotTag.TAUTOLOGY)
            score += 30

        # Check Context Bloat
        if token_cost > self.config.max_token_context:
            tags.append(RotTag.CONTEXT_BLOAT)
            score += 20

        verdict = RotVerdict(file=filepath, score=score, tags=tags)

        health = TestFileHealth(
            file_path=filepath,
            associated_source_files=[], # To be filled by coverage mapping
            loc=loc,
            mock_density=mock_density,
            churn_rate=0, # Placeholder
            token_cost=token_cost,
            unique_coverage_lines=0, # To be filled later
            is_critical_path=False
        )

        return health, verdict

    def _create_error_result(self, filepath: str, error: str) -> Tuple[TestFileHealth, RotVerdict]:
        health = TestFileHealth(
            file_path=filepath, associated_source_files=[], loc=0,
            mock_density=0, churn_rate=0, token_cost=0,
            unique_coverage_lines=0, is_critical_path=False
        )
        verdict = RotVerdict(file=filepath, score=0, tags=[], rationale=f"Error: {error}")
        return health, verdict

    def _calculate_mock_density(self, tree: ast.AST, loc: int) -> float:
        mock_lines: Set[int] = set()

        for node in ast.walk(tree):
            # Check function calls
            if isinstance(node, ast.Call) and hasattr(node, 'lineno'):
                if self._is_mock_call(node):
                    mock_lines.add(node.lineno)

            # Check decorators
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for decorator in node.decorator_list:
                    if hasattr(decorator, 'lineno'):
                        # Decorator can be Call or Name/Attribute
                        if isinstance(decorator, ast.Call):
                            if self._is_mock_call(decorator):
                                mock_lines.add(decorator.lineno)
                        elif self._is_mock_name(decorator):
                            mock_lines.add(decorator.lineno)

        if loc == 0: return 0.0
        return len(mock_lines) / loc

    def _is_mock_call(self, node: ast.Call) -> bool:
        # Check func name
        return self._is_mock_name(node.func)

    def _is_mock_name(self, node: ast.AST) -> bool:
        if isinstance(node, ast.Name):
            name = node.id.lower()
            return 'mock' in name or 'patch' in name or 'spy' in name
        elif isinstance(node, ast.Attribute):
            name = node.attr.lower()
            if 'mock' in name or 'patch' in name or 'spy' in name:
                return True
            # Recursively check value (e.g. unittest.mock)
            return self._is_mock_name(node.value)
        return False

    def _check_tautology(self, tree: ast.AST) -> bool:
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                # check `assert True` or `assert 1` (but 1 is truthy, usually bad practice if explicit)
                if isinstance(node.test, ast.Constant):
                    if node.test.value is True:
                        return True

                # check `assert x == x`
                if isinstance(node.test, ast.Compare):
                    if len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq):
                        left = node.test.left
                        right = node.test.comparators[0]
                        if self._is_structurally_equal(left, right):
                            return True
        return False

    def _is_structurally_equal(self, left: ast.AST, right: ast.AST) -> bool:
        return ast.dump(left) == ast.dump(right)
