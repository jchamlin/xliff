import os
from xliff_validator import validate_xliff_file

def list_xlf_files(folder_path):
    return [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith('.xlf')
    ]

def generate_output_sections(issues_by_file, max_script_output_files=1):
    script_output = []
    test_results = []
    validation_table = []
    line_snippets = []

    script_output.append('# ❌ Script Output\n')
    file_seen = set()
    for issue in issues_by_file:
        if issue.filename not in file_seen:
            script_output.append(f'Validating XLIFF file: {issue.filename}')
            script_output.append(f'CHECK #7: check_duplicate_ids v{issue.validator_version} called for {issue.filename}')
            file_seen.add(issue.filename)
            if len(file_seen) == max_script_output_files:
                break
    script_output.append('')

    test_results.append('# ❌ Test Results Table\n')
    summary = {}
    for issue in issues_by_file:
        summary.setdefault(issue.filename, []).append(issue.message)
    test_results.append('| File | Count | First Message |')
    test_results.append('|------|--------|----------------|')
    for filename, messages in summary.items():
        test_results.append(f'| {os.path.basename(filename)} | {len(messages)} | {messages[0]} |')

    validation_table.append('# ❌ Validation Issues Table\n')
    validation_table.append('| File | Validator | Line | Columns | Message |')
    validation_table.append('|------|-----------|------|---------|---------|')
    for issue in issues_by_file:
        validation_table.append(f'| {os.path.basename(issue.filename)} | {issue.validator} | {issue.line} | {issue.column_start}-{issue.column_end} | {issue.message} |')

    line_snippets.append('# ❌ Highlighted Line Snippets\n')
    seen_files = set()
    for issue in issues_by_file:
        if issue.filename not in seen_files:
            seen_files.add(issue.filename)
            with open(issue.filename, encoding='utf-8') as f:
                lines = f.readlines()
            if 0 < issue.line <= len(lines):
                line = lines[issue.line - 1].rstrip()
                highlighted = (
                    line[:issue.column_start] + '>>>' + line[issue.column_start:issue.column_end] + '<<<' + line[issue.column_end:]
                )
                line_snippets.append(f'- **{os.path.basename(issue.filename)}**')
                line_snippets.append(f'  ```xml\n  {highlighted}\n  ```')

    rule_summary = '# ✅ Test Rule Summary for Check #7\n\n'
    rule_summary += 'This check enforces strict ID management across all tags:\n\n'
    rule_summary += '- All `<file>` and `<unit>` elements must have **globally unique `id` attributes**.\n'
    rule_summary += '- All `<ph>` and `<pc>` tag IDs within each `<unit>` must be **strictly sequential**, alternating if both types are used.\n'
    rule_summary += '- All `<data>` IDs in the `<originalData>` block must be **used by a `dataRef`, `dataRefStart`, or `dataRefEnd`**, and must resolve correctly.\n'
    rule_summary += '- There must be **no missing or extra `<data>` IDs** - every reference must resolve, and every defined ID must be used.\n'
    rule_summary += '- If a `<ph>` or `<pc>` tag references a `<data>` ID, then the **prefix before the `_` in the tag\'s ID and the `dataRef` ID must match** (e.g., `p_0` and `p_0_start`).\n'
    return '\n'.join(script_output + ['\n'] + test_results + ['\n'] + validation_table + ['\n'] + line_snippets + ['\n'] + [rule_summary])

def run_and_save_output(test_dir, output_path):
    issues = []
    for f in list_xlf_files(test_dir):
        issues.extend(validate_xliff_file(f))
    output_md = generate_output_sections(issues)
    with open(output_path, 'w', encoding='utf-8') as out:
        out.write(output_md)
