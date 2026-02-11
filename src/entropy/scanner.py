import ast
import re
from typing import List, Tuple, Dict, Any

class Scanner:
    def __init__(self):
        pass

    def scan_file(self, filepath: str) -> Dict[str, Any]:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        loc = self.calculate_loc(content)
        mock_density = self.calculate_mock_density(content, loc)
        token_cost = self.calculate_token_cost(content)

        # AST Analysis
        try:
            tree = ast.parse(content)
            tautologies = self.detect_tautology(tree)
            large_literals = self.find_large_literals(tree)
        except SyntaxError:
            # Might happen if parsing fails (shouldn't for valid python)
            tautologies = False
            large_literals = []

        return {
            "loc": loc,
            "mock_density": mock_density,
            "token_cost": token_cost,
            "has_tautology": tautologies,
            "large_literals": large_literals
        }

    def calculate_loc(self, content: str) -> int:
        lines = content.splitlines()
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
        return len(code_lines)

    def calculate_mock_density(self, content: str, loc: int) -> float:
        if loc == 0:
            return 0.0

        # Regex for common mocking patterns in Python
        # unittest.mock: Mock(), MagicMock(), patch(), patch.object()
        # pytest-mock: mocker.patch(), mocker.spy()
        # manual: .return_value =, .side_effect =
        mock_patterns = [
            r"Mock\(", r"MagicMock\(", r"patch\(", r"spy\(",
            r"\.return_value", r"\.side_effect",
            r"mocker\."
        ]

        mock_lines = 0
        lines = content.splitlines()
        for line in lines:
            if any(re.search(p, line) for p in mock_patterns):
                mock_lines += 1

        return mock_lines / loc

    def calculate_token_cost(self, content: str) -> int:
        # Crude approximation: 4 chars per token
        return len(content) // 4

    def detect_tautology(self, tree: ast.AST) -> bool:
        """
        Detects assert True, assert 1, assert x == x
        """
        class TautologyVisitor(ast.NodeVisitor):
            def __init__(self):
                self.found = False

            def visit_Assert(self, node):
                # check if test is a constant True
                if isinstance(node.test, ast.Constant):
                    if node.test.value is True or (isinstance(node.test.value, int) and node.test.value != 0):
                        self.found = True

                # check if test is comparison x == x
                if isinstance(node.test, ast.Compare):
                    # Check simplistic cases: left == right (first comparator)
                    # This is complex to do perfectly, but checking simple identifiers works.
                    left = node.test.left
                    if node.test.ops and isinstance(node.test.ops[0], ast.Eq) and node.test.comparators:
                        right = node.test.comparators[0]
                        if self._is_same(left, right):
                            self.found = True

                self.generic_visit(node)

            def _is_same(self, n1, n2):
                if isinstance(n1, ast.Name) and isinstance(n2, ast.Name):
                    return n1.id == n2.id
                if isinstance(n1, ast.Constant) and isinstance(n2, ast.Constant):
                    return n1.value == n2.value
                return False

        visitor = TautologyVisitor()
        visitor.visit(tree)
        return visitor.found

    def find_large_literals(self, tree: ast.AST) -> List[Dict[str, Any]]:
        """
        Finds dictionary or list literals that are 'large'.
        Large defined as > 500 characters in source representation (approx).
        """
        large_literals = []

        class LiteralVisitor(ast.NodeVisitor):
            def visit_Dict(self, node):
                self._check_large(node, 'dict')
                self.generic_visit(node)

            def visit_List(self, node):
                self._check_large(node, 'list')
                self.generic_visit(node)

            def _check_large(self, node, type_):
                # We don't have source segment easily in AST without end_lineno/col_offset and source code access
                # mapped perfectly, but we can estimate by number of elements or recursive traversal.
                # A better way is using `ast.unparse` (Python 3.9+) to get source string and check length.
                try:
                    source_segment = ast.unparse(node)
                    if len(source_segment) > 1000: # Threshold for "Bloat"
                        large_literals.append({
                            "type": type_,
                            "lineno": node.lineno,
                            "length": len(source_segment),
                            "node": node # We can't pickle node easily but for now this is in-memory
                        })
                except Exception:
                    pass

        visitor = LiteralVisitor()
        visitor.visit(tree)
        return large_literals
