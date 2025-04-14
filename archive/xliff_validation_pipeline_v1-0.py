# XLIFF 2.0 Full Validation Pipeline (Steps 1–13)
# This script performs schema validation, ID checks, structure comparison,
# placeholder reference validation, HTML validation, and translation checks.

from lxml import etree
from collections import defaultdict
import difflib
from html.parser import HTMLParser

XLIFF_NS = {'x': 'urn:oasis:names:tc:xliff:document:2.0'}

# STEP 1: Schema Validation
def validate_with_schema(schema_path, file_paths):
    with open(schema_path, 'rb') as f:
        schema_doc = etree.parse(f)
    schema = etree.XMLSchema(schema_doc)
    results = {}
    for lang, path in file_paths.items():
        try:
            with open(path, 'rb') as f:
                doc = etree.parse(f)
            schema.assertValid(doc)
            results[lang] = "✅ Valid"
        except Exception as e:
            results[lang] = f"❌ {str(e)}"
    return results

# STEP 2: Global ID Check (excluding <pc>, <ph>, <data>)
def check_global_ids_excluding_scoped(parsed_files):
    scoped_tags = {f"{{{XLIFF_NS['x']}}}pc", f"{{{XLIFF_NS['x']}}}ph", f"{{{XLIFF_NS['x']}}}data"}
    issues = defaultdict(list)
    for lang, root in parsed_files.items():
        if isinstance(root, str): continue
        seen_ids = set()
        for elem in root.iter():
            if elem.tag in scoped_tags: continue
            elem_id = elem.get("id")
            if elem_id:
                if elem_id in seen_ids:
                    issues[lang].append(f"Duplicate ID: {elem_id}")
                seen_ids.add(elem_id)
    return issues

# STEP 3: Scoped ID Check (within <source> and <target>)
def validate_pc_ph_data_ids_scoped(parsed_files):
    relevant_tags = {f"{{{XLIFF_NS['x']}}}pc", f"{{{XLIFF_NS['x']}}}ph", f"{{{XLIFF_NS['x']}}}data"}
    issues = defaultdict(list)
    for lang, root in parsed_files.items():
        if isinstance(root, str): continue
        for unit in root.findall(".//x:file/x:unit", namespaces=XLIFF_NS):
            unit_id = unit.get("id")
            for seg in unit.findall(".//x:segment", namespaces=XLIFF_NS):
                for tag in ["x:source", "x:target"]:
                    elem = seg.find(tag, namespaces=XLIFF_NS)
                    if elem is None: continue
                    seen_ids = set()
                    for child in elem.iter():
                        if child.tag in relevant_tags:
                            cid = child.get("id")
                            if cid:
                                if cid in seen_ids:
                                    issues[lang].append(f"Duplicate ID '{cid}' in {tag} of unit '{unit_id}'")
                                seen_ids.add(cid)
    return issues

# STEP 4: Structure Match Within <source> and <target>
def extract_inline_structure(elem):
    tag_set = {f"{{{XLIFF_NS['x']}}}pc", f"{{{XLIFF_NS['x']}}}ph"}
    return [(e.tag, tuple(sorted(e.attrib.items()))) for e in elem.iter() if e.tag in tag_set]

def validate_pc_ph_structure_match(parsed_files):
    issues = defaultdict(list)
    for lang, root in parsed_files.items():
        if isinstance(root, str): continue
        for unit in root.findall(".//x:file/x:unit", namespaces=XLIFF_NS):
            uid = unit.get("id")
            seg = unit.find(".//x:segment", namespaces=XLIFF_NS)
            if seg is None: continue
            s = seg.find("x:source", namespaces=XLIFF_NS)
            t = seg.find("x:target", namespaces=XLIFF_NS)
            if s is not None and t is not None:
                if extract_inline_structure(s) != extract_inline_structure(t):
                    issues[lang].append(f"Mismatch between <source> and <target> in unit '{uid}'")
    return issues

