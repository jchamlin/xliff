import os
from utils import ValidationIssue
from utils import xliff_check

@xliff_check(1)
def check_utf8_bom(file_path):
    """
    CHECK #1: UTF-8 BOM (v3)
    Check that the file has a UTF-8 BOM
    """
    import codecs
    filename=os.path.basename(file_path)
    print("CHECK #1: check_utf8_bom v3 called for", filename)
    validation_issues = []
    
    try:
        with open(file_path, "rb") as f:
            first_bytes = f.read(4)
            if first_bytes.startswith(codecs.BOM_UTF8):
                return validation_issues
            elif first_bytes.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE, codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
                validation_issues.append(ValidationIssue(
                    validator="UTF-8 BOM",
                    message="Invalid BOM: file appears to be UTF-16 or UTF-32 encoded.",
                    filename=filename,
                    line=1,
                    column_start=1,
                    column_end=1,
                    unit_id=None,
                    text="(file start)"
                ))
            else:
                validation_issues.append(ValidationIssue(
                    validator="UTF-8 BOM",
                    message="Missing UTF-8 BOM at start of file",
                    filename=filename,
                    line=1,
                    column_start=1,
                    column_end=1,
                    unit_id=None,
                    text="(file start)"
                ))
    except Exception as e:
        validation_issues.append(ValidationIssue(
            validator="UTF-8 BOM",
            message=f"Error checking BOM: {str(e)}",
            filename=filename,
            line=1,
            column_start=1,
            column_end=1,
            unit_id=None,
            text="(file start)"
        ))

    return validation_issues
