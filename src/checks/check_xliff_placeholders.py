from utils import xliff_check

@xliff_check(12)
def check_xliff_placeholders(filename, lines):
    """
    CHECK #12: XLIFF Placeholders
    If a unit has an originalData element, then it uses XLIFF placeholders. These are pc and ph tags and they are used to escape 
    makup (tags) so they do not get mangled during human or machine translation.

    pc tag: is meant to enclose something with a <pc>asdfasdF</pc> but can be empty or even self-closed.
    has a dataRefStart attribute which references a data element in the originalData element by id
    has an optional dataRefEnd attribute which references a data element in the originalData element by id
    The values of those data elements are the replacement values, the start pc tag is replaced by the value pointed 
    to by dataRefStart, and the matching closing </pc> tag (careful, pc blocks can be nested) is replaced by the 
    value in the data node with an id that matches the dataRefEnd.

    ph tag: has a dataRef attribute which references a data element in the originalData element by id. The data element's value
    represents what the <ph/> tag is repalced by.

    This checks that the data element referenced by every dataRefStart, dataRefEnd, and dataRef exists.
    It also checks to make sure every data element is referenced, and there are no unreferenced data elements.

    If value of the source or target is HTML, then the pc tags represnt closeable elements like p, span, em, b, strong, etc 
    and the ph tags represent self-closing elements like br, hr, img, etc.

    If the data elements don't look like HTML tags, then the value is an Articulate Storyline or other type, and the tags represent 
    something proprietary. Like with Storyline, it uses <Style> tags.

    The actual value should be reconstructed using this process and validated.

    If value is HTML (because the data elements had values that look like HTML tags) then the HTML fragment should be 
    validated with an HTML 5 validator in its most strict mode (enabling all warnings).

    Otherwise the value should be considered XML and an XML validator should be run on the XML fragment (enclosing it with a <root></root> first) 
    in its most strict mode (enabling all warnings).

    Each error or warning raised by the HTML or XML validator should generate a validation issue.
    """
    print("CHECK #12: check_xliff_placeholders v1 called for", filename)
    validation_issues = []
    return validation_issues
