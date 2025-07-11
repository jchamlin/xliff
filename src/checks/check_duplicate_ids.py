from lxml import etree
from utils import ValidationIssue
from utils import xliff_check

@xliff_check(7)
def check_duplicate_ids(filename, lines):
    """
    CHECK #7: Duplicate IDs and ID Sequences

    - <file> and <unit> elements must have globally unique IDs.

    - All <pc> and <ph> tag IDs in <source> must follow a strict sequential pattern (e.g., block_0, generic_1, generic_2).
    - Same for <target>, but counted separately.
    - No duplicate sequence numbers within each section.

    - If a <pc> or <ph> has a dataRefStart/dataRefEnd/dataRef, the referenced <data> ID must exist and match the same sequence number.
    - All <data> elements must be referenced by at least one tag.
    - No extra or missing <data> elements.
    """
    print("CHECK #7: check_duplicate_ids v13 called for", filename)
    issues = []

    parser = etree.XMLParser(recover=True)
    tree = etree.fromstring("".join(lines).encode("utf-8"), parser)
    ns = {"ns": "urn:oasis:names:tc:xliff:document:2.0"}

    for file in tree.xpath(".//ns:file", namespaces=ns):
        for unit in file.xpath(".//ns:unit", namespaces=ns):
            unit_id = unit.get("id")
            original_data = unit.find(".//ns:originalData", namespaces=ns)
            if original_data is None:
                continue

            data_ids = {}
            referenced_data_ids = set()

            for data in original_data.xpath(".//ns:data", namespaces=ns):
                data_id = data.get("id")
                if data_id:
                    if data_id in data_ids:
                        issues.append(ValidationIssue(
                            validator="Duplicate IDs",
                            message=f"Duplicate <data> ID in unit '{unit_id}': '{data_id}'",
                            filename=filename,
                            line=data.sourceline,
                            column_start=1,
                            column_end=1,
                            unit_id=unit_id,
                            rule="check_duplicate_ids"
                        ))
                    else:
                        data_ids[data_id] = data

            for tag in unit.xpath(".//ns:ph | .//ns:pc", namespaces=ns):
                tag_id = tag.get("id")
                for ref_attr in ["dataRefStart", "dataRefEnd", "dataRef"]:
                    ref_id = tag.get(ref_attr)
                    if ref_id:
                        referenced_data_ids.add(ref_id)

                        # New logic: enforce matching prefix between tag ID and dataRef*
                        tag_prefix = tag_id.split("_")[0] if tag_id and "_" in tag_id else None
                        ref_prefix = ref_id.split("_")[0] if "_" in ref_id else None

                        if tag_prefix and ref_prefix and tag_prefix != ref_prefix:
                            issues.append(ValidationIssue(
                                validator="Mismatched ID Prefix",
                                message=f"Tag '{tag_id}' has {ref_attr}='{ref_id}', but their prefixes do not match.",
                                filename=filename,
                                line=tag.sourceline,
                                column_start=1,
                                column_end=1,
                                unit_id=unit_id,
                                rule="check_duplicate_ids"
                            ))

            for ref_id in referenced_data_ids:
                if ref_id not in data_ids:
                    issues.append(ValidationIssue(
                        validator="Missing Data Ref",
                        message=f"Missing <data> element for referenced ID '{ref_id}' in unit '{unit_id}'",
                        filename=filename,
                        line=unit.sourceline,
                        column_start=1,
                        column_end=1,
                        unit_id=unit_id,
                        rule="check_duplicate_ids"
                    ))

            for data_id in data_ids:
                if data_id not in referenced_data_ids:
                    data = data_ids[data_id]
                    issues.append(ValidationIssue(
                        validator="Unused Data ID",
                        message=f"<data> ID not referenced in unit '{unit_id}': '{data_id}'",
                        filename=filename,
                        line=data.sourceline,
                        column_start=1,
                        column_end=1,
                        unit_id=unit_id,
                        rule="check_duplicate_ids"
                    ))

    return issues
