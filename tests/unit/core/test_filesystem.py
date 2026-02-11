from pathlib import Path
from unittest.mock import MagicMock

import pytest

from fastgear_cli.core.filesystem import create_project

pytest_plugins = ["tests.fixtures.core.filesystem_fixtures"]


@pytest.mark.describe("🧪  CreateProject")
class TestCreateProject:
    @pytest.mark.it("✅  Should call render_template_dir with correct arguments")
    def test_calls_render_template_dir_with_correct_args(
        self,
        mocker: MagicMock,
        output_directory: Path,
        sample_context: dict,
    ):
        mock_render = mocker.patch("fastgear_cli.core.filesystem.render_template_dir")
        mock_root_dir = mocker.patch("fastgear_cli.core.filesystem.ROOT_DIR")
        mock_root_dir.__truediv__ = MagicMock(
            return_value=MagicMock(
                __truediv__=MagicMock(return_value=Path("/mock/templates/new_project"))
            )
        )

        create_project("new_project", output_directory, sample_context)

        mock_render.assert_called_once()
        call_args = mock_render.call_args
        assert call_args[0][1] == output_directory
        assert call_args[0][2] == sample_context

    @pytest.mark.it("✅  Should pass empty dicts when conditionals are None")
    def test_passes_empty_dicts_when_conditionals_none(
        self,
        mocker: MagicMock,
        output_directory: Path,
        sample_context: dict,
    ):
        mock_render = mocker.patch("fastgear_cli.core.filesystem.render_template_dir")
        mocker.patch("fastgear_cli.core.filesystem.ROOT_DIR", Path("/mock"))

        create_project("new_project", output_directory, sample_context)

        call_args = mock_render.call_args
        assert call_args[0][3] == {}
        assert call_args[0][4] == {}

    @pytest.mark.it("✅  Should pass conditional_files when provided")
    def test_passes_conditional_files_when_provided(
        self,
        mocker: MagicMock,
        output_directory: Path,
        sample_context: dict,
    ):
        mock_render = mocker.patch("fastgear_cli.core.filesystem.render_template_dir")
        mocker.patch("fastgear_cli.core.filesystem.ROOT_DIR", Path("/mock"))
        conditional_files = {"Dockerfile": True, "Makefile": False}

        create_project(
            "new_project",
            output_directory,
            sample_context,
            conditional_files=conditional_files,
        )

        call_args = mock_render.call_args
        assert call_args[0][3] == conditional_files

    @pytest.mark.it("✅  Should pass conditional_dirs when provided")
    def test_passes_conditional_dirs_when_provided(
        self,
        mocker: MagicMock,
        output_directory: Path,
        sample_context: dict,
    ):
        mock_render = mocker.patch("fastgear_cli.core.filesystem.render_template_dir")
        mocker.patch("fastgear_cli.core.filesystem.ROOT_DIR", Path("/mock"))
        conditional_dirs = {"docker": True, "tests": False}

        create_project(
            "new_project",
            output_directory,
            sample_context,
            conditional_dirs=conditional_dirs,
        )

        call_args = mock_render.call_args
        assert call_args[0][4] == conditional_dirs

    @pytest.mark.it("✅  Should construct correct template path from ROOT_DIR")
    def test_constructs_correct_template_path(
        self,
        mocker: MagicMock,
        output_directory: Path,
        sample_context: dict,
    ):
        mock_render = mocker.patch("fastgear_cli.core.filesystem.render_template_dir")
        fake_root = Path("/fake/root")
        mocker.patch("fastgear_cli.core.filesystem.ROOT_DIR", fake_root)

        create_project("custom_template", output_directory, sample_context)

        call_args = mock_render.call_args
        expected_template_root = fake_root / "templates" / "custom_template"
        assert call_args[0][0] == expected_template_root


