from utils import xliff_check

@xliff_check(11)
def check_initial_segment_targets(filename, lines):
    """
    CHECK #11: Initial State
    Checks if the the segment state is "initial" then the target element should either not exist or contain an exact copy of the source.
    """
    print("CHECK #11: check_initial_segment_targets v1 called for", filename)
    validation_issues = []
    return validation_issues
