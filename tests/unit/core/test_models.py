from pathlib import Path

import pytest
from pydantic import ValidationError

from fastgear_cli.core.models import ProjectInitConfig

pytest_plugins = ["tests.fixtures.core.models_fixtures"]


@pytest.mark.describe("🧪  ProjectInitConfig")
class TestProjectInitConfig:
    @pytest.mark.it("✅  Should create config with valid data")
    def test_creates_config_with_valid_data(
        self,
        project_config_data: dict,
    ):
        config = ProjectInitConfig(**project_config_data)

        assert config.project_name == "test-project"
        assert config.project_title == "Test Project"
        assert config.use_docker is True
        assert config.base_dir == project_config_data["base_dir"]

    @pytest.mark.it("✅  Should use current directory as default base_dir")
    def test_uses_cwd_as_default_base_dir(self):
        config = ProjectInitConfig(
            project_name="my-project",
            project_title="My Project",
        )

        assert config.base_dir == Path.cwd()

    @pytest.mark.it("✅  Should default use_docker to True")
    def test_defaults_use_docker_to_true(self):
        config = ProjectInitConfig(
            project_name="my-project",
            project_title="My Project",
        )

        assert config.use_docker is True

    @pytest.mark.it("✅  Should strip whitespace from project_name")
    def test_strips_whitespace_from_project_name(self):
        config = ProjectInitConfig(
            project_name="  my-project  ",
            project_title="My Project",
        )

        assert config.project_name == "my-project"

    @pytest.mark.it("❌  Should raise ValidationError for empty project_name")
    def test_raises_error_for_empty_project_name(self):
        with pytest.raises(ValidationError) as exc_info:
            ProjectInitConfig(
                project_name="",
                project_title="My Project",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("project_name",) for error in errors)

    @pytest.mark.it("❌  Should raise ValidationError for empty project_title")
    def test_raises_error_for_empty_project_title(self):
        with pytest.raises(ValidationError) as exc_info:
            ProjectInitConfig(
                project_name="my-project",
                project_title="",
            )

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("project_title",) for error in errors)

    @pytest.mark.it("✅  Should strip whitespace-only project_name to empty string")
    def test_strips_whitespace_only_project_name(self):
        config = ProjectInitConfig(
            project_name="  a  ",
            project_title="My Project",
        )

        assert config.project_name == "a"


@pytest.mark.describe("🧪  ProjectInitConfigProjectDir")
class TestProjectInitConfigProjectDir:
    @pytest.mark.it("✅  Should return correct project_dir path")
    def test_returns_correct_project_dir_path(
        self,
        temp_directory: Path,
    ):
        config = ProjectInitConfig(
            base_dir=temp_directory,
            project_name="my-project",
            project_title="My Project",
        )

        assert config.project_dir == temp_directory / "my-project"

    @pytest.mark.it("✅  Should combine base_dir and project_name")
    def test_combines_base_dir_and_project_name(
        self,
        temp_directory: Path,
    ):
        config = ProjectInitConfig(
            base_dir=temp_directory / "subdir",
            project_name="test-app",
            project_title="Test App",
        )

        expected = temp_directory / "subdir" / "test-app"
        assert config.project_dir == expected


@pytest.mark.describe("🧪  ProjectInitConfigContext")
class TestProjectInitConfigContext:
    @pytest.mark.it("✅  Should return context dict with all required keys")
    def test_returns_context_with_all_keys(
        self,
        project_config_data: dict,
    ):
        config = ProjectInitConfig(**project_config_data)

        context = config.context

        assert "project_name" in context
        assert "project_title" in context
        assert "use_docker" in context

    @pytest.mark.it("✅  Should return correct values in context")
    def test_returns_correct_values_in_context(
        self,
        project_config_data: dict,
    ):
        config = ProjectInitConfig(**project_config_data)

        context = config.context

        assert context["project_name"] == "test-project"
        assert context["project_title"] == "Test Project"
        assert context["use_docker"] is True

    @pytest.mark.it("✅  Should reflect use_docker=False in context")
    def test_reflects_use_docker_false_in_context(
        self,
        project_config_without_docker: dict,
    ):
        config = ProjectInitConfig(**project_config_without_docker)

        context = config.context

        assert context["use_docker"] is False


@pytest.mark.describe("🧪  ProjectInitConfigConditionalFiles")
class TestProjectInitConfigConditionalFiles:
    @pytest.mark.it("✅  Should include .dockerignore when use_docker is True")
    def test_includes_dockerignore_when_use_docker_true(
        self,
        project_config_data: dict,
    ):
        config = ProjectInitConfig(**project_config_data)

        conditional_files = config.conditional_files

        assert ".dockerignore" in conditional_files
        assert conditional_files[".dockerignore"] is True

    @pytest.mark.it("✅  Should exclude .dockerignore when use_docker is False")
    def test_excludes_dockerignore_when_use_docker_false(
        self,
        project_config_without_docker: dict,
    ):
        config = ProjectInitConfig(**project_config_without_docker)

        conditional_files = config.conditional_files

        assert ".dockerignore" in conditional_files
        assert conditional_files[".dockerignore"] is False


@pytest.mark.describe("🧪  ProjectInitConfigConditionalDirs")
class TestProjectInitConfigConditionalDirs:
    @pytest.mark.it("✅  Should include docker dir when use_docker is True")
    def test_includes_docker_dir_when_use_docker_true(
        self,
        project_config_data: dict,
    ):
        config = ProjectInitConfig(**project_config_data)

        conditional_dirs = config.conditional_dirs

        assert "docker" in conditional_dirs
        assert conditional_dirs["docker"] is True

    @pytest.mark.it("✅  Should exclude docker dir when use_docker is False")
    def test_excludes_docker_dir_when_use_docker_false(
        self,
        project_config_without_docker: dict,
    ):
        config = ProjectInitConfig(**project_config_without_docker)

        conditional_dirs = config.conditional_dirs

        assert "docker" in conditional_dirs
        assert conditional_dirs["docker"] is False
