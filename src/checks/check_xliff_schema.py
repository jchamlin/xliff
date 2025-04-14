import os
from utils import Config
from utils import ValidationIssue
from utils import xliff_check

@xliff_check(6)
def check_xliff_schema(filename, lines):
    """
    CHECK #6: XLIFF Schema
    Check the XLIFF file against the xliff_core_2.0.xsd.
    """
    print("CHECK #6: check_xliff_schema v3 called for", filename)
    from lxml import etree

    validation_issues = []
    xml_string = "".join(lines)

    try:
        # Load and parse the schema with import resolution support
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        schema_path = os.path.join(Config.TEST_FILES_PATH, "xliff_core_2.0.xsd")
        with open(schema_path, "rb") as f:
            schema_doc = etree.parse(f, parser)
        schema = etree.XMLSchema(schema_doc)

        # Parse the XLIFF file against the schema
        xml_doc = etree.fromstring(xml_string.encode("utf-8"))
        schema.assertValid(xml_doc)

    except etree.DocumentInvalid as e:
        error = schema.error_log.last_error
        line, column = error.line, error.column
        validation_issues.append(ValidationIssue(
            validator="XLIFF Schema",
            message=f"Schema validation failed: {error.message}",
            filename=filename,
            line=line,
            column_start=column,
            column_end=column + 1,
            unit_id=None,
            text=lines[line - 1].strip() if 0 < line <= len(lines) else "(line unavailable)"
        ))

    except etree.XMLSyntaxError as e:
        line, column = e.position if hasattr(e, "position") else (1, 1)
        validation_issues.append(ValidationIssue(
            validator="XLIFF Schema",
            message=f"XML parsing failed: {e.args[0]}",
            filename=filename,
            line=line,
            column_start=column,
            column_end=column + 1,
            unit_id=None,
            text=lines[line - 1].strip() if 0 < line <= len(lines) else "(line unavailable)"
        ))

    except Exception as e:
        validation_issues.append(ValidationIssue(
            validator="XLIFF Schema",
            message=f"Unexpected error during schema validation: {str(e)}",
            filename=filename,
            line=1,
            column_start=1,
            column_end=1,
            unit_id=None,
            text="(schema validation failed unexpectedly)"
        ))

    return validation_issues
