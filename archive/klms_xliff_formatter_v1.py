"""
KLMS / Storyline XLIFF Formatter v1.0
=====================================

This script is designed to reconstruct <target> blocks for XLIFF 2.0 files,
specifically formatted for use with tools like Articulate Storyline.

GOAL: Ensure all formatting, spacing, indentation, and tag structure match
the original <source> block EXACTLY — only the translated inner text should differ.

---------------------------------------------------
RULES FOR STORYLINE-FORMATTED <pc> AND <ph> BLOCKS
---------------------------------------------------

1️⃣ Whitespace Preservation:
    - All leading spaces, tabs, and newlines must be preserved exactly.
    - Every line in <target> should match its counterpart in <source>.

2️⃣ Inline Text Handling:
    - If a <pc> tag contains direct translatable text (e.g., span_2):
        - The <pc> closing tag MUST be on a new line
        - It MUST be flush-left (no indent), e.g.:
              <pc dataRefStart="span_2" id="span_2">你好
</pc>

3️⃣ Structural Containers (e.g., block_0):
    - <pc> tags that contain only <ph> or other <pc> tags can be indented normally.
    - Their closing </pc> tag may be indented to match the opening tag.

4️⃣ Do not modify <ph> or <pc> tag attributes.
    - All ID values, dataRefStart/dataRefEnd/dataRef, and ordering must be preserved.

5️⃣ Placeholder Tokens:
    - If you encounter placeholders like {0}, {1}, etc., replace them:
        {0} -> 0000
        {1} -> 1111
        ... and so on before translation.
    - Reverse this after translation.

6️⃣ <target> formatting:
    - Start with same indentation as <source>
    - End with </target> on the same line as the final translatable <pc> element
    - Inner content of <target> should NOT be indented unless the original was

This script processes a line-by-line clone of the original <source> block,
replacing only the text inside <pc> tags that directly hold visible content.

"""

import re

# Define known inline content IDs (these are the ones where formatting must be exact)
INLINE_TEXT_IDS = {"span_2", "span_5", "span_8", "span_11", "span_14", "span_17", "span_18", "span_19"}

def format_translated_target(source_lines, translated_segments, inline_ids=INLINE_TEXT_IDS):
    translated_lines = []
    translated_iter = iter(translated_segments)

    for line in source_lines:
        content_match = re.search(r'(<pc [^>]+>)(.*?)(</pc>)', line)
        if content_match:
            start_tag, _, end_tag = content_match.groups()
            data_ref_match = re.search(r'dataRefStart="([^"]+)"', start_tag)
            data_ref_id = data_ref_match.group(1) if data_ref_match else ""
            indent = line[:line.find("<")]
            translated_text = next(translated_iter)

            if data_ref_id in inline_ids:
                # Inline content: flush-left closing </pc> on new line
                translated_lines.append(f'{indent}{start_tag}{translated_text}')
                translated_lines.append(f'</pc>')
            else:
                # Structural or pretty-safe
                translated_lines.append(f'{indent}{start_tag}{translated_text}{end_tag}')
        else:
            translated_lines.append(line)

    return translated_lines
