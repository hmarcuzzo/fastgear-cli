from pathlib import Path

import typer


class FileTreeUtils:
    @staticmethod
    def display_dry_run_output(files: list[Path], base_dir: Path) -> None:
        typer.secho("\n🔍 Dry run mode - no files created\n", fg=typer.colors.YELLOW)

        typer.secho("Files that would be created:", fg=typer.colors.CYAN)
        FileTreeUtils.print_file_tree(files, base_dir)
        typer.secho(f"\nTotal: {len(files)} file(s)", fg=typer.colors.CYAN)

    @staticmethod
    def print_file_tree(files: list[Path], base_dir: Path) -> None:
        tree = FileTreeUtils._build_tree(files, base_dir)
        FileTreeUtils._print_tree_recursive(tree)

    @staticmethod
    def _build_tree(files: list[Path], base_dir: Path) -> dict:
        tree: dict = {}

        for file_path in files:
            relative_path = file_path.relative_to(base_dir)
            parts = relative_path.parts
            current = tree
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = None
        return tree

    @staticmethod
    def _print_tree_recursive(tree: dict, prefix: str = "") -> None:
        items = sorted(tree.items(), key=lambda x: (x[1] is None, x[0]))
        for index, (name, subtree) in enumerate(items):
            is_last = index == len(items) - 1
            connector = "└── " if is_last else "├── "
            icon = "📄" if subtree is None else "📁"
            typer.echo(f"{prefix}{connector}{icon} {name}")
            if subtree is not None:
                extension = "    " if is_last else "│   "
                FileTreeUtils._print_tree_recursive(subtree, prefix + extension)
