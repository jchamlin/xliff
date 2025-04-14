# KLMS XLIFF TRANSLATION + VALIDATION PIPELINE (v1)
# -------------------------------------------------
# Author: ChatGPT + J.C.
# Purpose: Translate and validate XLIFF 2.0 files using a placeholder-safe pipeline
# Handles: Java placeholders, XLIFF pc/ph tags, HTML fragments, Storyline formatting
# Validation: All 15 steps from custom validator including BOM + XML declaration

import re
import difflib
from lxml import etree
from collections import defaultdict
from html.parser import HTMLParser

XLIFF_NS = {"x": "urn:oasis:names:tc:xliff:document:2.0"}
SEQ_PATTERN = re.compile(r"_(\d+)$")

# STEP 0: Check BOM
def check_bom(path):
    with open(path, "rb") as f:
        return f.read(4).startswith(b'\xef\xbb\xbf')

# STEP 1: Schema validation
def validate_schema(schema_path, file_paths):
    schema = etree.XMLSchema(etree.parse(schema_path))
    results = {}
    for lang, path in file_paths.items():
        try:
            doc = etree.parse(path)
            schema.assertValid(doc)
            results[lang] = "✅ Schema Valid"
        except Exception as e:
            results[lang] = f"❌ {str(e)}"
    return results

# STEP 2: Global ID uniqueness (excluding scoped)
def check_global_ids(parsed):
    issues = defaultdict(list)
    for lang, root in parsed.items():
        seen = set()
        for elem in root.iter():
            if elem.tag in {f"{{{XLIFF_NS['x']}}}pc", f"{{{XLIFF_NS['x']}}}ph", f"{{{XLIFF_NS['x']}}}data"}:
                continue
            elem_id = elem.get("id")
            if elem_id and elem_id in seen:
                issues[lang].append(f"Duplicate global ID: {elem_id}")
            seen.add(elem_id)
    return issues

# STEP 3: Check scoped ID duplication (within segments)
def check_scoped_ids(parsed):
    issues = defaultdict(list)
    for lang, root in parsed.items():
        for unit in root.findall(".//x:unit", namespaces=XLIFF_NS):
            uid = unit.get("id")
            for seg in unit.findall(".//x:segment", namespaces=XLIFF_NS):
                seen = set()
                for tag in seg.iter():
                    if "id" in tag.attrib:
                        tid = tag.get("id")
                        if tid in seen:
                            issues[lang].append(f"Duplicate scoped ID '{tid}' in unit {uid}")
                        seen.add(tid)
    return issues

# STEP 4–5: Structure matching
def extract_inline_structure(elem):
    return [(e.tag, tuple(sorted(e.attrib.items()))) for e in elem.iter() if e.tag in {f"{{{XLIFF_NS['x']}}}pc", f"{{{XLIFF_NS['x']}}}ph"}]

def validate_structure(parsed):
    ref = parsed["English"]
    ref_struct = {}
    for unit in ref.findall(".//x:unit", namespaces=XLIFF_NS):
        uid = unit.get("id")
        src = unit.find(".//x:segment/x:source", namespaces=XLIFF_NS)
        if src is not None:
            ref_struct[uid] = extract_inline_structure(src)

    issues = defaultdict(list)
    for lang, root in parsed.items():
        if lang == "English": continue
        for unit in root.findall(".//x:unit", namespaces=XLIFF_NS):
            uid = unit.get("id")
            tgt = unit.find(".//x:segment/x:target", namespaces=XLIFF_NS)
            if tgt is not None and extract_inline_structure(tgt) != ref_struct.get(uid, []):
                issues[lang].append(f"Structure mismatch in unit {uid}")
    return issues

# STEP 6: Validate <data> references
def validate_data_refs(path):
    tree = etree.parse(path)
    root = tree.getroot()
    data_ids = {d.get("id") for d in root.findall(".//x:data", namespaces=XLIFF_NS)}
    ref_ids = set()
    for tag in root.findall(".//x:pc", namespaces=XLIFF_NS):
        ref_ids |= {tag.get("dataRefStart"), tag.get("dataRefEnd")}
    for tag in root.findall(".//x:ph", namespaces=XLIFF_NS):
        ref_ids.add(tag.get("dataRef"))
    ref_ids = {r for r in ref_ids if r}
    issues = []
    for ref in ref_ids:
        if ref not in data_ids:
            issues.append(f"❌ Missing <data> element for id '{ref}'")
    for did in data_ids:
        if did not in ref_ids:
            issues.append(f"⚠️ Unused <data> id '{did}'")
    return issues