# STEP 5: Cross-Language Match Against English <source>
def compare_against_english_source(parsed_files):
    issues = defaultdict(list)
    ref = parsed_files["English"]
    baseline = {}
    for unit in ref.findall(".//x:file/x:unit", namespaces=XLIFF_NS):
        uid = unit.get("id")
        seg = unit.find(".//x:segment", namespaces=XLIFF_NS)
        src = seg.find("x:source", namespaces=XLIFF_NS) if seg is not None else None
        if src is not None:
            baseline[uid] = extract_inline_structure(src)
    for lang, root in parsed_files.items():
        if lang == "English" or isinstance(root, str): continue
        for unit in root.findall(".//x:file/x:unit", namespaces=XLIFF_NS):
            uid = unit.get("id")
            seg = unit.find(".//x:segment", namespaces=XLIFF_NS)
            if seg is None or uid not in baseline: continue
            for tag in ["x:source", "x:target"]:
                e = seg.find(tag, namespaces=XLIFF_NS)
                if e is not None and extract_inline_structure(e) != baseline[uid]:
                    issues[lang].append(f"Mismatch in {tag} for unit '{uid}'")
    return issues

# STEP 6: Placeholder Reference Validation

def validate_placeholder_references(parsed_files):
    issues = defaultdict(list)
    for lang, root in parsed_files.items():
        if isinstance(root, str): continue
        for unit in root.findall(".//x:file/x:unit", namespaces=XLIFF_NS):
            uid = unit.get("id")
            seg = unit.find(".//x:segment", namespaces=XLIFF_NS)
            if seg is None: continue
            original = unit.find("x:originalData", namespaces=XLIFF_NS)
            valid_ids = {d.get("id") for d in original.findall("x:data", namespaces=XLIFF_NS)} if original is not None else set()
            used_ids = set()
            for elem in seg.iter():
                if elem.tag == f"{{{XLIFF_NS['x']}}}ph":
                    ref = elem.get("dataRef")
                    if ref and ref not in valid_ids:
                        issues[lang].append(f"Invalid dataRef '{ref}' in unit '{uid}'")
                    if ref:
                        used_ids.add(ref)
                elif elem.tag == f"{{{XLIFF_NS['x']}}}pc":
                    for attr in ["dataRefStart", "dataRefEnd"]:
                        ref = elem.get(attr)
                        if ref and ref not in valid_ids:
                            issues[lang].append(f"Invalid {attr} '{ref}' in unit '{uid}'")
                        if ref:
                            used_ids.add(ref)
            for unused in valid_ids - used_ids:
                issues[lang].append(f"Unused data id '{unused}' in unit '{uid}'")
    return issues

# STEP 7: Language Code Validation

def validate_language_codes(parsed_files):
    issues = defaultdict(list)
    valid_langs = {"en", "es", "hmn", "so"}
    valid_combo = {"ksw-Mymr"}
    for lang, root in parsed_files.items():
        if isinstance(root, str): continue
        src = root.get("srcLang", "").strip()
        trg = root.get("trgLang", "").strip()
        if src and src not in valid_langs:
            issues[lang].append(f"Invalid srcLang: {src}")
        if trg and trg not in valid_langs and trg not in valid_combo:
            issues[lang].append(f"Invalid trgLang: {trg}")
    return issues

# STEP 8: Untranslated Detection with Filters

EXCLUDED_UNITS = {
    "header.application_name",
    "SmartFormComponent.ok",
    "language.hi.name", "language.hi.description",
    "language.hmn.name", "language.hmn.description",
    "language.ksw-Mymr.name", "language.ksw-Mymr.description"
}

