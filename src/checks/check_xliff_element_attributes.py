import re
from utils import ValidationIssue
from utils import xliff_check

@xliff_check(4)
def check_xliff_element_attributes(filename, lines):
    """
    CHECK #4: XLIFF Element Attributes
    Validates that the opening <xliff> tag:
    - Exists
    - Has all required attributes: xmlns, version, srcLang, trgLang
    - Attributes are in correct order
    - No extra attributes
    - Values are exact matches
    - trgLang matches the filename's language code
    """

    print("CHECK #4: check_xliff_element_attributes v2 called for", filename)
    validation_issues = []
    expected_attrs = [
        ("xmlns", "urn:oasis:names:tc:xliff:document:2.0"),
        ("version", "2.0"),
        ("srcLang", "en"),
        ("trgLang", None)  # trgLang must match filename
    ]

    expected_prefix = filename.split("(")[-1].split(")")[0] if "(" in filename else ""
    expected_prefix = expected_prefix.strip()

    for i, line in enumerate(lines):
        if '<xliff' in line:
            attr_pattern = re.compile(r'(\w+)="([^"]*)"')
            found_attrs = attr_pattern.findall(line)
            found_names = [name for name, _ in found_attrs]

            # Check for missing required attributes
            for name, _ in expected_attrs:
                if name not in found_names:
                    validation_issues.append(ValidationIssue(
                        validator="XLIFF Element",
                        message=f"Missing required attribute '{name}' in <xliff> tag.",
                        filename=filename,
                        line=i + 1,
                        column_start=1,
                        column_end=len(line.strip()),
                        unit_id=None,
                        text=line.strip()
                    ))
                    return validation_issues

            # Check for out-of-order attributes
            expected_order = [name for name, _ in expected_attrs]
            found_order_trimmed = [name for name in found_names if name in expected_order]
            if found_order_trimmed != expected_order:
                first_wrong = next((ix for ix, (f, e) in enumerate(zip(found_order_trimmed, expected_order)) if f != e), 0)
                mismatch_attr = found_order_trimmed[first_wrong]
                mismatch_span = re.search(fr'{mismatch_attr}="[^"]*"', line)
                if mismatch_span:
                    col_start = mismatch_span.start() + 1
                    col_end = mismatch_span.end() + 1
                    validation_issues.append(ValidationIssue(
                        validator="XLIFF Element",
                        message=f"Attribute '{mismatch_attr}' is out of order in <xliff> tag.",
                        filename=filename,
                        line=i + 1,
                        column_start=col_start,
                        column_end=col_end,
                        unit_id=None,
                        text=line.strip()
                    ))
                    return validation_issues

            # Check for extra attributes
            allowed = {name for name, _ in expected_attrs}
            for name, _ in found_attrs:
                if name not in allowed:
                    mismatch_span = re.search(fr'{name}="[^"]*"', line)
                    if mismatch_span:
                        col_start = mismatch_span.start() + 1
                        col_end = mismatch_span.end() + 1
                        validation_issues.append(ValidationIssue(
                            validator="XLIFF Element",
                            message=f"Unexpected attribute '{name}' in <xliff> tag.",
                            filename=filename,
                            line=i + 1,
                            column_start=col_start,
                            column_end=col_end,
                            unit_id=None,
                            text=line.strip()
                        ))
                        return validation_issues

            # Check trgLang value
            trgLang_value = dict(found_attrs).get("trgLang")
            if expected_prefix and not trgLang_value.startswith(expected_prefix):
                col = line.index("trgLang=") + len("trgLang=") + 2
                validation_issues.append(ValidationIssue(
                    validator="XLIFF Element",
                    message=f"trgLang '{trgLang_value}' does not match filename language code '{expected_prefix}'",
                    filename=filename,
                    line=i + 1,
                    column_start=col,
                    column_end=col + len(trgLang_value),
                    unit_id=None,
                    text=line.strip()
                ))
                return validation_issues

            return validation_issues  # Valid

    validation_issues.append(ValidationIssue(
        validator="XLIFF Element",
        message="Missing <xliff> element.",
        filename=filename,
        line=1,
        column_start=1,
        column_end=1,
        unit_id=None,
        text=lines[0].strip() if lines else "(empty file)"
    ))
    return validation_issues
