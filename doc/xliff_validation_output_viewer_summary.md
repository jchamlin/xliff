### 🛠 Hand-off Summary to Next Session (XLIFF 2.0 Translation 6)

This document captures important state for continuing this project in a fresh chat.

---

### ✅ Context & Progress Summary

We are validating XLIFF 2.0 files using a strict format-matching pipeline, especially for KLMS.

So far, we’ve fully implemented and tested:

- **CHECK #1:** `check_utf8_bom`
- **CHECK #2:** `check_xml_declaration`

All validations are tested using real and synthetic test files.

---

### 📂 Test Files Used (for CHECK #1 and CHECK #2)

#### ✅ Valid KLMS XLIFF Files (used in both CHECK #1 and CHECK #2)

| Filename                       | Notes            |
| ------------------------------ | ---------------- |
| `klms8-messages(en).xlf`       | Known valid file |
| `klms8-messages(es).xlf`       | Known valid file |
| `klms8-messages(hmn).xlf`      | Known valid file |
| `klms8-messages(ksw-Mymr).xlf` | Known valid file |
| `klms8-messages(so).xlf`       | Known valid file |

#### ❌ Failure Case Files for CHECK #1 (UTF-8 BOM Check)

| Filename               | Contents                           | Expected Result        |
| ---------------------- | ---------------------------------- | ---------------------- |
| `test-no-bom.xml`      | No BOM, but otherwise valid XML    | ❌ Missing BOM          |
| `test-utf16le-bom.xml` | UTF-16 LE BOM, valid XML in UTF-16 | ❌ Invalid BOM encoding |

#### ❌ Failure Case Files for CHECK #2 (XML Declaration Check)

| Filename                       | Contents                                                       | Expected Result                            |
| ------------------------------ | -------------------------------------------------------------- | ------------------------------------------ |
| `test-no-xml-declaration.xml`  | No declaration, starts with `<root>`                           | ❌ Missing declaration                      |
| `test-bad-xml-declaration.xml` | `<?xml version='1.0' encoding='utf-8'?>` (wrong quotes/casing) | ❌ Invalid declaration formatting           |
| `test-empty.xml`               | Empty file (0 bytes)                                           | ❌ Missing declaration (handled as "blank") |

These files were created dynamically using `utf-8-sig` encoding to simulate real-world conditions.

---

### ✅ Pipeline Behavior Implemented

- Fail-fast logic added: returns immediately after the first validation issue.
- BOM check occurs before reading the file.
- Proper exception handling verified.
- `make_validation_issue()` has a clearly defined format.
- Markdown display in ChatGPT was refined:
  - Use `...` **only** for truncation (not by default)
  - Highlight error line text in **code-style blocks**

---

### ⚠️ Known Tooling Defect & Workaround

Canvas → file → canvas syncs are unreliable. Copying the entire canvas to a file (or restoring it from a file) has failed in **3 separate chats**.
Failures include:

- Silent overwrites of the entire file with only partial content
- Invalid Python from broken transfers (missing imports, headers, or trailing code)
- Loss of comments and docstrings

✅ **Workaround in use:**

- Extract and isolate **only the function under test** from canvas.
- Save it into a file named after the function (e.g., `check_utf8_bom.py`).
- Use that file for isolated imports and testing.
- This method has proven 100% reliable.

Also:

- Add version-printing at the top of test functions (e.g. `print("check_utf8_bom v3")`) to confirm which version executes during testing.

---

### 🚀 Next Step Suggestion

Begin implementation of **CHECK #3: `check_namespace_prefixes()`**, continuing to follow:

- Fail-fast logic
- Docstring-style documentation
- Consistent formatting of validation issues

---

(End of hand-off summary)

### 🛑 Validation Issues (check_xml_declaration)

| Validator       | File                         | Line | Cols | Message                                                                     | Unit ID |
| --------------- | ---------------------------- | ---- | ---- | --------------------------------------------------------------------------- | ------- |
| XML Declaration | test-no-xml-declaration.xml  | 1    | 1–1  | Missing XML declaration at the top of file.                                 | —       |
| XML Declaration | test-bad-xml-declaration.xml | 1    | 1–39 | Invalid XML declaration. Expected: `<?xml version="1.0" encoding="UTF-8"?>` | —       |
| XML Declaration | test-empty.xml               | 1    | 1–1  | Missing XML declaration at the top of file.                                 | —       |

---

### 📄 Highlighted Line Snippets

- `test-no-xml-declaration.xml`  
  `<root>`  
  _(Missing declaration entirely — content begins abruptly.)_

- `test-bad-xml-declaration.xml`  
  `<?xml version='1.0' encoding='utf-8'?>` ← ❌ malformed (single quotes, lowercase)

- `test-empty.xml`  
  _(empty line)_ ← ❌ missing declaration completely



### 🧪 Failure Test Case Files

