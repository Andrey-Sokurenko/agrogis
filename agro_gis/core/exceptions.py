class EncodingDetectionError(Exception):
    """Raised when automatic encoding detection fails."""


class WindowsRegistryFileError(ValueError):
    """Raised when a .reg file is a Windows Registry export."""


class ParseError(Exception):
    """Raised when no parsing strategy succeeds."""


class EmptyDataError(ValueError):
    """Raised when no valid rows were parsed from a data file."""
