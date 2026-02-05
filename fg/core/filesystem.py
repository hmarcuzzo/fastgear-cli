from pathlib import Path


def create_project_structure(project_dir: Path) -> None:
    src_dir = project_dir / "src"
    main_file = src_dir / "main.py"

    project_dir.mkdir(exist_ok=False)
    src_dir.mkdir()
    main_file.touch()