def filtered_untranslated_check(parsed_files):
    issues = defaultdict(list)
    english_root = parsed_files["English"]
    reference_sources = {
        unit.get("id"): unit.find(".//x:segment/x:source", namespaces=XLIFF_NS).text.strip()
        for unit in english_root.findall(".//x:file/x:unit", namespaces=XLIFF_NS)
    }
    for lang, root in parsed_files.items():
        if lang == "English" or isinstance(root, str): continue
        for unit in root.findall(".//x:file/x:unit", namespaces=XLIFF_NS):
            uid = unit.get("id")
            if uid not in reference_sources or uid in EXCLUDED_UNITS: continue
            tgt_elem = unit.find(".//x:segment/x:target", namespaces=XLIFF_NS)
            tgt_text = (tgt_elem.text or "").strip() if tgt_elem is not None else ""
            if tgt_text == "" or tgt_text == reference_sources[uid]:
                issues[lang].append(f"Untranslated <target> in unit '{uid}'")
    return issues

# STEP 9: Unit Alignment

def check_unit_alignment(parsed_files):
    base_ids = [unit.get("id") for unit in parsed_files["English"].findall(".//x:file/x:unit", namespaces=XLIFF_NS)]
    mismatch = {}
    for lang, root in parsed_files.items():
        if lang == "English" or isinstance(root, str): continue
        ids = [unit.get("id") for unit in root.findall(".//x:file/x:unit", namespaces=XLIFF_NS)]
        if ids != base_ids:
            mismatch[lang] = f"Mismatch in unit ordering or count"
    return mismatch

# STEP 10: Structure Check (excluding <target> text, preserving state)

def strip_text_recursively(elem):
    elem.text = None
    elem.tail = None
    for child in elem:
        strip_text_recursively(child)

def normalize_structure_for_diff(xml_bytes):
    tree = etree.XML(xml_bytes, parser=etree.XMLParser(remove_blank_text=False))
    for target in tree.xpath("//x:target", namespaces=XLIFF_NS):
        strip_text_recursively(target)
    for xliff in tree.xpath("//x:xliff", namespaces=XLIFF_NS):
        if "trgLang" in xliff.attrib:
            del xliff.attrib["trgLang"]
    return etree.tostring(tree, pretty_print=True, encoding="unicode")

# STEP 11: HTML Validation

class SimpleHTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_error = False
    def error(self, message):
        self.has_error = True

def validate_html_fragments_from_segments(parsed_files):
    issues = defaultdict(list)
    for lang, root in parsed_files.items():
        if isinstance(root, str): continue
        for unit in root.findall(".//x:file/x:unit", namespaces=XLIFF_NS):
            uid = unit.get("id")
            data_map = {d.get("id"): d.text or "" for d in unit.findall("x:originalData/x:data", namespaces=XLIFF_NS)}
            for seg in unit.findall(".//x:segment", namespaces=XLIFF_NS):
                for tag_name in ["x:source", "x:target"]:
                    elem = seg.find(tag_name, namespaces=XLIFF_NS)
                    if elem is None: continue
                    html = ""
                    for node in elem.iter():
                        if node.tag == f"{{{XLIFF_NS['x']}}}ph":
                            html += data_map.get(node.get("dataRef"), "")
                        elif node.tag == f"{{{XLIFF_NS['x']}}}pc":
                            html += data_map.get(node.get("dataRefStart"), "")
                            html += node.text or ""
                            html += data_map.get(node.get("dataRefEnd"), "")
                        elif node.text:
                            html += node.text
                    parser = SimpleHTMLValidator()
                    try:
                        parser.feed(html)
                        if parser.has_error:
                            issues[lang].append(f"Invalid HTML in {tag_name} of unit '{uid}'")
                    except:
                        issues[lang].append(f"Exception parsing HTML in {tag_name} of unit '{uid}'")
    return issues

# STEP 12: Segment Structure Validation

