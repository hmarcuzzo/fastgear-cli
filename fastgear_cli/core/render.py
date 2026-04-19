import subprocess
import sys
from pathlib import Path

import typer
from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_template(
    template_root: Path,
    output_root: Path,
    context: dict,
    conditional_files: dict,
    conditional_dirs: dict,
    *,
    dry_run: bool = False,
) -> list[Path]:
    env = Environment(
        loader=FileSystemLoader(str(template_root)),
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
    )

    rendered_files: list[Path] = []

    for tpl_path in template_root.rglob("*"):
        rel = tpl_path.relative_to(template_root)

        if (
            tpl_path.is_dir()
            or not _should_render_dir(rel, conditional_dirs)
            or not _should_render_file(rel, conditional_files)
        ):
            continue

        rendered_rel = env.from_string(str(rel)).render(**context)
        out_path = output_root / rendered_rel

        if tpl_path.name.endswith(".j2"):
            out_path = out_path.with_suffix("")

        if out_path.exists():
            continue

        rendered_files.append(out_path)

        if dry_run:
            continue

        out_path.parent.mkdir(parents=True, exist_ok=True)

        if tpl_path.name.endswith(".j2"):
            template = env.get_template(str(rel))
            out_path.write_text(template.render(**context), encoding="utf-8")
        else:
            out_path.write_bytes(tpl_path.read_bytes())

    return rendered_files


def run_ruff_format(file_path: Path, project_dir: Path) -> None:
    resolved_file_path = file_path.resolve()

    base_command = [sys.executable, "-m", "ruff"]
    check_command = [*base_command, "check", "--fix", str(resolved_file_path)]
    format_command = [*base_command, "format", str(resolved_file_path)]

    cwd = project_dir.resolve()
    try:
        subprocess.run(
            check_command,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
        subprocess.run(
            format_command,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd,
        )
    except FileNotFoundError:
        typer.secho(
            "ruff not found in the current CLI environment.",
            fg=typer.colors.YELLOW,
        )
    except subprocess.CalledProcessError as error:
        typer.secho(
            f"Failed to apply ruff rules to '{file_path.name}': {error.stderr.strip()}",
            fg=typer.colors.YELLOW,
        )


def _should_render_dir(rel_path: Path, conditional_dirs: dict) -> bool:
    parts = rel_path.parts
    if len(parts) <= 1:
        return True

    dir_parts = parts[1:-1]
    if not dir_parts:
        return True

    for i in range(len(dir_parts)):
        partial_path = "/".join(dir_parts[: i + 1])
        single_part = dir_parts[i]

        if partial_path in conditional_dirs and not conditional_dirs[partial_path]:
            return False
        if (
            single_part in conditional_dirs
            and partial_path not in conditional_dirs
            and not conditional_dirs[single_part]
        ):
            return False

    return True


def _should_render_file(rel_path: Path | str, conditional_files: dict) -> bool:
    rel_path = Path(rel_path)
    if len(rel_path.parts) <= 1:
        file_path = rel_path.as_posix()
        if file_path in conditional_files:
            return conditional_files[file_path]
        return True

    file_path = Path(*rel_path.parts[1:]).as_posix()

    if file_path in conditional_files:
        return conditional_files[file_path]

    return True
