import re
from utils import compare_format_lines
from utils import xliff_check

@xliff_check(9)
def check_target_format(filename, lines):
    """
    CHECK #9: Target Format
    Check each target block against its source to ensure the formatting and first tag on each line is the same as the source.
    For each unit in the file, make a list of lines of the source block, and a list of lines of the target block,
    and then call a utility function to a basic compare of those two lists. The target should have the same number of lines as the source, 
    each line of the target should have: the same leading whitespace as the matching source line, the same trailing whitespace as the matching source line, 
    and start with the same tag as the source line does.
    There are two exceptions: on any line if you detect the starting tags are "<source" and "<target", or "</source" and "</target", 
    which will happen when comparing a source block to a target block, consider those equivalent and don't create a validation issue.
    """
    print("CHECK #9: check_target_format v6 called for", filename)

    validation_issues = []
    unit_id = None
    in_source = False
    in_target = False
    source_lines = []
    target_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        if '<unit' in stripped:
            match = re.search(r'id=["\'](.*?)["\']', stripped)
            unit_id = match.group(1) if match else None

        if '<source' in stripped:
            in_source = True
            source_lines = []
        if in_source:
            source_lines.append(line)
        if '</source' in stripped:
            in_source = False

        if '<target' in stripped:
            in_target = True
            target_lines = []
        if in_target:
            target_lines.append(line)
        if '</target' in stripped:
            in_target = False
            validation_issues.extend(
                compare_format_lines(source_lines, target_lines, filename, unit_id, i + 1, "Target Format")
            )

    return validation_issues