def validate_segment_structure(parsed_files):
    issues = defaultdict(list)
    for lang, root in parsed_files.items():
        if isinstance(root, str): continue
        for unit in root.findall(".//x:file/x:unit", namespaces=XLIFF_NS):
            uid = unit.get("id")
            for seg in unit.findall(".//x:segment", namespaces=XLIFF_NS):
                sources = seg.findall("x:source", namespaces=XLIFF_NS)
                targets = seg.findall("x:target", namespaces=XLIFF_NS)
                if len(sources) != 1:
                    issues[lang].append(f"Segment in unit '{uid}' has {len(sources)} <source> elements")
                if len(targets) != 1:
                    issues[lang].append(f"Segment in unit '{uid}' has {len(targets)} <target> elements")
                elif targets[0].text is None or targets[0].text.strip() == "":
                    issues[lang].append(f"<target> in unit '{uid}' is empty")
                if sources and (sources[0].text is None or sources[0].text.strip() == ""):
                    issues[lang].append(f"<source> in unit '{uid}' is empty")
    return issues

# STEP 13: Namespace Prefix Check

def check_invalid_namespace_prefixes(file_paths):
    issues = {}
    for lang, path in file_paths.items():
        with open(path, "r", encoding="utf-8") as f:
            if "ns0:" in f.read():
                issues[lang] = "Invalid namespace prefix 'ns0:' detected in file."
    return issues

# STEP 14: Final Structure Comparison (includes state)

def final_step_13_structural_check(file_paths):
    reference_path = file_paths["English"]
    with open(reference_path, "rb") as f:
        baseline = normalize_structure_for_diff(f.read())
    mismatches = {}
    for lang, path in file_paths.items():
        if lang == "English": continue
        with open(path, "rb") as f:
            other = normalize_structure_for_diff(f.read())
        if baseline != other:
            diff = list(difflib.unified_diff(baseline.splitlines(), other.splitlines(), lineterm=""))
            mismatches[lang] = diff[:40]  # preview
    return mismatches


# Step 0: Check for exact XML declaration before parsing
def validate_xml_declaration(file_paths, expected='<?xml version="1.0" encoding="UTF-8"?>'):
    issues = {}
    for lang, path in file_paths.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line != expected:
                    issues[lang] = f"Invalid XML declaration: found '{first_line}'"
        except Exception as e:
            issues[lang] = f"Error reading file: {e}"
    return issues


def validate_xml_declaration(file_paths, expected='<?xml version="1.0" encoding="UTF-8"?>'):
    issues = {}
    for lang, path in file_paths.items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                first_line = lines[0].strip()
                if first_line != expected:
                    issues[lang] = f"Invalid XML declaration: found '{first_line}'"

                # New: Compare line counts with English reference
                if lang != "English" and "English" in file_paths:
                    with open(file_paths["English"], "r", encoding="utf-8") as ef:
                        en_lines = ef.readlines()
                        if len(lines) != len(en_lines):
                            issues[lang] = issues.get(lang, "") + f" | Line count mismatch: {len(lines)} vs {len(en_lines)}"
        except Exception as e:
            issues[lang] = f"Error reading file: {e}"
    return issues


def validate_xml_declaration(file_paths, expected='<?xml version="1.0" encoding="UTF-8"?>'):
    issues = {}
    for lang, path in file_paths.items():
        try:
            with open(path, "r", encoding="utf-8-sig") as f:
                lines = f.readlines()
                has_bom = f.encoding.lower().endswith("sig")
                first_line = lines[0].strip()

                # Check XML header
                if first_line != expected:
                    issues[lang] = f"Invalid XML declaration: found '{first_line}'"

                # Check line count
                if lang != "English" and "English" in file_paths:
                    with open(file_paths["English"], "r", encoding="utf-8-sig") as ef:
                        en_lines = ef.readlines()
                        en_has_bom = ef.encoding.lower().endswith("sig")

                        if len(lines) != len(en_lines):
                            issues[lang] = issues.get(lang, "") + f" | Line count mismatch: {len(lines)} vs {len(en_lines)}"

                        # Check BOM match
                        if has_bom != en_has_bom:
                            bom_msg = "Missing BOM" if en_has_bom and not has_bom else "Unexpected BOM"
                            issues[lang] = issues.get(lang, "") + f" | BOM mismatch: {bom_msg}"

        except Exception as e:
            issues[lang] = f"Error reading file: {e}"
    return issues
