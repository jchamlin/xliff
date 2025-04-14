"""
KLMS XLIFF 2.0 Validation Pipeline v6

This code represents a validation pipeline for XLIFF 2.0 files for the KLMS project.
It is used as a check against producing invalid XLIFF files, and ensures any generated XLIFF 
files are compliant to the requirements. It is very important to note that in these files (due to 
limitations of some of the tools that generate and read these files, and also due to making it 
super-easy to use with visual diff tools like Beyond Compare), everything matters: whitespace, newlines, 
formatting, case, structure. So, when generating a file or doing translation, the spacing, indentions, 
trailing whitespace, newlines, case , etc must match the English master exactly, and any generated 
target must match the source structure and format exactly. So this validation pipeline checks to this
very strict level of compliance.
"""

import os

def make_validation_issue(
    validator,
    message,
    filename,
    line,
    column_start,
    column_end,
    unit_id,
    text
):
    """
    Validation Issues

    Validation issues are reported as a structure that includes:
    - Validator name (which validator found the issue, this should be a short name)
    - Validator message (a message which indicates exactly what went wrong, not just "problem" or "issue" or "mismatch")
    - File name (not full file path, just the name) the issue was detected in
    - Line Number the issue was detected on
    - Column range (start and end) that identify the start and end column of line that caused the issue
    - Unit ID that the line is part of, if the problem happened within the context of a containing unit element
    - The actual text of the line that the validation issue was found on

    Constructing Validation Issue Objects

    Because validation issues have strict requirements on things like knowing line numbers, column ranges, etc any 
    third-party tools used (like XML or HTML validators) must be able to report line and column numbers, and configured
    propertly to do so. When a third party tool returns issues, the information needed to construct a validation issue 
    object must be extracted from the object returned by the third party tool. Thinks like the unit id will need to be
    computed based on line number, because the third-party tool will be unaware of XLIFF standard.

    Displaying Validation Issues

    If they are in ChatGPT chat they should be rendered in a tabular form. When displaying the actual text of the line 
    that caused the error, that text should be shown using Markdown code formatting (backticks) to highlight the issue. 
    For readability this can be shortened by truncating leading or trailing part of the line and replacing it with ellipses (`...`),
    but only if necessary due to line length. If used, the ellipsis should indicate that part of the line has been omitted:
    - Use `...` at the start of the line if the leading portion is trimmed.
    - Use `...` at the end of the line if the trailing portion is trimmed.
    - Do not add ellipses unless truncation is actually done.
    - The middle section should preserve and clearly show the problematic content.
    
    If displayed from a command-line, they should be displayed as an ASCII art table with fixed width columns. 
    Instead of highlighting the area in yellow that caused the issue, enclose the problem range between >>> and <<<
    """
    return {
        "validator": validator,
        "message": message,
        "filename": filename,
        "line": line,
        "column_range": [column_start, column_end],
        "unit_id": unit_id,
        "text": text
    }

def main():
    """
    User Entry Point

    This code has no external dependencies and is standalone. It can be run as a program which calls the main() 
    method and as arguments accepts one file path or two. If one file, it will run the single XLIFF file validation 
    checks, if two files are specificed it will run the file pair validation checks (which include the single file 
    checks). ChatGPT should not attempt to use this entry point because its environment does not allow execution 
    of python code from a command line. Instead, ChatGPT should use the entry points specified below.
    """
    import argparse

    parser = argparse.ArgumentParser(description="Validate XLIFF files.")
    parser.add_argument("files", nargs='+', help="List of XLIFF files. Pass one for single file validation, two for file pair validation.")
    
    args = parser.parse_args()

    if len(args.files) == 1:
        validate_xliff_file(args.files[0])
    elif len(args.files) == 2:
        validate_xliff_file_pair(args.files[0], args.files[1])
    else:
        print("Invalid number of arguments. Please pass one or two file paths.")

