from utils import ValidationIssue
from utils import xliff_check

@xliff_check(2)
def check_xml_declaration(filename, lines):
    """
    CHECK #2: XML Declaration
    Check that the XML declaration is present and exactly matches: <?xml version="1.0" encoding="UTF-8"?>
    Common ChatGPT problems are forgetting to have one, using single quotes, or using lowercase utf-8.
    """
    print("CHECK #2: check_xml_declaration v2 called for", filename)
    validation_issues = []

    if not lines:
        return validation_issues

    first_line = lines[0].strip()
    expected = '<?xml version="1.0" encoding="UTF-8"?>'

    if not first_line.startswith("<?xml"):
        validation_issues.append(ValidationIssue(
            validator="XML Declaration",
            message="Missing XML declaration at the top of file.",
            filename=filename,
            line=1,
            column_start=1,
            column_end=1,
            unit_id=None,
            text=first_line
        ))
    elif first_line != expected:
        validation_issues.append(ValidationIssue(
            validator="XML Declaration",
            message=f"Invalid XML declaration. Expected: {expected}",
            filename=filename,
            line=1,
            column_start=1,
            column_end=len(first_line),
            unit_id=None,
            text=first_line
        ))

    return validation_issues