- `test-bad-ns0.xml`  
  Contains prefixed tags like `<ns0:root>` and `<ns0:child>`

- `test-bad-longns.xml`  
  Contains a longer namespace prefix: `<prefixTooLong:element>`

---

### ✅ check_namespace_prefixes() Test Rules

- ✅ **Valid** if the document contains **no element-level namespace prefixes** such as `<ns:tag>` or `</ns:tag>`

- ❌ **Fail** if **any element** is prefixed with a namespace (e.g., `<ns0:child>`) — fails fast after first instance

- ✅ Attributes like `xmlns` or `xmlns:ns0` are **not checked here** — this check focuses only on the **tag prefixing**

- ✅ Reports line, column, and highlights the **namespace prefix only**

- ❌ Fails even if the prefix is valid XML — KLMS does not permit prefixed tags

- ✅ Works for both self-closing and paired tags



### 🧪 Failure Test Case Files for check_xliff_element_attributes()

| Filename                              | Failure Scenario                      |
| ------------------------------------- | ------------------------------------- |
| `test-xliff-missing-tag.xml`          | No `<xliff>` element                  |
| `test-xliff-bad-order.xml`            | Attributes in wrong order             |
| `test-xliff-missing-xmlns.xml`        | Missing `xmlns` attribute             |
| `test-xliff-missing-trgLang.xml`      | Missing `trgLang` attribute           |
| `test-xliff-trgLang-mismatch(es).xlf` | `trgLang` doesn't match filename code |
| `test-xliff-extra-attr.xml`           | Extra attribute `tool="okapi"`        |

### ✅ check_xml_validation() Test Rules

- ✅ Passes if XML parses cleanly with strict lxml settings

- ❌ Fails if any well-formedness error occurs

- ✅ Reports exact error, line, column, and snippet

---

### 🧪 Failure Test Case Files for check_xml_validation()

| Filename             | Failure Scenario            |
| -------------------- | --------------------------- |
| `test-malformed.xml` | Unclosed or mismatched tags |

### ✅ check_xliff_schema() Test Rules

| Filename                     | Scenario                          |
| ---------------------------- | --------------------------------- |
| KLMS files                   | ✅ Should pass if schema compliant |
| `test-invalid-element.xml`   | ❌ Invalid element under segment   |
| `test-invalid-attribute.xml` | ❌ Extra invalid attribute on file |

### ✅ check_duplicate_ids() Test Rules

| Filename                             | Scenario                                     |
| ------------------------------------ | -------------------------------------------- |
| KLMS files (5)                       | ✅ Should pass — all IDs valid and unique     |
| `MCB_ICAPS_L01_Storyline`            | ✅ Should pass — complex real-world test case |
| `test-duplicate-file-id.xml`         | ❌ Duplicate `<file>` ID                      |
| `test-duplicate-unit-id.xml`         | ❌ Duplicate `<unit>` ID                      |
| `test-bad-originalData-sequence.xml` | ❌ Skipped sequence in `<data>` IDs           |
| `test-bad-data-gap.xml`              | ❌ Gap in `<data>` ID sequence                |
| `test-bad-ph-pc-sequence.xml`        | ❌ Invalid mixed `<ph>`/`<pc>` sequence       |
| `test-bad-ph-pc-mixed-order.xml`     | ❌ Out-of-order shared sequence IDs           |

---

### 📄 Failure Test File Definitions

| Filename                             | Scenario                                                            | How It Was Created                                                                   |
| ------------------------------------ | ------------------------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `test-duplicate-file-id.xml`         | ❌ Two `<file>` elements share the same ID                           | Added two `<file id="f1"/>` entries                                                  |
| `test-duplicate-unit-id.xml`         | ❌ Two `<unit>` elements share the same ID within a single `<file>`  | Added two `<unit id="u1">` blocks                                                    |
| `test-bad-originalData-sequence.xml` | ❌ Skipped number in `<data>` ID sequence inside `originalData`      | Used `<data id="note_1"/>` and `<data id="note_3"/>`, skipping `note_2`              |
| `test-bad-data-gap.xml`              | ❌ Gap in `<data>` ID sequence                                       | Included `info_1`, `info_2`, and `info_4` (missing `info_3`)                         |
| `test-bad-ph-pc-sequence.xml`        | ❌ Mixed `<ph>` and `<pc>` tags not in proper sequence               | Created IDs like `ph1`, `pc3`, `pc2`, `ph4` out of order                             |
| `test-bad-ph-pc-mixed-order.xml`     | ❌ Correct prefix but out-of-order numbers between `<ph>` and `<pc>` | Created sequence `ph1`, `ph2`, `pc4`, `ph3`, breaking the shared sequence pattern--- |

### 🧪 Failure Test File Definitions

#### `test-invalid-element.xml`

Created by adding a non-XLIFF element `<invalid>` inside a `<segment>` block. This element is not allowed according to the XLIFF 2.0 schema and causes validation to fail.

