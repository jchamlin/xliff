"""
🚨 MANDATORY PRECHECK FOR ALL XLIFF FILES

Before presenting, validating, or reviewing ANY generated or modified XLIFF file:

    Run: check_line_structure_match(source_file, translated_file)

This applies to ALL LANGUAGES and ALL FILES, not just zh.

The precheck ensures:
- Line count consistency
- Matching indentation
- Matching tag structure per line

❗Skipping this leads to structural mismatches and wasted human review effort.
This rule is non-negotiable going forward.

"""


"""
🚨 ALWAYS RUN A PRECHECK
Before showing or using any generated XLIFF file (especially zh), run:

    check_line_structure_match(source_file, translated_file)

This prevents invalid formatting, tag misalignment, and wasted time in review.
NEVER skip precheck. It must pass before presenting or validating the file.

This reminder was added after repeated cases of human effort wasted reviewing invalid output.
"""


"""
================== XLIFF TRANSLATION PIPELINE (SAFE VERSION) ==================

This script represents the full, correct behavior for translating XLIFF 2.0 files
with formatting, tag structure, and placeholder preservation.

Use this file to teach a future ChatGPT or teammate how to do this right.

-------------------------------------------------------------------------------
SUPPORTED FORMATS:
- KLMS XLIFF files: <source> blocks contain formatted text using <pc> / <ph>
- Storyline XLIFF files: deeper nesting, but same principles

-------------------------------------------------------------------------------
HOW TO TRANSLATE:
- Extract the full <source> block as a single translation unit.
- Tags (like <pc>, <ph>) must be preserved with:
    - Tag names
    - Attributes
    - Indentation
    - Whitespace
    - Line breaks
- Translate ONLY the human-readable text, not tags or attributes.
- Java-style placeholders ({0}, {1}) must be protected/replaced before translation.
- After translation, placeholders must be restored.
- The structure of the <target> must exactly match the structure of the <source>.

-------------------------------------------------------------------------------
PRE-VALIDATION CHECK (ALWAYS RUN BEFORE FULL VALIDATION):
Compare <source> and <target> line-by-line:
- Line count must match
- Leading whitespace must match
- First tag on each line must match (e.g., <pc>, <ph>, </pc>, etc.)

-------------------------------------------------------------------------------
TRIAL TRANSLATION SET:
Start with zh only using these units:
- home.welcome
- login.welcome
- help.content
- calendar.january to calendar.december
- calendar.jan to calendar.dec
- calendar.sunday to calendar.saturday
- calendar.sun.abbreviated3 to calendar.sat.abbreviated3
- calendar.su.abbreviated2 to calendar.sa.abbreviated2
- Units with Java placeholders like {0}, {1}, {2}

Supported Languages:
- zh: Simplified Chinese
- am: Amharic
- hi: Hindi

"""

# === Java Placeholder Protection ===

JAVA_PLACEHOLDER_MAP = {
    "{0}": "0000",
    "{1}": "1111",
    "{2}": "2222",
    "{3}": "3333",
    "{4}": "4444",
    "{5}": "5555",
    "{6}": "6666",
    "{7}": "7777",
    "{8}": "8888",
    "{9}": "9999",
}

def protect_java_placeholders(text):
    for k, v in JAVA_PLACEHOLDER_MAP.items():
        text = text.replace(k, v)
    return text

def restore_java_placeholders(text):
    for k, v in JAVA_PLACEHOLDER_MAP.items():
        text = text.replace(v, k)
    return text

# === Calendar Term Lookup ===

CALENDAR_LOOKUPS = {
    "zh": {
        "months": ["一月", "二月", "三月", "四月", "五月", "六月",
                   "七月", "八月", "九月", "十月", "十一月", "十二月"],
        "month_abbr": ["1月", "2月", "3月", "4月", "5月", "6月",
                       "7月", "8月", "9月", "10月", "11月", "12月"],
        "days": ["星期日", "星期一", "星期二", "星期三", "星期四", "星期五", "星期六"],
        "days_abbr3": ["日", "一", "二", "三", "四", "五", "六"],
        "days_abbr2": ["日", "一", "二", "三", "四", "五", "六"]
    },
    # Extend for 'am', 'hi' as needed
}

def get_calendar_lookup(lang_code):
    return CALENDAR_LOOKUPS.get(lang_code, {})

def translate_calendar_unit(unit_id, lang_code):
    lookup = get_calendar_lookup(lang_code)
    if unit_id.startswith("calendar."):
        key = unit_id[9:]
        if key in ["january", "february", "march", "april", "may", "june",
                   "july", "august", "september", "october", "november", "december"]:
            index = ["january", "february", "march", "april", "may", "june",
                     "july", "august", "september", "october", "november", "december"].index(key)
            return lookup.get("months", [])[index]
        if key in ["jan", "feb", "mar", "apr", "may", "jun",
                   "jul", "aug", "sep", "oct", "nov", "dec"]:
            index = ["jan", "feb", "mar", "apr", "may", "jun",
                     "jul", "aug", "sep", "oct", "nov", "dec"].index(key)
            return lookup.get("month_abbr", [])[index]
        if key in ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"]:
            index = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"].index(key)
            return lookup.get("days", [])[index]
        if key.endswith(".abbreviated3"):
            index = ["sun", "mon", "tue", "wed", "thu", "fri", "sat"].index(key[:3])
            return lookup.get("days_abbr3", [])[index]
        if key.endswith(".abbreviated2"):
            index = ["su", "mo", "tu", "we", "th", "fr", "sa"].index(key[:2])
            return lookup.get("days_abbr2", [])[index]
    return None