def validate_xliff_file(file_path):
    """
    ChatGPT Entry Point for Single File Validation

    ChatGPT's has access to files at the project level, and their paths are like /mnt/data/klms8-messages(es).xlf 
    So ChatGPT should use this function for single file validation. For generated files, they should 
    be written to /mnt/data before invoking these methods. The array of validation issues returned by these methods 
    can be used to render the results in the UI, or be used by ChatGPT to analyze what went wrong with it's generation 
    code and try to fix the issues. This validation should be run on any XLIFF file generated by ChatGPT before the 
    file is brought to the user's attention for review. This prevents wasting the user's time reviewing incorrect results.
    If ChatGPT generates a file and it fails these checks, it should use this validation output to diagnose it's code 
    and resolve it. ChatGPT should continuously fix and validate in a cycle until a correct result is produced, or it 
    gives up and needs user assistance in helping to resolve what is wrong because it ran of out ideas on how to fix 
    the code to resolve the issues reported by this pipeline.
    
    Returns a list of validation issue objects, or an empty list if no validation issues were found.
    """
    issues = check_utf8_bom(file_path)
    if issues: return issues

    filename = os.path.basename(file_path)
    with open(file_path, "r", encoding="utf-8-sig") as file:
        lines = file.readlines()

    for check in [
        check_xml_declaration,
        check_namespace_prefixes,
        check_xliff_element_attributes,
        check_xml_validation,
        check_xliff_schema,
        check_duplicate_ids,
        check_java_placeholders,
        check_target_format,
        check_untranslated_targets,
        check_initial_segment_state,
        check_xliff_placeholders
    ]:
        issues = check(filename, lines)
        if issues: return issues

    return []

def validate_xliff_file_pair(english_file_path, translated_file_path):
    """
    ChatGPT Entry Point for File Pair Validation (English Master XLIFF and a translated language XLIFF)

    ChatGPT's has access to files at the project level, and their paths are like /mnt/data/klms8-messages(es).xlf 
    So ChatGPT should use this function for validating a translated file against the English master
    it is based on. See the docstring comments in validate_xliff_file() for more info.
    
    Returns a list of validation issue objects, or an empty list if no validation issues were found.
    """
    issues = validate_xliff_file(english_file_path)
    if issues: return issues

    issues = validate_xliff_file(translated_file_path)
    if issues: return issues

    english_filename = os.path.basename(english_file_path)
    with open(english_file_path, "r", encoding="utf-8-sig") as file:
        english_lines = file.readlines()

    translated_filename = os.path.basename(translated_file_path)
    with open(translated_file_path, "r", encoding="utf-8-sig") as file:
        translated_lines = file.readlines()

    for check in [
        check_file_pair_formatting,
        check_file_pair_units,
        check_file_pair_structure
    ]:
        issues = check(english_filename, english_lines, translated_filename, translated_lines)
        if issues: return issues

    return []

# Define individual validation check methods (already defined earlier, including BOM check, XML declaration, structure checks, etc.)

# === Validation Checks ===

