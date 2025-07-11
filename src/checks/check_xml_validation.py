from utils import ValidationIssue
from utils import xliff_check

@xliff_check(5)
def check_xml_validation(filename, lines):
    """
    CHECK #5: XML Validation
    Check the file has no issues (no warnings or validation_issues) using an XML validator
    in the strictest validation mode (all checks enabled).
    """
    print("CHECK #5: check_xml_validation v2 called for", filename)
    from lxml import etree

    validation_issues = []
    xml_string = "".join(lines)

    try:
        parser = etree.XMLParser(recover=False, resolve_entities=True, dtd_validation=False)
        etree.fromstring(xml_string.encode("utf-8"), parser)
    except etree.XMLSyntaxError as e:
        line, column = e.position if hasattr(e, "position") else (1, 1)
        validation_issues.append(ValidationIssue(
            validator="XML Validation",
            message=f"XML parsing failed: {e.args[0]}",
            filename=filename,
            line=line,
            column_start=column,
            column_end=column + 1,
            unit_id=None,
            text=lines[line - 1].strip() if 0 < line <= len(lines) else "(line unavailable)"
        ))

    return validation_issues
