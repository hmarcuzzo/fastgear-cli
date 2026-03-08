import re
from pathlib import Path

from fastgear_cli.core.render import run_ruff_format


def update_module_init(
    *,
    base_dir: Path,
    module_dir: str,
    module_name: str,
    symbol_name: str,
    source_suffix: str,
    dry_run: bool,
) -> Path | None:
    init_path = base_dir / module_dir / "__init__.py"
    import_line = f"from .{module_name}_{source_suffix} import {symbol_name}"

    if not init_path.exists():
        content = f'{import_line}\n\n__all__ = ["{symbol_name}"]\n'
    else:
        current = init_path.read_text(encoding="utf-8")
        content = merge_module_init_content(current, import_line, symbol_name)
        if content == current:
            return None

    if dry_run:
        return init_path

    init_path.parent.mkdir(parents=True, exist_ok=True)
    init_path.write_text(content, encoding="utf-8")
    run_ruff_format(init_path, base_dir)
    return init_path


def merge_module_init_content(
    current: str,
    import_line: str,
    symbol_name: str,
) -> str:
    lines = current.splitlines()
    if import_line not in lines:
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

    merged = "\n".join(lines).rstrip("\n")
    all_match = re.search(r"__all__\s*=\s*\[(.*?)\]", merged, re.DOTALL)

    if all_match:
        raw_items = all_match.group(1)
        values = re.findall(r"""["']([^"']+)["']""", raw_items)
        if not values:
            values = re.findall(r"[A-Za-z_][A-Za-z0-9_]*", raw_items)
        if symbol_name not in values:
            values.append(symbol_name)
        quoted_values = ", ".join(f'"{item}"' for item in values)
        all_value = f"__all__ = [{quoted_values}]"
        merged = f"{merged[: all_match.start()]}{all_value}{merged[all_match.end() :]}"
    else:
        if merged and not merged.endswith("\n\n"):
            merged = f"{merged}\n\n"
        merged = f'{merged}__all__ = ["{symbol_name}"]'

    return f"{merged.rstrip()}\n"
