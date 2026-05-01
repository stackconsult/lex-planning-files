#!/usr/bin/env python3
"""Build validation script for LexCore + LexRadar.

Runs comprehensive syntax checks, import validation, and
test discovery to verify build integrity before committing.
"""
import ast
import sys
from pathlib import Path
from typing import List, Tuple


def check_syntax(file_path: Path) -> Tuple[bool, str]:
    """Check Python file syntax."""
    try:
        with open(file_path, "r") as f:
            ast.parse(f.read())
        return True, "OK"
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"


def validate_imports(file_path: Path) -> Tuple[bool, str]:
    """Validate that imports are resolvable."""
    try:
        with open(file_path, "r") as f:
            tree = ast.parse(f.read())
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                module = node.module
                if module and module.startswith("src."):
                    # Check if module exists
                    parts = module.split(".")
                    current = Path("backend")
                    for part in parts:
                        current = current / part
                        if not current.exists() and not (current.parent / f"{part}.py").exists():
                            return False, f"Import not found: {module}"
        return True, "OK"
    except Exception as e:
        return False, str(e)


def discover_tests(test_dir: Path) -> List[Path]:
    """Discover test files."""
    return list(test_dir.rglob("test_*.py"))


def main():
    """Run full build validation."""
    backend = Path("backend")
    src_dir = backend / "src"
    test_dir = backend / "tests"
    
    print("=" * 60)
    print("LEXCORE + LEXRADAR BUILD VALIDATION")
    print("=" * 60)
    
    # Syntax check all Python files
    print("\n[1/4] Syntax Validation")
    python_files = list(src_dir.rglob("*.py"))
    syntax_pass = 0
    syntax_fail = 0
    
    for f in python_files:
        ok, msg = check_syntax(f)
        if ok:
            syntax_pass += 1
        else:
            syntax_fail += 1
            print(f"  FAIL {f}: {msg}")
    
    print(f"  {syntax_pass}/{len(python_files)} files passed syntax check")
    
    # Import validation
    print("\n[2/4] Import Validation")
    import_pass = 0
    import_fail = 0
    
    for f in python_files:
        ok, msg = validate_imports(f)
        if ok:
            import_pass += 1
        else:
            import_fail += 1
            print(f"  FAIL {f}: {msg}")
    
    print(f"  {import_pass}/{len(python_files)} files passed import check")
    
    # Test discovery
    print("\n[3/4] Test Discovery")
    tests = discover_tests(test_dir)
    print(f"  Found {len(tests)} test files:")
    for t in tests:
        print(f"    - {t.relative_to(backend)}")
    
    # Architecture validation
    print("\n[4/4] Architecture Validation")
    required_dirs = [
        "src/api/routes",
        "src/core",
        "src/connectors",
        "src/workers",
        "alembic/versions",
        "tests/integration",
        "tests/unit",
    ]
    
    for d in required_dirs:
        path = backend / d
        if path.exists():
            files = list(path.rglob("*.py"))
            print(f"  OK {d} ({len(files)} files)")
        else:
            print(f"  MISSING {d}")
    
    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)
    print(f"Syntax:      {syntax_pass}/{len(python_files)} pass")
    print(f"Imports:     {import_pass}/{len(python_files)} pass")
    print(f"Tests:       {len(tests)} files discovered")
    print(f"Status:      {'PASS' if syntax_fail == 0 and import_fail == 0 else 'FAIL'}")
    print("=" * 60)
    
    return 0 if (syntax_fail == 0 and import_fail == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