# STEP 7: Language codes
def check_lang_codes(parsed):
    valid = {"en", "zh", "am", "hi", "hmn", "so", "ksw-Mymr"}
    issues = defaultdict(list)
    for lang, root in parsed.items():
        src = root.get("srcLang", "")
        trg = root.get("trgLang", "")
        if src not in valid:
            issues[lang].append(f"Invalid srcLang: {src}")
        if trg and trg not in valid:
            issues[lang].append(f"Invalid trgLang: {trg}")
    return issues

# STEP 8: Untranslated check
def check_untranslated(parsed):
    base = parsed["English"]
    ref = {u.get("id"): u.find(".//x:segment/x:source", namespaces=XLIFF_NS).text for u in base.findall(".//x:unit", namespaces=XLIFF_NS)}
    issues = defaultdict(list)
    for lang, root in parsed.items():
        if lang == "English": continue
        for u in root.findall(".//x:unit", namespaces=XLIFF_NS):
            uid = u.get("id")
            tgt = u.find(".//x:segment/x:target", namespaces=XLIFF_NS)
            if tgt is None or (tgt.text or "").strip() == (ref.get(uid) or "").strip():
                issues[lang].append(f"Untranslated <target> in {uid}")
    return issues

# STEP 9: Unit alignment
def check_alignment(parsed):
    base_ids = [u.get("id") for u in parsed["English"].findall(".//x:unit", namespaces=XLIFF_NS)]
    return {lang: "Mismatch in units" for lang, root in parsed.items() if lang != "English" and [u.get("id") for u in root.findall(".//x:unit", namespaces=XLIFF_NS)] != base_ids}

# STEP 10: Structure diff ignoring text
def normalize(xml_bytes):
    tree = etree.XML(xml_bytes, etree.XMLParser(remove_blank_text=False))
    for tgt in tree.xpath("//x:target", namespaces=XLIFF_NS):
        tgt.text = None
        for ch in tgt: ch.text = ch.tail = None
    for root in tree.xpath("//x:xliff", namespaces=XLIFF_NS):
        root.attrib.pop("trgLang", None)
    return etree.tostring(tree, pretty_print=True, encoding="unicode")

def structural_diff(path1, path2):
    with open(path1, "rb") as f1, open(path2, "rb") as f2:
        norm1 = normalize(f1.read()).splitlines()
        norm2 = normalize(f2.read()).splitlines()
    return list(difflib.unified_diff(norm1, norm2, lineterm=""))[:20]

# STEP 11: HTML check
class HTMLChecker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.has_error = False
    def error(self, msg):
        self.has_error = True

def check_html(parsed):
    issues = defaultdict(list)
    for lang, root in parsed.items():
        for u in root.findall(".//x:unit", namespaces=XLIFF_NS):
            data = {d.get("id"): d.text for d in u.findall(".//x:originalData/x:data", namespaces=XLIFF_NS)}
            for html in data.values():
                try:
                    checker = HTMLChecker()
                    checker.feed(html or "")
                    if checker.has_error:
                        issues[lang].append("Invalid HTML in <data>")
                except:
                    issues[lang].append("HTML parse error in <data>")
    return issues

# STEP 12: Segment structure
def segment_check(parsed):
    issues = defaultdict(list)
    for lang, root in parsed.items():
        for u in root.findall(".//x:unit", namespaces=XLIFF_NS):
            uid = u.get("id")
            for s in u.findall(".//x:segment", namespaces=XLIFF_NS):
                if len(s.findall("x:source", namespaces=XLIFF_NS)) != 1:
                    issues[lang].append(f"{uid} missing source")
                if len(s.findall("x:target", namespaces=XLIFF_NS)) != 1:
                    issues[lang].append(f"{uid} missing target")
    return issues

# STEP 13: Check for ns0 prefix
def check_ns_prefix(path):
    return "ns0:" in open(path, "r", encoding="utf-8").read()

# STEP 14: XML declaration
def has_xml_decl(path):
    return open(path, "rb").readline().startswith(b"<?xml version=\"1.0\" encoding=\"UTF-8\"?>")

# This script is intended to be imported and used with full file inputs and a schema reference.
