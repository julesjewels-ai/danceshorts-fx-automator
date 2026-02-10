import ast
import os

class EntropyScanner(ast.NodeVisitor):
    def __init__(self):
        self.tautologies = 0
        self.imports = []

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            self.imports.append(node.module)
        self.generic_visit(node)

    def visit_Assert(self, node):
        # Check for tautologies
        # assert True
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            self.tautologies += 1
        # assert 1 == 1
        elif isinstance(node.test, ast.Compare):
            if len(node.test.ops) == 1 and isinstance(node.test.ops[0], ast.Eq):
                left = node.test.left
                right = node.test.comparators[0]
                if isinstance(left, ast.Constant) and isinstance(right, ast.Constant):
                     if left.value == right.value:
                         self.tautologies += 1
        self.generic_visit(node)

def scan_file(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    # Count non-empty lines for LOC
    loc = len([l for l in lines if l.strip()])

    # Mock Density: Text-based scan
    mock_keywords = ['mock', 'patch', 'spy', 'magicmock']
    mock_lines_count = 0
    for line in lines:
        l = line.strip().lower()
        if any(keyword in l for keyword in mock_keywords):
            mock_lines_count += 1

    mock_density = mock_lines_count / loc if loc > 0 else 0
    token_cost = len(content) // 4

    # AST Analysis
    try:
        tree = ast.parse(content)
        scanner = EntropyScanner()
        scanner.visit(tree)
        tautologies = scanner.tautologies
        imports = scanner.imports
    except SyntaxError:
        # Might happen if file is invalid python
        tautologies = 0
        imports = []

    return {
        'loc': loc,
        'mock_density': mock_density,
        'token_cost': token_cost,
        'tautologies': tautologies,
        'imports': imports
    }
