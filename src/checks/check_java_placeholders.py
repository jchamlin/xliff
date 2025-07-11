import re
from utils import ValidationIssue
from utils import xliff_check

@xliff_check(8)
def check_java_placeholders(filename, lines):
    """
    CHECK #8: Java Placeholder
    Ensure Java placeholders (such as {0}, {1}, etc.) are correct between each source and target pair. The count of the number of 
    times each placeholder is used should match between source and target, but the ordering doesn't matter since in translation 
    they may be rearranged.
    """
    print("CHECK #8: check_java_placeholders v4 called for", filename)
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

            validation_issues.append(ValidationIssue(
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