#### `test-invalid-attribute.xml`

Created by inserting an invalid attribute `badAttr="oops"` into the `<file>` element. This attribute is not defined in the schema and is therefore rejected during validation.



### ✅ check_duplicate_ids() Test Rules

| Filename                             | Scenario                                     |
| ------------------------------------ | -------------------------------------------- |
| KLMS files (5)                       | ✅ Should pass — all IDs valid and unique     |
| `MCB_ICAPS_L01_Storyline`            | ✅ Should pass — complex real-world test case |
| `test-duplicate-file-id.xml`         | ❌ Duplicate `<file>` ID                      |
| `test-duplicate-unit-id.xml`         | ❌ Duplicate `<unit>` ID                      |
| `test-bad-originalData-sequence.xml` | ❌ Skipped sequence in `<data>` IDs           |
| `test-bad-data-gap.xml`              | ❌ Gap in `<data>` ID sequence                |
| `test-bad-ph-pc-sequence.xml`        | ❌ Invalid mixed `<ph>`/`<pc>` sequence       |
| `test-bad-ph-pc-mixed-order.xml`     | ❌ Out-of-order shared sequence IDs           |

---

### 📄 Failure Test File Definitions

| Filename                             | Scenario                                                            | How It Was Created                                                                |
| ------------------------------------ | ------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| `test-duplicate-file-id.xml`         | ❌ Two `<file>` elements share the same ID                           | Added two `<file id="f1"/>` entries                                               |
| `test-duplicate-unit-id.xml`         | ❌ Two `<unit>` elements share the same ID within a single `<file>`  | Added two `<unit id="u1">` blocks                                                 |
| `test-bad-originalData-sequence.xml` | ❌ Skipped number in `<data>` ID sequence inside `originalData`      | Used `<data id="note_1"/>` and `<data id="note_3"/>`, skipping `note_2`           |
| `test-bad-data-gap.xml`              | ❌ Gap in `<data>` ID sequence                                       | Included `info_1`, `info_2`, and `info_4` (missing `info_3`)                      |
| `test-bad-ph-pc-sequence.xml`        | ❌ Mixed `<ph>` and `<pc>` tags not in proper sequence               | Created IDs like `ph1`, `pc3`, `pc2`, `ph4` out of order                          |
| `test-bad-ph-pc-mixed-order.xml`     | ❌ Correct prefix but out-of-order numbers between `<ph>` and `<pc>` | Created sequence `ph1`, `ph2`, `pc4`, `ph3`, breaking the shared sequence pattern |

### ✅ check_java_placeholders() Test Rules

| Filename                        | Scenario                                                      |
| ------------------------------- | ------------------------------------------------------------- |
| KLMS files (5)                  | ✅ Should pass — all placeholders correctly matched            |
| `test-placeholder-missing.xml`  | ❌ Target is missing a placeholder present in the source       |
| `test-placeholder-mismatch.xml` | ❌ Target has mismatched counts of placeholders (e.g., {1} x2) |

---

### 📄 Failure Test File Definitions

| Filename                        | Scenario                                                    | How It Was Created                                                        |
| ------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------- |
| `test-placeholder-missing.xml`  | ❌ Target is missing `{0}`                                   | Source has "This is step {0}.", target omits placeholder: "This is step." |
| `test-placeholder-mismatch.xml` | ❌ `{0}` and `{1}` used with incorrect frequencies in target | Source has `{0}, {1}, {0}`; target has `{0}, {1}, {1}`                    |

### ✅ check_target_format() Test Rules

| Filename                              | Scenario                                                  |
| ------------------------------------- | --------------------------------------------------------- |
| KLMS files (5)                        | ✅ Should pass — original formatting preserved             |
| `test-format-leading-whitespace.xml`  | ❌ Extra indent on closing tag not matching source         |
| `test-format-trailing-whitespace.xml` | ❌ Trailing space removed/added before line break          |
| `test-format-tag-mismatch.xml`        | ❌ Tag start order misaligned due to altered line wrapping |

---

### 📄 Failure Test File Definitions

| Filename                              | Scenario                                                      | How It Was Created                                                                                            |
| ------------------------------------- | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------- |
| `test-format-leading-whitespace.xml`  | ❌ Source has `</pc>` at start of line, target has it indented | Unit contains a `<pc>` block where source puts `</pc>` at start of line; target has it indented               |
| `test-format-trailing-whitespace.xml` | ❌ Source ends first line with space before newline            | Two-line sentence where first line ends in space and second starts without indent, target alters that spacing |
| `test-format-tag-mismatch.xml`        | ❌ Source and target wrap `<ph>` differently                   | Source wraps `<ph>` onto next line; target keeps tag and content on same line, causing start-tag mismatch     |

## ✅ Check #10 — Test Results (Re-run with Split Conditions)

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
