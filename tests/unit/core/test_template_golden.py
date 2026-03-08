from hashlib import sha256
from pathlib import Path

import pytest

from fastgear_cli.core.filesystem import create_template
from fastgear_cli.core.models import ProjectInitConfig

GOLDEN_DIR = Path(__file__).resolve().parents[2] / "fixtures" / "core" / "golden"


def _snapshot_tree(files: list[Path], base_dir: Path) -> str:
    return "\n".join(sorted(file.relative_to(base_dir).as_posix() for file in files)) + "\n"


def _snapshot_with_hashes(files: list[Path], base_dir: Path) -> str:
    lines = []
    for file_path in sorted(files, key=lambda path: path.relative_to(base_dir).as_posix()):
        relative_path = file_path.relative_to(base_dir).as_posix()
        digest = sha256(file_path.read_bytes(), usedforsecurity=False).hexdigest()[:16]
        lines.append(f"{relative_path} {digest}")
    return "\n".join(lines) + "\n"


@pytest.mark.describe("🧪  TemplateGolden")
class TestTemplateGolden:
    @pytest.mark.it("✅  Should keep add/entity/folder template snapshot stable")
    def test_add_entity_folder_template_snapshot(self, tmp_path: Path):
        files = create_template(
            "add/entity/folder",
            tmp_path,
            {"element_name": "billing", "element_class_name": "Billing"},
        )

        snapshot = _snapshot_with_hashes(files, tmp_path)
        expected = (GOLDEN_DIR / "add_entity_folder.snapshot").read_text(encoding="utf-8")
        assert snapshot == expected

    @pytest.mark.it("✅  Should keep new_project minimal tree snapshot stable")
    def test_new_project_minimal_tree_snapshot(self, tmp_path: Path):
        config = ProjectInitConfig(
            base_dir=tmp_path,
            project_name="sample_api",
            project_title="Sample Api",
            use_docker=False,
            agent_tools=[],
            ci_provider=None,
            use_database=False,
            database_provider=None,
        )

        files = create_template(
            "new_project",
            config.base_dir,
            config.context,
            config.conditional_files,
            config.conditional_dirs,
        )

        snapshot = _snapshot_tree(files, tmp_path)
        expected = (GOLDEN_DIR / "new_project_minimal.tree").read_text(encoding="utf-8")
        assert snapshot == expected
