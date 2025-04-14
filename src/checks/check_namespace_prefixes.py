import re
from utils import ValidationIssue
from utils import xliff_check

@xliff_check(3)
def check_namespace_prefixes(filename, lines):
    """
    CHECK #3: XML Namespace Prefixes
    Check that the file does not contain element namespace prefixes like "ns0:" or any other form like <ns:tag> or </ns:tag>.
    """
    print("CHECK #3: check_namespace_prefixes v4 called for", filename)
    validation_issues = []

    namespace_tag_pattern = re.compile(r"<\/?([a-zA-Z0-9]+):[a-zA-Z0-9]+")

    for i, line in enumerate(lines):
        match = namespace_tag_pattern.search(line)
        if match:
            ns_prefix = match.group(1)
            col = match.start(1) + 1  # 1-based index for column
            validation_issues.append(ValidationIssue(
                validator="XML Namespace Prefixes",
                message=f"Namespace prefix '{ns_prefix}:' is not allowed. Remove namespace prefixing from elements.",
                filename=filename,
                line=i + 1,
                column_start=col,
                column_end=col + len(ns_prefix),
                unit_id=None,
                text=line.strip()
            ))
            return validation_issues  # Fail fast on first match

    return validation_issues
