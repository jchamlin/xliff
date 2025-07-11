✅ Check #7 — check_duplicate_ids Test on MCB_ICAPS_L01_Storyline(en).xlf`



### 🖨️ Test Output

```
CHECK #7: check_duplicate_ids v10 called for /mnt/data/test-files/MCB_OTPS_L01_Storyline(en).xlfTraceback (most recent call last):  File "<string>", line 14, in check_duplicate_ids  File "src/lxml/etree.pyx", line 3306, in lxml.etree.fromstring  File "src/lxml/parser.pxi", line 1990, in lxml.etree._parseMemoryDocumentValueError: Unicode strings with encoding declaration are not supported. Please use bytes input or XML fragments without declaration.During handling of the above exception, another exception occurred:Traceback (most recent call last):  File "<cell>", line 12, in <cell>    results = validate_xliff_file("/mnt/data/test-files/MCB_OTPS_L01_Storyline(en).xlf")  File "/mnt/data/src/xliff_validator.py", line 58, in validate_xliff_file    issues = check(filename, lines)  File "<string>", line 126, in check_duplicate_idsTypeError: ValidationIssue.__init__() missing 5 required positional arguments: 'line', 'column_start', 'column_end', 'unit_id', and 'text'
```

---

### 🧪 Test Results Table

| File                            | Issues Found | First Few Issues (preview)                                                                                                                                                                                                           |
| ------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| klms8-messages(en).xlf          | 0            | []                                                                                                                                                                                                                                   |
| klms8-messages(es).xlf          | 0            | []                                                                                                                                                                                                                                   |
| klms8-messages(hmn).xlf         | 0            | []                                                                                                                                                                                                                                   |
| klms8-messages(ksw-Mymr).xlf    | 0            | []                                                                                                                                                                                                                                   |
| klms8-messages(so).xlf          | 0            | []                                                                                                                                                                                                                                   |
| MCB_ICAPS_L01_Storyline(en).xlf | 0            | []                                                                                                                                                                                                                                   |
| test-missing-target.xlf         | 1            | [{'validator': 'Untranslated Targets', 'message': 'Target is missing', 'filename': 'test-missing-target.xlf', 'line': 6, 'column_start': 1, 'column_end': 1, 'unit_id': 'u1', 'text': ''}]                                           |
| test-empty-target.xlf           | 1            | [{'validator': 'Untranslated Targets', 'message': 'Target is empty', 'filename': 'test-empty-target.xlf', 'line': 6, 'column_start': 1, 'column_end': 1, 'unit_id': 'u2', 'text': ''}]                                               |
| test-identical-target.xlf       | 1            | [{'validator': 'Untranslated Targets', 'message': 'Target is identical to source', 'filename': 'test-identical-target.xlf', 'line': 6, 'column_start': 1, 'column_end': 1, 'unit_id': 'u3', 'text': 'Test'}]                         |
| test-ends-with-source.xlf       | 1            | [{'validator': 'Untranslated Targets', 'message': 'Target contains unmodified source text', 'filename': 'test-ends-with-source.xlf', 'line': 6, 'column_start': 1, 'column_end': 1, 'unit_id': 'u4', 'text': '[ZH]Test'}]            |
| test-contains-source.xlf        | 1            | [{'validator': 'Untranslated Targets', 'message': 'Target contains unmodified source text', 'filename': 'test-contains-source.xlf', 'line': 6, 'column_start': 1, 'column_end': 1, 'unit_id': 'u5', 'text': '[Pending] ***Test***'}] |

---

### 📊 Validation Issues Table

| Validator            | Message                                | File                      | Line | Col Start | Col End | Unit ID | Text                 |
| -------------------- | -------------------------------------- | ------------------------- | ---- | --------- | ------- | ------- | -------------------- |
| Untranslated Targets | Target is missing                      | test-missing-target.xlf   | 6    | 1         | 1       | u1      |                      |
| Untranslated Targets | Target is empty                        | test-empty-target.xlf     | 6    | 1         | 1       | u2      |                      |
| Untranslated Targets | Target is identical to source          | test-identical-target.xlf | 6    | 1         | 1       | u3      | Test                 |
| Untranslated Targets | Target contains unmodified source text | test-ends-with-source.xlf | 6    | 1         | 1       | u4      | [ZH]Test             |
| Untranslated Targets | Target contains unmodified source text | test-contains-source.xlf  | 6    | 1         | 1       | u5      | [Pending] ***Test*** |

---

### 📄 Highlighted Line Snippets

- `test-missing-target.xlf`  
  *(Missing* `*<target>*` *block entirely — only* `*<source>*` *is present.)*

- `test-empty-target.xlf`  
  `<target state="translated"></target>` ← ❌ empty target

- `test-identical-target.xlf`  
  `<target state="translated">Test</target>` ← ❌ identical to source

- `test-ends-with-source.xlf`  
  `<target state="translated">[ZH]Test</target>` ← ❌ ends with source

- `test-contains-source.xlf`  
  `<target state="translated">[Pending] ***Test***</target>` ← ❌ contains source

---

### 🧪 Test Rules for `check_untranslated_targets()`

These files should all be valid XLIFF 2.0 with:

- A `trgLang` different from `srcLang`

- At least one `<segment state="translated">` element

Success files:

- All five `klms8-messages(...)` XLIFF files

- `MCB_ICAPS_L01_Storyline(en).xlf`

Failure conditions tested:

- Missing `<target>` block

- Empty `<target>` content

- Identical target and source text

- Target containing source as suffix or substring

---

### 📂 Failure Test File Definitions

| File                        | Description                                               |
| --------------------------- | --------------------------------------------------------- |
| `test-missing-target.xlf`   | Segment is missing the `<target>` block entirely          |
| `test-empty-target.xlf`     | Segment has `<target state="translated"></target>`        |
| `test-identical-target.xlf` | Target text is exactly the same as the source             |
| `test-ends-with-source.xlf` | Target includes source as a substring (e.g., `[ZH]Test`)  |
| `test-contains-source.xlf`  | Target includes source in the middle (e.g., `***Test***`) |