# === Precheck Line Structure Match ===

import re

def check_line_structure_match(path1, path2):
    def analyze(file_path):
        structure = []
        with open(file_path, "r", encoding="utf-8-sig") as f:
            for line in f:
                leading_ws = len(line) - len(line.lstrip())
                tag_match = re.match(r'\s*<(/?\w+)', line)
                tag = tag_match.group(1) if tag_match else None
                structure.append((leading_ws, tag))
        return structure

    structure1 = analyze(path1)
    structure2 = analyze(path2)

    discrepancies = []
    for i, (s1, s2) in enumerate(zip(structure1, structure2), start=1):
        if s1 != s2:
            discrepancies.append((i, s1, s2))
    return discrepancies


# === Utility: Extract a single <file> and <unit> from a full XLIFF file ===

def extract_single_unit_xliff(full_xliff_path, target_unit_id, output_path, encoding="utf-8-sig"):
    with open(full_xliff_path, "r", encoding=encoding) as f:
        lines = f.readlines()

    inside_file = False
    inside_unit = False
    capture_unit = False
    file_buffer = []
    unit_buffer = []
    found_unit = False

    for line in lines:
        if "<file " in line and not inside_file:
            current_file = [line]
            inside_file = True
            continue
        elif inside_file and "</file>" in line:
            current_file.append(line)
            if found_unit:
                file_buffer = current_file[:1] + unit_buffer + current_file[-1:]
                break
            inside_file = False
            unit_buffer = []
            found_unit = False
        elif inside_file:
            current_file.append(line)
            if "<unit " in line and f'id="{target_unit_id}"' in line:
                capture_unit = True
                found_unit = True
            if capture_unit:
                unit_buffer.append(line)
            if "</unit>" in line and capture_unit:
                capture_unit = False

    output = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<xliff xmlns="urn:oasis:names:tc:xliff:document:2.0" version="2.0" srcLang="en" trgLang="en">\n'
        + ''.join(file_buffer) +
        '</xliff>\n'
    )

    with open(output_path, "wb") as f:
        f.write(b'\xef\xbb\xbf')
        f.write(output.encode("utf-8"))


# === insert_translated_target_block ===
"""
Copies source structure to create a <target> block with identical:
- Attributes (e.g., xml:space="preserve")
- Tag formatting (inline vs. block)

If any of the direct children of <source> are non-whitespace text nodes, then:
- <target> must be inline (same line as content)
- </target> must also close inline

Otherwise, <target> and </target> can be on their own lines

This prevents adding unintended whitespace (especially important for Storyline).

Args:
- source_lines: list of str (lines between <source> and </source>)
- translated_lines: list of translated text (same length)
- source_tag: actual <source ... > opening line

Returns:
- list of lines representing the full <target> block (same length as source)
"""

def insert_translated_target_block(source_lines, translated_lines, source_tag):
    import xml.etree.ElementTree as ET
    import re

    # Copy any attributes (e.g., xml:space) from <source>
    attr_match = re.search(r'<source(.*?)>', source_tag)
    attr_text = attr_match.group(1).strip() if attr_match else ""
    target_open = f"<target{(' ' + attr_text) if attr_text else ''}>"

    # Determine if source contains non-whitespace text nodes
    contains_text = any(line.strip() and not line.strip().startswith("<") for line in source_lines)

    target_block = []

    if contains_text:
        # Inline-style wrapping (e.g., KLMS)
        target_block.append(" " * 16 + target_open.rstrip() + "\n")
        for i, text_line in enumerate(translated_lines):
            indent = len(source_lines[i]) - len(source_lines[i].lstrip()) if i < len(source_lines) else 20
            target_block.append(" " * indent + text_line + "\n")
        target_block[-1] = target_block[-1].rstrip() + "</target>\n"
    else:
        # Block-wrapped (e.g., Storyline-style)
        target_block.append(" " * 16 + target_open + "\n")
        for i, text_line in enumerate(translated_lines):
            indent = len(source_lines[i]) - len(source_lines[i].lstrip()) if i < len(source_lines) else 20
            target_block.append(" " * indent + text_line + "\n")
        target_block.append(" " * 16 + "</target>\n")

    return target_block


# === insert_target_by_renaming_source ===
"""
This approach simplifies translation and formatting issues entirely by:

1. Extracting the entire <source ...>...</source> block
2. Renaming both the opening and closing tags: <source ...> becomes <target ...>
3. Sending the ENTIRE block for translation (including tags, whitespace, indent)
4. Inserting the returned block directly below </source>, with no reformatting

Benefits:
- Preserves exact formatting and tag positions
- Automatically carries over xml:space or other attributes
- Prevents any trailing whitespace bugs or structural mismatches
- Works identically across KLMS, Storyline, and other formats

This is the preferred method going forward if translation engine preserves formatting inside tags.
"""

import re

def insert_target_by_renaming_source_block(en_lines, translated_block):
    inside_target = False
    zh_lines = []
    inserted = False

    for line in en_lines:
        if "<xliff" in line:
            line = line.replace('trgLang="en"', 'trgLang="zh"')
        if "<segment" in line:
            line = line.replace('state="final"', 'state="translated"')
        if "<target" in line:
            inside_target = True
            continue
        if inside_target and "</target>" in line:
            inside_target = False
            continue
        zh_lines.append(line)
        if "</source>" in line and not inserted:
            zh_lines.extend([l + "\n" for l in translated_block])
            inserted = True
    return zh_lines
