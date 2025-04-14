# Manual handling of XLIFF file, translation with placeholder replacement
manual_lines = []
current_uid = None
in_target_block = False

for i, line in enumerate(en_lines):
    stripped = line.strip()

    if "<unit" in line and 'id="' in line:
        match = re.search(r'id="([^"]+)"', line)
        current_uid = match.group(1) if match else None

    if "<target" in stripped and current_uid:
        indent = " " * (len(line) - len(line.lstrip()))
        
        # Extract and handle <source> elements with <pc> and <ph> tags
        source_line = next((l for l in en_lines[i-3:i] if "<source" in l), "").strip()
        match = re.search(r"<source[^>]*>(.*?)</source>", source_line)
        source_text = match.group(1) if match else ""

        # Replace placeholders with actual content from originalData
        translated_content = source_text

        # Handle <pc> and <ph> replacements correctly
        pc_matches = re.findall(r'<pc[^>]*dataRefStart="([^"]+)"[^>]*dataRefEnd="([^"]+)"[^>]*>(.*?)</pc>', source_text)
        for match in pc_matches:
            data_ref_start, data_ref_end, pc_content = match
            data_start = next((d for d in original_data if d['id'] == data_ref_start), {}).get('content', '')
            data_end = next((d for d in original_data if d['id'] == data_ref_end), {}).get('content', '')
            translated_content = translated_content.replace(pc_content, f"<pc>{data_start}{pc_content}{data_end}</pc>")

        ph_matches = re.findall(r'<ph[^>]*dataRef="([^"]+)"[^>]*>(.*?)</ph>', source_text)
        for match in ph_matches:
            data_ref, ph_content = match
            data_content = next((d for d in original_data if d['id'] == data_ref), {}).get('content', '')
            translated_content = translated_content.replace(ph_content, f"<ph>{data_content}</ph>")

        # Write the final translated content to <target>
        manual_lines.append(f'{indent}<target trgLang="zh" state="translated" xml:space="preserve">{translated_content}</target>
')
        continue

    # Set state to "initial" for untranslated or empty <target> content
    if 'state="final"' in line and current_uid:
        state = "translated" if current_uid in subset_ids else "initial"
        line = line.replace('state="final"', f'state="{state}"')

    manual_lines.append(line)

# Write the final reconstructed file
if manual_lines[0].strip().startswith("<?xml"):
    manual_lines[0] = '<?xml version="1.0" encoding="UTF-8"?>
'

with open(final_path, "w", encoding="utf-8-sig" if english_has_bom else "utf-8") as f:
    f.writelines(manual_lines)
