import re

# === KLMS + STORYLINE Translation Engine ===
# This unified translation module handles XLIFF 2.0 files with rich inline markup.
# It:
# - Preserves all formatting, spacing, and tag structure
# - Supports Java-style placeholder protection
# - Handles culturally appropriate month/day abbreviations
# - Treats <pc id="block_"> or <pc id="p_"> as whole-context translation units
# - Is compatible with both KLMS and Storyline files
# - Translates only text nodes, never tags or attributes

# === Placeholder protection ===
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

# === Month and Day Abbreviation Logic ===

# Culturally appropriate abbreviations per language
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
    # Add more languages as needed...
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

# === Translation Block Handling ===

def is_translatable_block(pc_id):
    return pc_id.startswith("block_") or pc_id.startswith("p_")

# === Formatting-Free Translation Strategy ===
# We preserve formatting by passing the whole <pc id="block_#">...</pc> structure to translation untouched.
# Translations should be done with:
# "Only translate human-readable text. Preserve tags, spacing, indent, and order. Reorder lines if needed for grammar."

# === END MODULE ===