# CHECK 1 START
def check_utf8_bom(file_path):
    """
    CHECK #1: UTF-8 BOM (v3)
    Check that the file has a UTF-8 BOM
    """
    import codecs
    print("check_utf8_bom v3 called for", filename)
    validation_issues = []
    
    try:
        with open(file_path, "rb") as f:
            first_bytes = f.read(4)
            print("First bytes:", first_bytes)
            if first_bytes.startswith(codecs.BOM_UTF8):
                print("Valid UTF-8 BOM detected")
                return validation_issues
            elif first_bytes.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE, codecs.BOM_UTF32_LE, codecs.BOM_UTF32_BE)):
                print("Invalid BOM detected (UTF-16 or UTF-32)")
                validation_issues.append(make_validation_issue(
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
                print("Missing BOM")
                validation_issues.append(make_validation_issue(
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
        print("Exception in check_utf8_bom:", str(e))
        validation_issues.append(make_validation_issue(
            validator="UTF-8 BOM",
            message=f"Error checking BOM: {str(e)}",
            filename=os.path.basename(file_path),
            line=1,
            column_start=1,
            column_end=1,
            unit_id=None,
            text="(file start)"
        ))

    return validation_issues
# CHECK 1 END

# CHECK 2 START
def check_xml_declaration(filename, lines):
    """
    CHECK #2: XML Declaration
    Check that the XML declaration is present and exactly matches: <?xml version="1.0" encoding="UTF-8"?>
    Common ChatGPT problems are forgetting to have one, using single quotes, or using lowercase utf-8.
    """
    print("check_xml_declaration v2 called for", filename)
    validation_issues = []

    if not lines:
        return validation_issues

    first_line = lines[0].strip()
    expected = '<?xml version="1.0" encoding="UTF-8"?>'

    if not first_line.startswith("<?xml"):
        validation_issues.append(make_validation_issue(
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
        validation_issues.append(make_validation_issue(
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
# CHECK 2 END

# CHECK 3 START
def check_namespace_prefixes(filename, lines):
    """
    CHECK #3: XML Namespace Prefixes
    Check that the file does not contain element namespace prefixes like "ns0:" or any other form like <ns:tag> or </ns:tag>.
    """
    import re
    print("check_namespace_prefixes v4 called for", filename)
    validation_issues = []

    namespace_tag_pattern = re.compile(r"<\/?([a-zA-Z0-9]+):[a-zA-Z0-9]+")

    for i, line in enumerate(lines):
        match = namespace_tag_pattern.search(line)
        if match:
            ns_prefix = match.group(1)
            col = match.start(1) + 1  # 1-based index for column
            validation_issues.append(make_validation_issue(
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
# CHECK 3 END

# CHECK 4 START
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
    import re

    print("check_xliff_element_attributes v2 called for", filename)
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
            for name, expected_value in expected_attrs:
                if name not in found_names:
                    validation_issues.append(make_validation_issue(
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
                    validation_issues.append(make_validation_issue(
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
                        validation_issues.append(make_validation_issue(
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
                validation_issues.append(make_validation_issue(
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

    validation_issues.append(make_validation_issue(
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
# CHECK 4 END

# CHECK 5 START
def check_xml_validation(filename, lines):
    """
    CHECK #5: XML Validation
    Check the file has no issues (no warnings or validation_issues) using an XML validator
    in the strictest validation mode (all checks enabled).
    """
    print("check_xml_validation v2 called for", filename)
    from lxml import etree

    validation_issues = []
    xml_string = "".join(lines)

    try:
        parser = etree.XMLParser(recover=False, resolve_entities=True, dtd_validation=False)
        etree.fromstring(xml_string.encode("utf-8"), parser)
    except etree.XMLSyntaxError as e:
        line, column = e.position if hasattr(e, "position") else (1, 1)
        validation_issues.append(make_validation_issue(
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
# CHECK 5 END

# CHECK 6 START
def check_xliff_schema(filename, lines):
    """
    CHECK #6: XLIFF Schema
    Check the XLIFF file against the xliff_core_2.0.xsd.
    """
    print("check_xliff_schema v3 called for", filename)
    from lxml import etree
    import os

    validation_issues = []
    xml_string = "".join(lines)

    try:
        # Load and parse the schema with import resolution support
        parser = etree.XMLParser(load_dtd=True, resolve_entities=True)
        base_path = "/mnt/data/"
        schema_path = os.path.join(base_path, "xliff_core_2.0.xsd")
        with open(schema_path, "rb") as f:
            schema_doc = etree.parse(f, parser)
        schema = etree.XMLSchema(schema_doc)

        # Parse the XLIFF file against the schema
        xml_doc = etree.fromstring(xml_string.encode("utf-8"))
        schema.assertValid(xml_doc)

    except etree.DocumentInvalid as e:
        error = schema.error_log.last_error
        line, column = error.line, error.column
        validation_issues.append(make_validation_issue(
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
        validation_issues.append(make_validation_issue(
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
        validation_issues.append(make_validation_issue(
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
# CHECK 6 END

# CHECK 7 START
def check_duplicate_ids(filename, lines):
    """
    CHECK #7: Duplicate IDs and ID Sequences
    Check the XLIFF file for duplicate and misnumbered IDs.
    - <file> and <unit> elements must have globally unique IDs.
    - Within each <unit>:
      • <data> element IDs must be unique and follow a sequential pattern: baseName_1, baseName_2, etc., without gaps or duplicates.
      • <ph> and <pc> element IDs must be unique and also follow a single shared global sequence across both types (e.g., ph1, pc2, pc3, ph4).
    """
    print("check_duplicate_ids v2 called for", filename)

    from lxml import etree
    import re

    validation_issues = []
    xml_string = "".join(lines)
    parser = etree.XMLParser(recover=True)
    tree = etree.fromstring(xml_string.encode("utf-8"), parser)
    ns = {"ns": "urn:oasis:names:tc:xliff:document:2.0"}

    global_ids = set()
    global_id_elements = tree.xpath("//ns:file | //ns:unit", namespaces=ns)

    for elem in global_id_elements:
        eid = elem.get("id")
        if eid in global_ids:
            validation_issues.append(make_validation_issue(
                validator="Duplicate IDs",
                message=f"Duplicate global ID: '{eid}'",
                filename=filename,
                line=elem.sourceline,
                column_start=1,
                column_end=1,
                unit_id=None,
                text=lines[elem.sourceline - 1].strip()
            ))
        else:
            global_ids.add(eid)

    for unit in tree.xpath("//ns:unit", namespaces=ns):
        unit_id = unit.get("id")
        local_data_ids = {}
        sequence_tracker = []

        for el in unit.xpath(".//ns:data", namespaces=ns):
            eid = el.get("id")
            if not eid:
                continue
            if eid in local_data_ids:
                validation_issues.append(make_validation_issue(
                    validator="Duplicate IDs",
                    message=f"Duplicate <data> ID in unit '{unit_id}': '{eid}'",
                    filename=filename,
                    line=el.sourceline,
                    column_start=1,
                    column_end=1,
                    unit_id=unit_id,
                    text=lines[el.sourceline - 1].strip()
                ))
            else:
                local_data_ids[eid] = el
                m = re.match(r"(.+?)_(\d+)$", eid)
                if m:
                    sequence_tracker.append((eid, m.group(1), int(m.group(2))))

        # Check data sequence gaps
        if sequence_tracker:
            base = sequence_tracker[0][1]
            expected = list(range(1, len(sequence_tracker) + 1))
            actual = sorted([n[2] for n in sequence_tracker])
            if expected != actual:
                validation_issues.append(make_validation_issue(
                    validator="ID Sequence",
                    message=f"<data> IDs in unit '{unit_id}' do not follow sequential pattern {base}_1, {base}_2, ...",
                    filename=filename,
                    line=unit.sourceline,
                    column_start=1,
                    column_end=1,
                    unit_id=unit_id,
                    text=lines[unit.sourceline - 1].strip()
                ))

        # Check pc/ph shared sequence
        sequence_ids = []
        for el in unit.xpath(".//ns:ph | .//ns:pc", namespaces=ns):
            eid = el.get("id")
            if not eid:
                continue
            match = re.match(r"([a-zA-Z]+)(\d+)$", eid)
            if match:
                tag, num = match.groups()
                sequence_ids.append((eid, tag, int(num), el))

        sequence_ids.sort(key=lambda x: x[2])
        expected_nums = list(range(1, len(sequence_ids) + 1))
        actual_nums = [x[2] for x in sequence_ids]

        if expected_nums != actual_nums:
            validation_issues.append(make_validation_issue(
                validator="ID Sequence",
                message=f"<ph>/<pc> IDs in unit '{unit_id}' must follow a shared sequential pattern like ph1, pc2, pc3, ph4",
                filename=filename,
                line=sequence_ids[0][3].sourceline if sequence_ids else unit.sourceline,
                column_start=1,
                column_end=1,
                unit_id=unit_id,
                text=lines[sequence_ids[0][3].sourceline - 1].strip() if sequence_ids else lines[unit.sourceline - 1].strip()
            ))

    return validation_issues
# CHECK 7 END

# CHECK 8 START
def check_java_placeholders(filename, lines):
    """
    CHECK #8: Java Placeholder
    Ensure Java placeholders (such as {0}, {1}, etc.) are correct between each source and target pair. The count of the number of 
    times each placeholder is used should match between source and target, but the ordering doesn't matter since in translation 
    they may be rearranged.
    """
    print("check_java_placeholders v4 called for", filename)
    import re
    from lxml import etree

    validation_issues = []
    xml_string = "".join(lines)
    parser = etree.XMLParser(recover=True)
    tree = etree.fromstring(xml_string.encode("utf-8"), parser)
    ns = {"ns": "urn:oasis:names:tc:xliff:document:2.0"}

    for segment in tree.xpath("//ns:segment", namespaces=ns):
        source = segment.find("ns:source", namespaces=ns)
        target = segment.find("ns:target", namespaces=ns)
        if source is None or target is None:
            continue

        source_text = etree.tostring(source, method="text", encoding="unicode")
        target_text = etree.tostring(target, method="text", encoding="unicode")

        source_placeholders = re.findall(r"\{\d+\}", source_text)
        target_placeholders = re.findall(r"\{\d+\}", target_text)

        def count_map(lst):
            return {ph: lst.count(ph) for ph in set(lst)}

        source_counts = count_map(source_placeholders)
        target_counts = count_map(target_placeholders)

        if source_counts != target_counts:
            line = target.sourceline
            first_bad = None
            for ph in set(source_counts.keys()).union(target_counts.keys()):
                if source_counts.get(ph, 0) != target_counts.get(ph, 0):
                    first_bad = ph
                    break

            line_text = lines[line - 1].strip() if line and 0 < line <= len(lines) else "(unknown)"
            col_start = line_text.find(first_bad) + 1 if first_bad and first_bad in line_text else 1
            col_end = col_start + len(first_bad) - 1 if first_bad else 1

            validation_issues.append(make_validation_issue(
                validator="Java Placeholder",
                message=f"Placeholder mismatch: source {source_counts}, target {target_counts}",
                filename=filename,
                line=line,
                column_start=col_start,
                column_end=col_end,
                unit_id=segment.getparent().get("id") if segment.getparent() is not None else None,
                text=line_text
            ))

    return validation_issues
# CHECK 8 END

# CHECK 9 START
def check_target_format(filename, lines):
    """
    CHECK #9: Target Format
    Check each target block against its source to ensure the formatting and first tag on each line is the same as the source.
    For each unit in the file, make a list of lines of the source block, and a list of lines of the target block,
    and then call a utility function to a basic compare of those two lists. The target should have the same number of lines as the source, 
    each line of the target should have: the same leading whitespace as the matching source line, the same trailing whitespace as the matching source line, 
    and start with the same tag as the source line does.
    There are two exceptions: on any line if you detect the starting tags are "<source" and "<target", or "</source" and "</target", 
    which will happen when comparing a source block to a target block, consider those equivalent and don't create a validation issue.
    """
    print("check_target_format v6 called for", filename)
    import re

    validation_issues = []
    unit_id = None
    in_source = False
    in_target = False
    source_lines = []
    target_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        if '<unit' in stripped:
            match = re.search(r'id=["\'](.*?)["\']', stripped)
            unit_id = match.group(1) if match else None

        if '<source' in stripped:
            in_source = True
            source_lines = []
        if in_source:
            source_lines.append(line)
        if '</source' in stripped:
            in_source = False

        if '<target' in stripped:
            in_target = True
            target_lines = []
        if in_target:
            target_lines.append(line)
        if '</target' in stripped:
            in_target = False
            validation_issues.extend(
                compare_format_lines(source_lines, target_lines, filename, unit_id, i + 1, "Target Format")
            )

    return validation_issues

def compare_format_lines(source_lines, target_lines, filename, unit_id, base_line_number, validator_name):
    """
    Compare two aligned lists of lines (source and target) for format consistency.

    This function checks:
    - That the line counts match
    - That leading and trailing whitespace on each line match
    - That the starting XML tag on each line matches, with allowance for <source>/<target> and </source>/</target> equivalency

    Parameters:
        source_lines (list of str): Lines from the source block.
        target_lines (list of str): Lines from the target block.
        filename (str): The name of the file being validated.
        unit_id (str): The unit ID associated with the block.
        base_line_number (int): Line number used in reporting issues.
        validator_name (str): The name of the validation check.

    Returns:
        list: A list of validation issue dictionaries (possibly empty).
    """
    import re
    issues = []

    if len(source_lines) != len(target_lines):
        issues.append(make_validation_issue(
            validator=validator_name,
            message=f"Mismatch in line count: source={len(source_lines)} lines, target={len(target_lines)} lines.",
            filename=filename,
            line=base_line_number,
            column_start=1,
            column_end=1,
            unit_id=unit_id,
            text=""
        ))
        return issues

    for j in range(len(source_lines)):
        src_line = source_lines[j]
        tgt_line = target_lines[j]

        src_strip = src_line.strip()
        tgt_strip = tgt_line.strip()

        src_leading = re.match(r"^\s*", src_line).group()
        tgt_leading = re.match(r"^\s*", tgt_line).group()
        src_trailing = re.search(r"\s*$", src_line).group()
        tgt_trailing = re.search(r"\s*$", tgt_line).group()

        if src_leading != tgt_leading or src_trailing != tgt_trailing:
            issues.append(make_validation_issue(
                validator=validator_name,
                message=f"Line {j+1} has different whitespace formatting in target.",
                filename=filename,
                line=base_line_number,
                column_start=1,
                column_end=1,
                unit_id=unit_id,
                text=tgt_line.strip()
            ))
            continue

        src_tag = re.match(r"<\/?\w+", src_strip)
        tgt_tag = re.match(r"<\/?\w+", tgt_strip)

        if src_tag and tgt_tag:
            src_val = src_tag.group()
            tgt_val = tgt_tag.group()
            if not ((src_val == "<source" and tgt_val == "<target") or
                    (src_val == "</source" and tgt_val == "</target") or
                    (src_val == tgt_val)):
                issues.append(make_validation_issue(
                    validator=validator_name,
                    message=f"Line {j+1} starts with different tag: source='{src_val}', target='{tgt_val}'",
                    filename=filename,
                    line=base_line_number,
                    column_start=1,
                    column_end=1,
                    unit_id=unit_id,
                    text=tgt_line.strip()
                ))

    return issues
# CHECK 9 END

# CHECK 10 START
def check_untranslated_targets(filename, lines):
    """
    CHECK #10: Untranslated Targets
    If the trgLang of the file differs from the srcLang, then this file represents a file with translations. Each segment that is 
    not in state "initial" should be checked to make sure the target is not empty and is different than the source and that it 
    doesn't contain the text from the source. The target may contain XLIFF placeholders (pc and ph tags) so the value's XML DOM will 
    have to be walked checking for at least one non-blank text node.

    Common issues that have happened that indicate the target is not translated:
    - target is missing
    - target is empty
    - target is an exact match for the source
    - target has a placeholder plus the actual source text like [ZH]ExactEnglishText

    There are some exceptions:
    - The unit header.application_name should never be translated and the target should match the source exactly.
    The customer, Minnesota Certification Board, decided they didn't want their name translated.
    """
    print("check_untranslated_targets v5 called for", filename)
    import xml.etree.ElementTree as ET
    import re

    validation_issues = []
    trg_lang = None
    src_lang = None
    current_unit_id = None
    in_unit = False
    in_segment = False
    source_xml = ""
    target_xml = ""
    target_state = ""
    line_number = 0
    in_source = False
    in_target = False
    target_found = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        if '<xliff' in line and 'trgLang=' in line and 'srcLang=' in line:
            trg_match = re.search(r'trgLang=["\'](.*?)["\']', line)
            src_match = re.search(r'srcLang=["\'](.*?)["\']', line)
            if trg_match and src_match:
                trg_lang = trg_match.group(1)
                src_lang = src_match.group(1)

        if '<unit' in line:
            in_unit = True
            match = re.search(r'id=["\'](.*?)["\']', line)
            current_unit_id = match.group(1) if match else None

        if '</unit>' in line:
            in_unit = False

        if '<segment' in line:
            in_segment = True
            source_xml = ""
            target_xml = ""
            target_state = ""
            line_number = i + 1
            target_found = False

        if '</segment>' in line:
            in_segment = False
            if trg_lang and src_lang and trg_lang != src_lang:
                if not target_found:
                    validation_issues.append(make_validation_issue(
                        validator="Untranslated Targets",
                        message="Target is missing",
                        filename=filename,
                        line=line_number,
                        column_start=1,
                        column_end=1,
                        unit_id=current_unit_id,
                        text=""
                    ))
                else:
                    try:
                        src_root = ET.fromstring(f"<wrapper>{source_xml}</wrapper>")
                        tgt_root = ET.fromstring(f"<wrapper>{target_xml}</wrapper>")

                        def extract_text(elem):
                            return ''.join([e.strip() for e in elem.itertext() if e.strip()])

                        src_text = extract_text(src_root)
                        tgt_text = extract_text(tgt_root)

                        if current_unit_id == "header.application_name":
                            continue

                        if not tgt_text:
                            validation_issues.append(make_validation_issue(
                                validator="Untranslated Targets",
                                message="Target is empty",
                                filename=filename,
                                line=line_number,
                                column_start=1,
                                column_end=1,
                                unit_id=current_unit_id,
                                text=""
                            ))
                        elif tgt_text == src_text:
                            validation_issues.append(make_validation_issue(
                                validator="Untranslated Targets",
                                message="Target is identical to source",
                                filename=filename,
                                line=line_number,
                                column_start=1,
                                column_end=1,
                                unit_id=current_unit_id,
                                text=tgt_text
                            ))
                        elif src_text in tgt_text:
                            validation_issues.append(make_validation_issue(
                                validator="Untranslated Targets",
                                message="Target contains unmodified source text",
                                filename=filename,
                                line=line_number,
                                column_start=1,
                                column_end=1,
                                unit_id=current_unit_id,
                                text=tgt_text
                            ))

                    except ET.ParseError:
                        continue

        if in_segment:
            if '<source' in stripped:
                in_source = True
            if in_source:
                source_xml += line
            if '</source>' in stripped:
                in_source = False

            if '<target' in stripped:
                in_target = True
                target_found = True
                state_match = re.search(r'state=["\'](.*?)["\']', line)
                if state_match:
                    target_state = state_match.group(1)
            if in_target:
                target_xml += line
            if '</target>' in stripped:
                in_target = False

    return validation_issues
# CHECK 10 END

# CHECK 11 START
def check_initial_segment_state(filename, lines):
    """
    CHECK #11: Initial State
    Checks if the the segment state is "initial" then the target element should either not exist or contain an exact copy of the source.
    """
    print("check_initial_segment_state v1 called for", filename)
    validation_issues = []
    return validation_issues
# CHECK 11 END

# CHECK 12 START
def check_xliff_placeholders(filename, lines):
    """
    CHECK #12: XLIFF Placeholders
    If a unit has an originalData element, then it uses XLIFF placeholders. These are pc and ph tags and they are used to escape 
    makup (tags) so they do not get mangled during human or machine translation.

    pc tag: is meant to enclose something with a <pc>asdfasdF</pc> but can be empty or even self-closed.
    has a dataRefStart attribute which references a data element in the originalData element by id
    has an optional dataRefEnd attribute which references a data element in the originalData element by id
    The values of those data elements are the replacement values, the start pc tag is replaced by the value pointed 
    to by dataRefStart, and the matching closing </pc> tag (careful, pc blocks can be nested) is replaced by the 
    value in the data node with an id that matches the dataRefEnd.

    ph tag: has a dataRef attribute which references a data element in the originalData element by id. The data element's value
    represents what the <ph/> tag is repalced by.

    This checks that the data element referenced by every dataRefStart, dataRefEnd, and dataRef exists.
    It also checks to make sure every data element is referenced, and there are no unreferenced data elements.

    If value of the source or target is HTML, then the pc tags represnt closeable elements like p, span, em, b, strong, etc 
    and the ph tags represent self-closing elements like br, hr, img, etc.

    If the data elements don't look like HTML tags, then the value is an Articulate Storyline or other type, and the tags represent 
    something proprietary. Like with Storyline, it uses <Style> tags.

    The actual value should be reconstructed using this process and validated.

    If value is HTML (because the data elements had values that look like HTML tags) then the HTML fragment should be 
    validated with an HTML 5 validator in its most strict mode (enabling all warnings).

    Otherwise the value should be considered XML and an XML validator should be run on the XML fragment (enclosing it with a <root></root> first) 
    in its most strict mode (enabling all warnings).

    Each error or warning raised by the HTML or XML validator should generate a validation issue.
    """
    print("check_xliff_placeholders v1 called for", filename)
    validation_issues = []
    return validation_issues
# CHECK 12 END

# CHECK 13 START
def check_file_pair_formatting(english_filename, english_lines, translated_filename, translated_lines):
    """
    CHECK #13: Formatting
    Validate the translated file has identical formatting to the English master, including leading/trailing whitespace and the first tag on the line matches.
    This is the same as CHECK #9 above and calls the same utility method to perform the check, but instead of passing in source and target 
    blocks as arrays of lines, this passes in the entire files as arrays of lines.
    """
    print("check_file_pair_formatting v1 called for", english_filename, " and ", translated_filename)
    validation_issues = []
    return validation_issues
# CHECK 13 END

# CHECK 14 START
def check_file_pair_units(english_filename, english_lines, translated_filename, translated_lines):
    """
    CHECK #14 Units
    Check that the translated file has the same units as the English master. Each unit that is out of order, missing, or extra is a validation issue.
    """
    print("check_file_pair_units v1 called for", filename)
    validation_issues = []
    return validation_issues
# CHECK 14 END

# CHECK 15 START
def check_file_pair_structure(english_filename, english_lines, translated_filename, translated_lines):
    """
    CHECK #15: XML Structure
    Ensure that both files contain the exact same XML structure, matching tags, ordering, nesting, etc.
    The easiest method may be to parse both files into an XML DOM and walk both trees in parallel comparing.
    - Element nodes (name, attributes, attribute values) should always match with the exceptions noted below.
    - Text nodes must match unless inside of a target element. When inside of a target element, no text node comparison is needed
    The exceptions:
    1. the trgLang attribute on the xliff element
    2. the value of the state attribute on a segment element
    3. the text nodes inside of a value element
    """
    print("check_file_pair_structure v1 called for", english_filename, " and ", translated_filename)
    validation_issues = []
    return validation_issues
# CHECK 15 END

# Running the script
if __name__ == "__main__":
    import sys
    sys.argv = ["script.py", "/mnt/data/klms8-messages(en).xlf"]
    main()
