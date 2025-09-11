"""
Integration tests for pattern file integrity and structure validation.
"""
import os
import re
import yaml
from typing import Dict, List, Tuple
from tests.integration.test_base import AutomatedTest


class TestPatternIntegrity(AutomatedTest):
    """Test the integrity and structure of all pattern files."""

    def __init__(self):
        super().__init__()
        self.patterns_dir = os.path.join(os.path.dirname(__file__), "../../../patterns")
        self.required_sections = [
            "# Pattern",
            "## Purpose",
            "## Functionality",
            "## Pattern Inputs",
            "## Pattern Outputs",
            "## Model Configuration"
        ]

    def run(self):
        """Run the integrity validation tests."""
        # Test case 1: Validate all pattern files exist and are readable
        self._test_pattern_files_accessible()

        # Test case 2: Validate pattern file structure
        self._test_pattern_structure_integrity()

        # Test case 3: Validate YAML sections are valid
        self._test_yaml_validity()

        # Test case 4: Check for duplicate sections
        self._test_no_duplicate_sections()

        # Test case 5: Validate required sections exist
        self._test_required_sections_present()

        return self.results

    def _get_pattern_files(self) -> List[str]:
        """Get all pattern markdown files."""
        pattern_files = []
        if os.path.exists(self.patterns_dir):
            for filename in os.listdir(self.patterns_dir):
                if filename.endswith('.md') and not filename.startswith('_'):
                    pattern_files.append(os.path.join(self.patterns_dir, filename))
        return sorted(pattern_files)

    def _test_pattern_files_accessible(self):
        """Test that all pattern files exist and are readable."""
        pattern_files = self._get_pattern_files()

        if not pattern_files:
            self.add_result(
                "pattern_files_accessible",
                False,
                "No pattern files found in patterns directory",
                {"patterns_dir": self.patterns_dir}
            )
            return

        accessible_files = []
        inaccessible_files = []

        for pattern_file in pattern_files:
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content.strip():
                        accessible_files.append(os.path.basename(pattern_file))
                    else:
                        inaccessible_files.append(f"{os.path.basename(pattern_file)} (empty)")
            except Exception as e:
                inaccessible_files.append(f"{os.path.basename(pattern_file)} (error: {str(e)})")

        success = len(inaccessible_files) == 0

        self.add_result(
            "pattern_files_accessible",
            success,
            f"All {len(accessible_files)} pattern files are accessible" if success
            else f"Found {len(inaccessible_files)} inaccessible files",
            {
                "accessible_files": accessible_files,
                "inaccessible_files": inaccessible_files,
                "total_files": len(pattern_files)
            }
        )

    def _parse_pattern_file(self, file_path: str) -> Dict:
        """Parse a pattern file and extract sections."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        sections = {}
        current_section = None
        current_content = []

        lines = content.split('\n')
        for line_num, line in enumerate(lines, 1):
            # Check for main headers (# Pattern:, ## Purpose:, etc.)
            if re.match(r'^#+ ', line):
                # Save previous section
                if current_section:
                    # Preserve existing metadata (like duplicates) when updating content
                    if current_section in sections:
                        sections[current_section]['content'] = '\n'.join(current_content).strip()
                    else:
                        sections[current_section] = {
                            'content': '\n'.join(current_content).strip(),
                            'line_number': sections.get(current_section, {}).get('line_number', 0)
                        }

                # Start new section
                header = line.strip()
                current_section = header
                current_content = []

                # Track if this section already exists
                if current_section in sections:
                    if 'duplicates' not in sections[current_section]:
                        sections[current_section]['duplicates'] = [sections[current_section]['line_number']]
                    sections[current_section]['duplicates'].append(line_num)
                else:
                    sections[current_section] = {'line_number': line_num}
            else:
                if current_section:
                    current_content.append(line)

        # Save the last section
        if current_section:
            # Preserve existing metadata (like duplicates) when updating content
            if current_section in sections:
                sections[current_section]['content'] = '\n'.join(current_content).strip()
            else:
                sections[current_section] = {
                    'content': '\n'.join(current_content).strip(),
                    'line_number': sections.get(current_section, {}).get('line_number', 0)
                }

        return sections

    def _test_pattern_structure_integrity(self):
        """Test that all pattern files have the correct structure."""
        pattern_files = self._get_pattern_files()

        structure_issues = []
        valid_files = []

        for pattern_file in pattern_files:
            filename = os.path.basename(pattern_file)
            try:
                sections = self._parse_pattern_file(pattern_file)

                # Check for required structure
                issues = []

                # Must start with "# Pattern" (with or without colon)
                pattern_header = None
                for section in sections.keys():
                    if section.startswith('# Pattern'):
                        pattern_header = section
                        break

                if not pattern_header:
                    issues.append("Missing '# Pattern' header")

                # Check for required sections (with or without colons)
                found_sections = set(sections.keys())
                for required in self.required_sections:
                    # Check if section exists with or without colon
                    if not any(section.startswith(required) for section in found_sections):
                        issues.append(f"Missing required section: {required}")

                if issues:
                    structure_issues.append({
                        'file': filename,
                        'issues': issues
                    })
                else:
                    valid_files.append(filename)

            except Exception as e:
                structure_issues.append({
                    'file': filename,
                    'issues': [f"Parse error: {str(e)}"]
                })

        success = len(structure_issues) == 0

        self.add_result(
            "pattern_structure_integrity",
            success,
            f"All {len(valid_files)} pattern files have correct structure" if success
            else f"Found structure issues in {len(structure_issues)} files",
            {
                "valid_files": valid_files,
                "structure_issues": structure_issues,
                "total_files": len(pattern_files)
            }
        )

    def _extract_yaml_blocks(self, content: str) -> List[Tuple[str, int]]:
        """Extract YAML code blocks from markdown content."""
        yaml_blocks = []
        lines = content.split('\n')
        in_yaml_block = False
        yaml_content = []
        start_line = 0

        for line_num, line in enumerate(lines, 1):
            if line.strip() == '```yaml':
                in_yaml_block = True
                yaml_content = []
                start_line = line_num
            elif line.strip() == '```' and in_yaml_block:
                in_yaml_block = False
                yaml_blocks.append(('\n'.join(yaml_content), start_line))
            elif in_yaml_block:
                yaml_content.append(line)

        return yaml_blocks

    def _test_yaml_validity(self):
        """Test that all YAML blocks in pattern files are valid."""
        pattern_files = self._get_pattern_files()

        yaml_issues = []
        valid_yamls = 0
        total_yamls = 0

        for pattern_file in pattern_files:
            filename = os.path.basename(pattern_file)
            try:
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                yaml_blocks = self._extract_yaml_blocks(content)

                for yaml_content, line_num in yaml_blocks:
                    total_yamls += 1
                    try:
                        yaml.safe_load(yaml_content)
                        valid_yamls += 1
                    except yaml.YAMLError as e:
                        yaml_issues.append({
                            'file': filename,
                            'line': line_num,
                            'error': str(e),
                            'yaml_content': yaml_content[:200] + ('...' if len(yaml_content) > 200 else '')
                        })

            except Exception as e:
                yaml_issues.append({
                    'file': filename,
                    'line': 0,
                    'error': f"File read error: {str(e)}",
                    'yaml_content': ''
                })

        success = len(yaml_issues) == 0

        self.add_result(
            "yaml_validity",
            success,
            f"All {valid_yamls} YAML blocks are valid" if success
            else f"Found YAML errors in {len(yaml_issues)} blocks out of {total_yamls}",
            {
                "valid_yamls": valid_yamls,
                "total_yamls": total_yamls,
                "yaml_issues": yaml_issues
            }
        )

    def _test_no_duplicate_sections(self):
        """Test that pattern files don't have duplicate sections."""
        pattern_files = self._get_pattern_files()

        duplicate_issues = []
        clean_files = []

        for pattern_file in pattern_files:
            filename = os.path.basename(pattern_file)
            try:
                sections = self._parse_pattern_file(pattern_file)

                duplicates_found = []
                for section_name, section_data in sections.items():
                    if 'duplicates' in section_data:
                        duplicates_found.append({
                            'section': section_name,
                            'line_numbers': section_data['duplicates']
                        })

                if duplicates_found:
                    duplicate_issues.append({
                        'file': filename,
                        'duplicates': duplicates_found
                    })
                else:
                    clean_files.append(filename)

            except Exception as e:
                duplicate_issues.append({
                    'file': filename,
                    'duplicates': [{'section': 'parse_error', 'error': str(e)}]
                })

        success = len(duplicate_issues) == 0

        self.add_result(
            "no_duplicate_sections",
            success,
            f"All {len(clean_files)} pattern files have unique sections" if success
            else f"Found duplicate sections in {len(duplicate_issues)} files",
            {
                "clean_files": clean_files,
                "duplicate_issues": duplicate_issues,
                "total_files": len(pattern_files)
            }
        )

    def _test_required_sections_present(self):
        """Test that all pattern files have the required sections."""
        pattern_files = self._get_pattern_files()

        missing_sections_issues = []
        complete_files = []

        for pattern_file in pattern_files:
            filename = os.path.basename(pattern_file)
            try:
                sections = self._parse_pattern_file(pattern_file)
                section_headers = set(sections.keys())

                missing_sections = []
                for required in self.required_sections:
                    # Check if any section starts with the required prefix
                    if not any(header.startswith(required) for header in section_headers):
                        missing_sections.append(required)

                if missing_sections:
                    missing_sections_issues.append({
                        'file': filename,
                        'missing_sections': missing_sections,
                        'found_sections': list(section_headers)
                    })
                else:
                    complete_files.append(filename)

            except Exception as e:
                missing_sections_issues.append({
                    'file': filename,
                    'missing_sections': ['parse_error'],
                    'error': str(e)
                })

        success = len(missing_sections_issues) == 0

        self.add_result(
            "required_sections_present",
            success,
            f"All {len(complete_files)} pattern files have required sections" if success
            else f"Found missing sections in {len(missing_sections_issues)} files",
            {
                "complete_files": complete_files,
                "missing_sections_issues": missing_sections_issues,
                "required_sections": self.required_sections,
                "total_files": len(pattern_files)
            }
        )
