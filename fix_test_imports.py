#!/usr/bin/env python3
"""
Script to fix test imports after refactoring:
- shared -> utils
- modules -> core
- infrastructure -> output
"""

import re
from pathlib import Path

def fix_test_imports(file_path):
    """Fix imports in a test file"""
    print(f"Processing test: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    original_content = content

    # Fix modules references to core
    content = re.sub(
        r'from askai\.modules\.([a-zA-Z_][a-zA-Z0-9_]*)',
        r'from askai.core.\1',
        content
    )
    content = re.sub(
        r'import askai\.modules\.([a-zA-Z_][a-zA-Z0-9_]*)',
        r'import askai.core.\1',
        content
    )

    # Fix shared references to utils
    content = re.sub(
        r'from askai\.shared\.([a-zA-Z_][a-zA-Z0-9_]*)',
        r'from askai.utils.\1',
        content
    )
    content = re.sub(
        r'import askai\.shared\.([a-zA-Z_][a-zA-Z0-9_]*)',
        r'import askai.utils.\1',
        content
    )

    # Fix infrastructure/output references to output
    content = re.sub(
        r'from askai\.infrastructure\.output\.([a-zA-Z_][a-zA-Z0-9_.]*)',
        r'from askai.output.\1',
        content
    )
    content = re.sub(
        r'import askai\.infrastructure\.output\.([a-zA-Z_][a-zA-Z0-9_.]*)',
        r'import askai.output.\1',
        content
    )

    # Fix mock references to use new paths
    content = re.sub(
        r"sys\.modules\['askai\.shared\.config'\]",
        r"sys.modules['askai.utils.config']",
        content
    )
    content = re.sub(
        r"sys\.modules\['askai\.shared\.config\.loader'\]",
        r"sys.modules['askai.utils.config']",
        content
    )
    content = re.sub(
        r"'askai\.shared\.config'",
        r"'askai.utils.config'",
        content
    )
    content = re.sub(
        r"'askai\.shared\.config\.loader'",
        r"'askai.utils.config'",
        content
    )

    # Fix specific file name changes
    content = re.sub(
        r'output_coordinator\.py',
        r'coordinator.py',
        content
    )
    content = re.sub(
        r'pattern_configuration\.py',
        r'configuration.py',
        content
    )
    content = re.sub(
        r'pattern_inputs\.py',
        r'inputs.py',
        content
    )
    content = re.sub(
        r'pattern_outputs\.py',
        r'outputs.py',
        content
    )

    if content != original_content:
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Updated imports in {file_path}")
            return True
        except Exception as e:
            print(f"  ❌ Error writing {file_path}: {e}")
            return False
    else:
        print(f"  ℹ️  No changes needed in {file_path}")
        return True

def main():
    """Process all test files"""
    tests_dir = Path("/home/nicola/Git/askai-cli/tests")

    if not tests_dir.exists():
        print(f"Error: {tests_dir} does not exist")
        return

    # Find all Python test files
    test_files = list(tests_dir.rglob("test_*.py"))
    test_files.extend(list(tests_dir.rglob("*_test.py")))

    print(f"Found {len(test_files)} test files to process...")

    success_count = 0
    for test_file in test_files:
        if fix_test_imports(test_file):
            success_count += 1

    print(f"\n✅ Successfully processed {success_count}/{len(test_files)} test files")

if __name__ == "__main__":
    main()