@pytest.mark.describe("🧪  CreateProjectIntegration")
class TestCreateProjectIntegration:
    @pytest.mark.it("✅  Should create project files from template")
    def test_creates_project_files_from_template(
        self,
        mocker: MagicMock,
        template_with_files: Path,
        output_directory: Path,
        sample_context: dict,
    ):
        mocker.patch(
            "fastgear_cli.core.filesystem.ROOT_DIR",
            template_with_files.parent.parent,
        )

        create_project("test_template", output_directory, sample_context)

        project_dir = output_directory / "my-project"
        assert project_dir.exists()
        assert (project_dir / "README.md").exists()
        assert (project_dir / "config.txt").exists()

    @pytest.mark.it("✅  Should render Jinja2 templates with context")
    def test_renders_jinja2_templates_with_context(
        self,
        mocker: MagicMock,
        template_with_files: Path,
        output_directory: Path,
        sample_context: dict,
    ):
        mocker.patch(
            "fastgear_cli.core.filesystem.ROOT_DIR",
            template_with_files.parent.parent,
        )

        create_project("test_template", output_directory, sample_context)

        readme_path = output_directory / "my-project" / "README.md"
        content = readme_path.read_text()
        assert "# My Project" in content

    @pytest.mark.it("✅  Should copy static files without modification")
    def test_copies_static_files_without_modification(
        self,
        mocker: MagicMock,
        template_with_files: Path,
        output_directory: Path,
        sample_context: dict,
    ):
        mocker.patch(
            "fastgear_cli.core.filesystem.ROOT_DIR",
            template_with_files.parent.parent,
        )

        create_project("test_template", output_directory, sample_context)

        config_path = output_directory / "my-project" / "config.txt"
        content = config_path.read_text()
        assert content == "static content"

    @pytest.mark.it("✅  Should skip conditional directories when disabled")
    def test_skips_conditional_dirs_when_disabled(
        self,
        mocker: MagicMock,
        template_with_conditional_dir: Path,
        output_directory: Path,
        sample_context: dict,
    ):
        mocker.patch(
            "fastgear_cli.core.filesystem.ROOT_DIR",
            template_with_conditional_dir.parent.parent,
        )

        create_project(
            "test_template",
            output_directory,
            sample_context,
            conditional_dirs={"docker": False},
        )

        project_dir = output_directory / "my-project"
        assert not (project_dir / "docker").exists()
        assert (project_dir / "src" / "main.py").exists()

    @pytest.mark.it("✅  Should include conditional directories when enabled")
    def test_includes_conditional_dirs_when_enabled(
        self,
        mocker: MagicMock,
        template_with_conditional_dir: Path,
        output_directory: Path,
        sample_context: dict,
    ):
        mocker.patch(
            "fastgear_cli.core.filesystem.ROOT_DIR",
            template_with_conditional_dir.parent.parent,
        )

        create_project(
            "test_template",
            output_directory,
            sample_context,
            conditional_dirs={"docker": True},
        )

        project_dir = output_directory / "my-project"
        assert (project_dir / "docker" / "Dockerfile").exists()

    @pytest.mark.it("✅  Should skip conditional files when disabled")
    def test_skips_conditional_files_when_disabled(
        self,
        mocker: MagicMock,
        template_with_conditional_file: Path,
        output_directory: Path,
        sample_context: dict,
    ):
        mocker.patch(
            "fastgear_cli.core.filesystem.ROOT_DIR",
            template_with_conditional_file.parent.parent,
        )

        create_project(
            "test_template",
            output_directory,
            sample_context,
            conditional_files={"OPTIONAL.md": False},
        )

        project_dir = output_directory / "my-project"
        assert (project_dir / "README.md").exists()
        assert not (project_dir / "OPTIONAL.md").exists()

    @pytest.mark.it("✅  Should include conditional files when enabled")
    def test_includes_conditional_files_when_enabled(
        self,
        mocker: MagicMock,
        template_with_conditional_file: Path,
        output_directory: Path,
        sample_context: dict,
    ):
        mocker.patch(
            "fastgear_cli.core.filesystem.ROOT_DIR",
            template_with_conditional_file.parent.parent,
        )

        create_project(
            "test_template",
            output_directory,
            sample_context,
            conditional_files={"OPTIONAL.md": True},
        )

        project_dir = output_directory / "my-project"
        assert (project_dir / "README.md").exists()
        assert (project_dir / "OPTIONAL.md").exists()
