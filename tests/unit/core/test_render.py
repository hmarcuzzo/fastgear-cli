from pathlib import Path

import pytest

from fastgear_cli.core.render import (
    _should_render_dir,
    _should_render_file,
    render_template_dir,
)

pytest_plugins = ["tests.fixtures.core.render_fixtures"]


@pytest.mark.describe("🧪  RenderTemplateDir")
class TestRenderTemplateDir:
    @pytest.mark.it("✅  Should render Jinja2 template files with context")
    def test_renders_jinja2_template_with_context(
        self,
        template_with_jinja2_file: Path,
        output_root: Path,
        simple_context: dict,
    ):
        render_template_dir(
            template_with_jinja2_file,
            output_root,
            simple_context,
            {},
            {},
        )

        readme_path = output_root / "README.md"
        assert readme_path.exists()
        content = readme_path.read_text()
        assert "# My Project" in content
        assert "Project: my-project" in content

    @pytest.mark.it("✅  Should remove .j2 extension from rendered files")
    def test_removes_j2_extension_from_rendered_files(
        self,
        template_with_jinja2_file: Path,
        output_root: Path,
        simple_context: dict,
    ):
        render_template_dir(
            template_with_jinja2_file,
            output_root,
            simple_context,
            {},
            {},
        )

        assert (output_root / "README.md").exists()
        assert not (output_root / "README.md.j2").exists()

    @pytest.mark.it("✅  Should copy static files without modification")
    def test_copies_static_files_without_modification(
        self,
        template_with_static_file: Path,
        output_root: Path,
        simple_context: dict,
    ):
        render_template_dir(
            template_with_static_file,
            output_root,
            simple_context,
            {},
            {},
        )

        static_path = output_root / "static.txt"
        assert static_path.exists()
        assert static_path.read_text() == "This is static content"

    @pytest.mark.it("✅  Should create nested directory structure")
    def test_creates_nested_directory_structure(
        self,
        template_with_nested_dirs: Path,
        output_root: Path,
        simple_context: dict,
    ):
        render_template_dir(
            template_with_nested_dirs,
            output_root,
            simple_context,
            {},
            {},
        )

        expected_file = output_root / "my-project" / "src" / "main.py"
        assert expected_file.exists()

    @pytest.mark.it("✅  Should render directory names with context")
    def test_renders_directory_names_with_context(
        self,
        template_with_nested_dirs: Path,
        output_root: Path,
        simple_context: dict,
    ):
        render_template_dir(
            template_with_nested_dirs,
            output_root,
            simple_context,
            {},
            {},
        )

        assert (output_root / "my-project").exists()
        assert (output_root / "my-project").is_dir()

    @pytest.mark.it("✅  Should skip files in disabled conditional directories")
    def test_skips_files_in_disabled_conditional_dirs(
        self,
        template_with_conditional_dir: Path,
        output_root: Path,
        simple_context: dict,
    ):
        render_template_dir(
            template_with_conditional_dir,
            output_root,
            simple_context,
            {},
            {"docker": False},
        )

        assert not (output_root / "docker").exists()
        assert (output_root / "src" / "app.py").exists()

    @pytest.mark.it("✅  Should include files in enabled conditional directories")
    def test_includes_files_in_enabled_conditional_dirs(
        self,
        template_with_conditional_dir: Path,
        output_root: Path,
        simple_context: dict,
    ):
        render_template_dir(
            template_with_conditional_dir,
            output_root,
            simple_context,
            {},
            {"docker": True},
        )

        assert (output_root / "docker" / "Dockerfile").exists()
        assert (output_root / "src" / "app.py").exists()

    @pytest.mark.it("✅  Should skip disabled conditional files")
    def test_skips_disabled_conditional_files(
        self,
        template_with_conditional_file: Path,
        output_root: Path,
        simple_context: dict,
    ):
        render_template_dir(
            template_with_conditional_file,
            output_root,
            simple_context,
            {".dockerignore": False},
            {},
        )

        assert (output_root / "README.md").exists()
        assert not (output_root / ".dockerignore").exists()

    @pytest.mark.it("✅  Should include enabled conditional files")
    def test_includes_enabled_conditional_files(
        self,
        template_with_conditional_file: Path,
        output_root: Path,
        simple_context: dict,
    ):
        render_template_dir(
            template_with_conditional_file,
            output_root,
            simple_context,
            {".dockerignore": True},
            {},
        )

        assert (output_root / "README.md").exists()
        assert (output_root / ".dockerignore").exists()

    @pytest.mark.it("✅  Should preserve trailing newlines in templates")
    def test_preserves_trailing_newlines_in_templates(
        self,
        template_root: Path,
        output_root: Path,
        simple_context: dict,
    ):
        template_file = template_root / "file.txt.j2"
        template_file.write_text("content\n")

        render_template_dir(
            template_root,
            output_root,
            simple_context,
            {},
            {},
        )

        output_file = output_root / "file.txt"
        assert output_file.read_text().endswith("\n")


