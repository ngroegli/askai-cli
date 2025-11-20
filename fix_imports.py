#!/usr/bin/env python3
"""
Script to fix import statements after refactoring:
- shared -> utils
- modules -> core
- infrastructure/output -> output
"""

import re
from pathlib import Path

def fix_imports_in_file(file_path):
    """Fix imports in a single Python file"""
    print(f"Processing: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return False

    original_content = content

    # Fix imports from askai.shared to askai.utils
    content = re.sub(
        r'from askai\.shared\.([a-zA-Z_][a-zA-Z0-9_]*)',
        r'from askai.utils.\1',
        content
    )
    content = re.sub(
        r'from askai\.shared import',
        r'from askai.utils import',
        content
    )
    content = re.sub(
        r'import askai\.shared\.([a-zA-Z_][a-zA-Z0-9_]*)',
        r'import askai.utils.\1',
        content
    )

    # Fix imports from askai.modules to askai.core
    content = re.sub(
        r'from askai\.modules\.([a-zA-Z_][a-zA-Z0-9_]*)',
        r'from askai.core.\1',
        content
    )
    content = re.sub(
        r'from askai\.modules import',
        r'from askai.core import',
        content
    )
    content = re.sub(
        r'import askai\.modules\.([a-zA-Z_][a-zA-Z0-9_]*)',
        r'import askai.core.\1',
        content
    )

    # Fix imports from askai.infrastructure.output to askai.output
    content = re.sub(
        r'from askai\.infrastructure\.output\.([a-zA-Z_][a-zA-Z0-9_.]*)',
        r'from askai.output.\1',
        content
    )
    content = re.sub(
        r'from askai\.infrastructure\.output import',
        r'from askai.output import',
        content
    )
    content = re.sub(
        r'import askai\.infrastructure\.output\.([a-zA-Z_][a-zA-Z0-9_.]*)',
        r'import askai.output.\1',
        content
    )

    # Special cases for specific file reorganizations
    # Fix TUI relative imports for consolidated structure
    if 'presentation/tui' in str(file_path):
        content = re.sub(r'from \.\.common', 'from .styles', content)
        content = re.sub(r'from \.\.components', 'from .components', content)

    # Fix API route imports that may have been split
    if 'presentation/api' in str(file_path):
        # Update any remaining old module structure references
        content = re.sub(
            r'from askai\.modules\.([^.]+)\.([^.\s]+)',
            r'from askai.core.\1.\2',
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
        print(f"  ℹ️  No import changes needed in {file_path}")
        return True

def main():
    """Process all Python files in src/askai"""
    src_dir = Path("/home/nicola/Git/askai-cli/src/askai")

    if not src_dir.exists():
        print(f"Error: {src_dir} does not exist")
        return

    # Find all Python files
    py_files = list(src_dir.rglob("*.py"))

    print(f"Found {len(py_files)} Python files to process...")

    success_count = 0
    for py_file in py_files:
        if fix_imports_in_file(py_file):
            success_count += 1

    print(f"\n✅ Successfully processed {success_count}/{len(py_files)} files")

if __name__ == "__main__":
    main()