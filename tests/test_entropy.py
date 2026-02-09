import pytest
import ast
import tempfile
import os
from src.entropy.models import EntropyConfig, RotVerdict, RotTag
from src.entropy.scanner import RotScanner
from src.entropy.git_utils import get_file_churn

def test_scanner_tautology():
    scanner = RotScanner(EntropyConfig())
    code = "def test_x(): assert True"
    tree = ast.parse(code)
    assert scanner._check_tautology(tree) is True

    code2 = "def test_y(): assert 1 == 1"
    tree2 = ast.parse(code2)
    assert scanner._check_tautology(tree2) is True

    code3 = "def test_z(): assert 1 == 2"
    tree3 = ast.parse(code3)
    assert scanner._check_tautology(tree3) is False

def test_scanner_mock_density():
    scanner = RotScanner(EntropyConfig())
    code = """from unittest.mock import MagicMock
def test_x():
    m = MagicMock()
    m2 = MagicMock()
"""
    tree = ast.parse(code)
    density = scanner._calculate_mock_density(tree, 5)
    assert density == 0.4

def test_scan_file_integration():
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.py') as f:
        f.write("def test_foo(): assert True")
        path = f.name

    try:
        scanner = RotScanner(EntropyConfig())
        health, verdict = scanner.scan_file(path)
        assert RotTag.TAUTOLOGY in verdict.tags
    finally:
        os.remove(path)

def test_churn():
    if os.path.exists("README.md"):
        churn = get_file_churn("README.md")
        assert isinstance(churn, int)
        assert churn >= 0
