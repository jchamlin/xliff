from .check_utf8_bom import check_utf8_bom
from .check_xml_declaration import check_xml_declaration
from .check_namespace_prefixes import check_namespace_prefixes
from .check_xliff_element_attributes import check_xliff_element_attributes
from .check_xml_validation import check_xml_validation
from .check_xliff_schema import check_xliff_schema
from .check_duplicate_ids import check_duplicate_ids
from .check_java_placeholders import check_java_placeholders
from .check_target_format import check_target_format
from .check_untranslated_targets import check_untranslated_targets
from .check_initial_segment_targets import check_initial_segment_targets
from .check_xliff_placeholders import check_xliff_placeholders
from .check_file_pair_formatting import check_file_pair_formatting
from .check_file_pair_units import check_file_pair_units
from .check_file_pair_structure import check_file_pair_structure

# Automatically populate __all__ by filtering for all check functions
check_functions = [obj for name, obj in globals().items() 
                   if callable(obj) and name.startswith("check_")]

# Populate __all__ dynamically
__all__ = [func.__name__ for func in check_functions]

# Optionally, keep the same sorting if you need to maintain order
check_functions.sort(key=lambda f: f.__name__)  # Or sort by _check_number if applicable

ALL_SINGLE_FILE_CHECKS = []
ALL_FILE_PAIR_CHECKS = []

# Automatically collect and order check functions based on @xliff_check decorator metadata
for check in check_functions:
    if hasattr(check, "_check_pair") and check._check_pair:
        ALL_FILE_PAIR_CHECKS.append(check)
    else:
        ALL_SINGLE_FILE_CHECKS.append(check)

ALL_SINGLE_FILE_CHECKS.sort(key=lambda f: f._check_number)
ALL_FILE_PAIR_CHECKS.sort(key=lambda f: f._check_number)