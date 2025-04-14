import re
from utils import ValidationIssue
from utils import xliff_check

@xliff_check(10)
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
    print("CHECK #10: check_untranslated_targets v5 called for", filename)
    import xml.etree.ElementTree as ET

    validation_issues = []
    trg_lang = None
    src_lang = None
    current_unit_id = None
    in_segment = False
    source_xml = ""
    target_xml = ""
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
            match = re.search(r'id=["\'](.*?)["\']', line)
            current_unit_id = match.group(1) if match else None

        if '<segment' in line:
            in_segment = True
            source_xml = ""
            target_xml = ""
            line_number = i + 1
            target_found = False

        if '</segment>' in line:
            in_segment = False
            if trg_lang and src_lang and trg_lang != src_lang:
                if not target_found:
                    validation_issues.append(ValidationIssue(
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
                            validation_issues.append(ValidationIssue(
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
                            validation_issues.append(ValidationIssue(
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
                            validation_issues.append(ValidationIssue(
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
            if in_target:
                target_xml += line
            if '</target>' in stripped:
                in_target = False

    return validation_issues
