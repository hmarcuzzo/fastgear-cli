class FastgearCliError(Exception):
    """Base exception for domain errors handled by CLI commands."""


class InvalidInputError(FastgearCliError):
    """Raised when user input is invalid for the requested operation."""


class TemplateConflictError(FastgearCliError):
    """Raised when template generation cannot create any new file."""
