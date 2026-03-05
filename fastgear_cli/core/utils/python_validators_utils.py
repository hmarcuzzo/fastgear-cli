import re


def is_valid_python_path(path: str) -> bool:
    return all(is_valid_python_identifier(part) for part in path.split("."))


def is_valid_python_identifier(value: str) -> bool:
    return re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", value) is not None
