from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def render_template_dir(
    template_root: Path, output_root: Path, context: dict, conditional_files: dict
) -> None:
    env = Environment(
        loader=FileSystemLoader(str(template_root)),
        autoescape=select_autoescape(enabled_extensions=()),
        keep_trailing_newline=True,
    )

    for tpl_path in template_root.rglob("*"):
        rel = tpl_path.relative_to(template_root)

        # jump directories
        if tpl_path.is_dir():
            continue

        if not _should_render_file(tpl_path.name, context, conditional_files):
            continue

        # render template
        rendered_rel = env.from_string(str(rel)).render(**context)
        out_path = output_root / rendered_rel

        out_path.parent.mkdir(parents=True, exist_ok=True)

        if tpl_path.name.endswith(".j2"):
            template = env.get_template(str(rel))
            out_path = out_path.with_suffix("")  # remove .j2
            out_path.write_text(template.render(**context), encoding="utf-8")
        else:
            out_path.write_bytes(tpl_path.read_bytes())


def _should_render_file(file_name: str, context: dict, conditional_files: dict) -> bool:
    condition_key = conditional_files.get(file_name)
    if condition_key is None:
        return True
    return bool(context.get(condition_key))