@pytest.mark.describe("🧪  ShouldRenderDir")
class TestShouldRenderDir:
    @pytest.mark.it("✅  Should return True when no conditional dirs")
    def test_returns_true_when_no_conditional_dirs(self):
        rel_path = Path("src/main.py")

        result = _should_render_dir(rel_path, {})

        assert result is True

    @pytest.mark.it("✅  Should return True when dir not in conditionals")
    def test_returns_true_when_dir_not_in_conditionals(self):
        rel_path = Path("src/main.py")

        result = _should_render_dir(rel_path, {"docker": False})

        assert result is True

    @pytest.mark.it("✅  Should return True when conditional dir is enabled")
    def test_returns_true_when_conditional_dir_enabled(self):
        rel_path = Path("docker/Dockerfile")

        result = _should_render_dir(rel_path, {"docker": True})

        assert result is True

    @pytest.mark.it("✅  Should return False when conditional dir is disabled")
    def test_returns_false_when_conditional_dir_disabled(self):
        rel_path = Path("docker/Dockerfile")

        result = _should_render_dir(rel_path, {"docker": False})

        assert result is False

    @pytest.mark.it("✅  Should check parent directories in path")
    def test_checks_parent_directories_in_path(self):
        rel_path = Path("docker/configs/settings.yml")

        result = _should_render_dir(rel_path, {"docker": False})

        assert result is False

    @pytest.mark.it("✅  Should return True for deeply nested enabled dir")
    def test_returns_true_for_deeply_nested_enabled_dir(self):
        rel_path = Path("docker/configs/settings.yml")

        result = _should_render_dir(rel_path, {"docker": True, "configs": True})

        assert result is True

    @pytest.mark.it("✅  Should return False when any parent dir is disabled")
    def test_returns_false_when_any_parent_disabled(self):
        rel_path = Path("docker/configs/settings.yml")

        result = _should_render_dir(rel_path, {"docker": True, "configs": False})

        assert result is False


@pytest.mark.describe("🧪  ShouldRenderFile")
class TestShouldRenderFile:
    @pytest.mark.it("✅  Should return True when no conditional files")
    def test_returns_true_when_no_conditional_files(self):
        result = _should_render_file("README.md", {})

        assert result is True

    @pytest.mark.it("✅  Should return True when file not in conditionals")
    def test_returns_true_when_file_not_in_conditionals(self):
        result = _should_render_file("README.md", {".dockerignore": False})

        assert result is True

    @pytest.mark.it("✅  Should return True when conditional file is enabled")
    def test_returns_true_when_conditional_file_enabled(self):
        result = _should_render_file(".dockerignore", {".dockerignore": True})

        assert result is True

    @pytest.mark.it("✅  Should return False when conditional file is disabled")
    def test_returns_false_when_conditional_file_disabled(self):
        result = _should_render_file(".dockerignore", {".dockerignore": False})

        assert result is False

    @pytest.mark.it("✅  Should handle multiple conditional files")
    def test_handles_multiple_conditional_files(self):
        conditionals = {
            ".dockerignore": True,
            "Makefile": False,
            "docker-compose.yml": True,
        }

        assert _should_render_file(".dockerignore", conditionals) is True
        assert _should_render_file("Makefile", conditionals) is False
        assert _should_render_file("docker-compose.yml", conditionals) is True
        assert _should_render_file("README.md", conditionals) is True
