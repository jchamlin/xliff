from utils import xliff_check

@xliff_check(15, pair=True)
def check_file_pair_structure(english_filename, english_lines, translated_filename, translated_lines):
    """
    CHECK #15: XML Structure
    Ensure that both files contain the exact same XML structure, matching tags, ordering, nesting, etc.
    The easiest method may be to parse both files into an XML DOM and walk both trees in parallel comparing.
    - Element nodes (name, attributes, attribute values) should always match with the exceptions noted below.
    - Text nodes must match unless inside of a target element. When inside of a target element, no text node comparison is needed
    The exceptions:
    1. the trgLang attribute on the xliff element
    2. the value of the state attribute on a segment element
    3. the text nodes inside of a value element
    """
    print("check_file_pair_structure v1 called for", english_filename, " and ", translated_filename)
    validation_issues = []
    return validation_issues
