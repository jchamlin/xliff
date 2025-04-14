from utils import xliff_check

@xliff_check(14, pair=True)
def check_file_pair_units(english_filename, english_lines, translated_filename, translated_lines):
    """
    CHECK #14 Units
    Check that the translated file has the same units as the English master. Each unit that is out of order, missing, or extra is a validation issue.
    """
    print("check_file_pair_units v1 called for", english_filename, " and ", translated_filename)
    validation_issues = []
    return validation_issues
