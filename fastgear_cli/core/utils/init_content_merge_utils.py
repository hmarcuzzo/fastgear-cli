import re


def convert_lines_to_content(lines: list[str]) -> str:
    if not lines:
        return ""
    return f"{'\n'.join(lines).rstrip()}\n"


def ensure_import_line(lines: list[str], import_line: str) -> list[str]:
    if import_line in lines:
        return lines

    insert_idx = 0
    while insert_idx < len(lines) and (
        lines[insert_idx].startswith("from ")
        or lines[insert_idx].startswith("import ")
        or not lines[insert_idx].strip()
    ):
        insert_idx += 1

    lines.insert(insert_idx, import_line)
    if insert_idx > 0 and lines[insert_idx - 1].strip():
        lines.insert(insert_idx, "")

    return lines


def merge_required_line(
    *,
    current: str,
    required_line: str,
    anchor_line: str | None = None,
) -> str:
    lines = current.splitlines()
    if required_line in lines:
        return current

    if required_line.startswith(("from ", "import ")):
        lines = ensure_import_line(lines, required_line)
        return convert_lines_to_content(lines)

    if anchor_line and anchor_line in lines:
        anchor_index = lines.index(anchor_line)
        lines.insert(anchor_index + 1, required_line)
    else:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(required_line)

    return convert_lines_to_content(lines)


def merge_symbol_list_assignment(
    *,
    current: str,
    list_name: str,
    symbol_name: str,
) -> str:
    assignment_pattern = re.compile(
        rf"{re.escape(list_name)}\s*=\s*\[(.*?)]",
        re.DOTALL,
    )
    assignment_match = assignment_pattern.search(current)

    if assignment_match:
        raw_values = assignment_match.group(1)
        symbols = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw_values)
        if symbol_name not in symbols:
            symbols.append(symbol_name)

        merged_assignment = f"{list_name} = [{', '.join(symbols)}]"
        merged = (
            f"{current[: assignment_match.start()]}"
            f"{merged_assignment}"
            f"{current[assignment_match.end() :]}"
        )
        return convert_lines_to_content(merged.splitlines())

    return merge_required_line(
        current=current,
        required_line=f"{list_name} = [{symbol_name}]",
    )


def parse_symbol_list_assignment(line: str) -> tuple[str, list[str]] | None:
    assignment_match = re.fullmatch(r"([A-Za-z_][A-Za-z0-9_]*)\s*=\s*\[(.*)]", line)
    if not assignment_match:
        return None

    list_name = assignment_match.group(1)
    raw_values = assignment_match.group(2)
    symbols = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw_values)
    return list_name, symbols
