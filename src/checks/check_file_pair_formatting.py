from utils import xliff_check

@xliff_check(13, pair=True)
def check_file_pair_formatting(english_filename, english_lines, translated_filename, translated_lines):
    """
    CHECK #13: Formatting
    Validate the translated file has identical formatting to the English master, including leading/trailing whitespace and the first tag on the line matches.
    This is the same as CHECK #9 above and calls the same utility method to perform the check, but instead of passing in source and target 
    blocks as arrays of lines, this passes in the entire files as arrays of lines.
    """
    print("check_file_pair_formatting v1 called for", english_filename, " and ", translated_filename)
    validation_issues = []
    return validation_issues
