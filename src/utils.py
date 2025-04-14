import os
import re

class Config:
    # Private variable to hold the test files path
    _TEST_FILES_PATH = "/mnt/data/test-files/" if os.path.exists("/mnt/data/") else "../test-files/"
    
    @classmethod
    @property
    def TEST_FILES_PATH(cls):
        """
        Returns the path for the test files. It defaults to '/mnt/data/test-files/' in the ChatGPT runtime environment;
        otherwise, it falls back to '../test-files/' for running in the user's local environment.
        """
        return cls._TEST_FILES_PATH

class ValidationIssue:
    def __init__(self, validator, message, filename, line, column_start, column_end, unit_id, text):
        self.validator = validator
        self.message = message
        self.filename = filename
        self.line = line
        self.column_start = column_start
        self.column_end = column_end
        self.unit_id = unit_id
        self.text = text

    def __repr__(self):
        return (f"ValidationIssue(validator={self.validator}, message={self.message}, "
                f"filename={self.filename}, line={self.line}, column_start={self.column_start}, "
                f"column_end={self.column_end}, unit_id={self.unit_id}, text={self.text})")

    def to_dict(self):
        """
        Converts the ValidationIssue to a dictionary for easier manipulation or logging.
        """
        return {
            'validator': self.validator,
            'message': self.message,
            'filename': self.filename,
            'line': self.line,
            'column_start': self.column_start,
            'column_end': self.column_end,
            'unit_id': self.unit_id,
            'text': self.text
        }

    def format_for_display(self):
        return (
            f"[{self.validator}] {self.message} "
            f"(unit={self.unit_id}, line={self.line}, col={self.column_start}-{self.column_end})"
        )

    @classmethod
    def table_header(cls):
        return (
            "-" * 161 + "\n"
            "| Validator        | Message                                      | File                          | Line #| Column #s| Unit ID     | Problem Text               |\n"
            "|------------------|----------------------------------------------|-------------------------------|-------|----------|-------------|----------------------------|"
        )
    
    @classmethod
    def table_footer(cls):
        return "-" * 161 + "\n"
    
    def format_as_table_row(self):
        return (
            f"| {self.validator:<16.16} | "
            f"{self.message:<44.44} | "
            f"{self.filename:<29.29} | "
            f"{self.line:<5} | "
            f"{self.column_start}–{self.column_end:<6} | "
            f"{str(self.unit_id):<11.11} | "
            f"{self.text:<26.26} |"
        )

def xliff_check(number: int, pair: bool = False):
    """
    Decorator for XLIFF validator check functions.

    Args:
        number (int): The numeric order in which this check should run.
                      Lower numbers run earlier in the pipeline.
        pair (bool): Set to True if the check compares two files (source + target),
                     otherwise defaults to False for single-file checks.

    Returns:
        function: The original function, with metadata attributes:
                  _check_number and _check_pair attached for dynamic discovery.

    Example:
        @xliff_check(7)
        def check_duplicate_ids(filename, lines):
            ...

        @xliff_check(15, pair=True)
        def check_tag_consistency(src_file, src_lines, tgt_file, tgt_lines):
            ...
    """    
    def decorator(func):
        func._check_number = number
        func._check_pair = pair
        return func
    return decorator

def read_file_lines(filepath):
    """
    Reads a file in UTF-8 encoding and returns its contents as a list of lines.

    Args:
        filepath (str): Full path to the file.

    Returns:
        list[str]: Lines of text from the file.

    Raises:
        UnicodeDecodeError: If the file is not UTF-8 encoded.
    """
    with open(filepath, encoding="utf-8-sig") as f:
        return f.readlines()

def compare_format_lines(source_lines, target_lines, filename, unit_id, base_line_number, validator_name):
    """
    Compare two aligned lists of lines (source and target) for format consistency.

    This function checks:
    - That the line counts match
    - That leading and trailing whitespace on each line match
    - That the starting XML tag on each line matches, with allowance for <source>/<target> and </source>/</target> equivalency

    Parameters:
        source_lines (list of str): Lines from the source block.
        target_lines (list of str): Lines from the target block.
        filename (str): The name of the file being validated.
        unit_id (str): The unit ID associated with the block.
        base_line_number (int): Line number used in reporting issues.
        validator_name (str): The name of the validation check.

    Returns:
        list: A list of ValidationIssue (possibly empty).
    """
    issues = []

    if len(source_lines) != len(target_lines):
        issues.append(ValidationIssue(
            validator=validator_name,
            message=f"Mismatch in line count: source={len(source_lines)} lines, target={len(target_lines)} lines.",
            filename=filename,
            line=base_line_number,
            column_start=1,
            column_end=1,
            unit_id=unit_id,
            text=""
        ))
        return issues

    for j in range(len(source_lines)):
        src_line = source_lines[j]
        tgt_line = target_lines[j]

        src_strip = src_line.strip()
        tgt_strip = tgt_line.strip()

        src_leading = re.match(r"^\s*", src_line).group()
        tgt_leading = re.match(r"^\s*", tgt_line).group()
        src_trailing = re.search(r"\s*$", src_line).group()
        tgt_trailing = re.search(r"\s*$", tgt_line).group()

        if src_leading != tgt_leading or src_trailing != tgt_trailing:
            issues.append(ValidationIssue(
                validator=validator_name,
                message=f"Line {j+1} has different whitespace formatting in target.",
                filename=filename,
                line=base_line_number,
                column_start=1,
                column_end=1,
                unit_id=unit_id,
                text=tgt_line.strip()
            ))
            continue

        src_tag = re.match(r"<\/?\w+", src_strip)
        tgt_tag = re.match(r"<\/?\w+", tgt_strip)

        if src_tag and tgt_tag:
            src_val = src_tag.group()
            tgt_val = tgt_tag.group()
            if not ((src_val == "<source" and tgt_val == "<target") or
                    (src_val == "</source" and tgt_val == "</target") or
                    (src_val == tgt_val)):
                issues.append(ValidationIssue(
                    validator=validator_name,
                    message=f"Line {j+1} starts with different tag: source='{src_val}', target='{tgt_val}'",
                    filename=filename,
                    line=base_line_number,
                    column_start=1,
                    column_end=1,
                    unit_id=unit_id,
                    text=tgt_line.strip()
                ))

    return issues
