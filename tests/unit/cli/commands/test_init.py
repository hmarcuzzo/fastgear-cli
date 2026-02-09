import subprocess
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from typer.testing import CliRunner

from fastgear_cli.cli.commands.init import init_app

pytest_plugins = ["tests.fixtures.cli.commands.init_fixtures"]

runner = CliRunner()


@pytest.mark.describe("🧪  InitCommand")
class TestInitCommand:
    @pytest.mark.it("✅  Should create project in specified directory")
    def test_creates_project_in_current_directory(
        self,
        mocker: MagicMock,
        temp_directory: Path,
        project_name: str,
        project_title: str,
    ):
        mocker.patch(
            "fastgear_cli.cli.commands.init.ask_project_name",
            return_value=project_name,
        )
        mocker.patch(
            "fastgear_cli.cli.commands.init.confirm_project_title",
            return_value=project_title,
        )
        mocker.patch("fastgear_cli.cli.commands.init.typer.confirm", return_value=True)
        mock_create = mocker.patch("fastgear_cli.cli.commands.init.create_project")
        mocker.patch("fastgear_cli.cli.commands.init.subprocess.run")

        result = runner.invoke(init_app, [str(temp_directory)])

        assert result.exit_code == 0
        mock_create.assert_called_once()
        call_args = mock_create.call_args
        assert call_args[0][0] == "new_project"
        assert call_args[0][1] == temp_directory

    @pytest.mark.it("✅  Should create project in custom directory argument")
    def test_creates_project_with_directory_argument(
        self,
        mocker: MagicMock,
        temp_directory: Path,
        project_name: str,
        project_title: str,
    ):
        custom_dir = temp_directory / "custom"
        custom_dir.mkdir()

        mocker.patch(
            "fastgear_cli.cli.commands.init.ask_project_name",
            return_value=project_name,
        )
        mocker.patch(
            "fastgear_cli.cli.commands.init.confirm_project_title",
            return_value=project_title,
        )
        mocker.patch("fastgear_cli.cli.commands.init.typer.confirm", return_value=True)
        mock_create = mocker.patch("fastgear_cli.cli.commands.init.create_project")
        mocker.patch("fastgear_cli.cli.commands.init.subprocess.run")

        result = runner.invoke(init_app, [str(custom_dir)])

        assert result.exit_code == 0
        call_args = mock_create.call_args
        assert call_args[0][1] == custom_dir

    @pytest.mark.it("✅  Should create project without docker when user declines")
    def test_creates_project_without_docker(
        self,
        mocker: MagicMock,
        temp_directory: Path,
        project_name: str,
        project_title: str,
    ):
        mocker.patch(
            "fastgear_cli.cli.commands.init.ask_project_name",
            return_value=project_name,
        )
        mocker.patch(
            "fastgear_cli.cli.commands.init.confirm_project_title",
            return_value=project_title,
        )
        mocker.patch("fastgear_cli.cli.commands.init.typer.confirm", return_value=False)
        mock_create = mocker.patch("fastgear_cli.cli.commands.init.create_project")
        mocker.patch("fastgear_cli.cli.commands.init.subprocess.run")

        result = runner.invoke(init_app, [str(temp_directory)])

        assert result.exit_code == 0
        call_args = mock_create.call_args
        context = call_args[0][2]
        assert context["use_docker"] is False

    @pytest.mark.it("❌  Should fail when project directory already exists")
    def test_fails_when_directory_exists(
        self,
        mocker: MagicMock,
        temp_directory: Path,
        project_name: str,
        project_title: str,
    ):
        mocker.patch(
            "fastgear_cli.cli.commands.init.ask_project_name",
            return_value=project_name,
        )
        mocker.patch(
            "fastgear_cli.cli.commands.init.confirm_project_title",
            return_value=project_title,
        )
        mocker.patch("fastgear_cli.cli.commands.init.typer.confirm", return_value=True)
        mocker.patch(
            "fastgear_cli.cli.commands.init.create_project",
            side_effect=FileExistsError,
        )

        result = runner.invoke(init_app, [str(temp_directory)])

        assert result.exit_code == 1
        assert "already exists" in result.output

    @pytest.mark.it("✅  Should run uv lock after project creation")
    def test_runs_uv_lock_after_project_creation(
        self,
        mocker: MagicMock,
        temp_directory: Path,
        project_name: str,
        project_title: str,
    ):
        mocker.patch(
            "fastgear_cli.cli.commands.init.ask_project_name",
            return_value=project_name,
        )
        mocker.patch(
            "fastgear_cli.cli.commands.init.confirm_project_title",
            return_value=project_title,
        )
        mocker.patch("fastgear_cli.cli.commands.init.typer.confirm", return_value=True)
        mocker.patch("fastgear_cli.cli.commands.init.create_project")
        mock_subprocess = mocker.patch("fastgear_cli.cli.commands.init.subprocess.run")

        result = runner.invoke(init_app, [str(temp_directory)])

        assert result.exit_code == 0
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args
        assert call_args[0][0] == ["uv", "lock"]
        assert "Generating uv.lock" in result.output

    @pytest.mark.it("⚠️  Should handle uv lock failure gracefully")
    def test_handles_uv_lock_failure(
        self,
        mocker: MagicMock,
        temp_directory: Path,
        project_name: str,
        project_title: str,
    ):
        mocker.patch(
            "fastgear_cli.cli.commands.init.ask_project_name",
            return_value=project_name,
        )
        mocker.patch(
            "fastgear_cli.cli.commands.init.confirm_project_title",
            return_value=project_title,
        )
        mocker.patch("fastgear_cli.cli.commands.init.typer.confirm", return_value=True)
        mocker.patch("fastgear_cli.cli.commands.init.create_project")
        mocker.patch(
            "fastgear_cli.cli.commands.init.subprocess.run",
            side_effect=subprocess.CalledProcessError(1, "uv lock", stderr="error"),
        )

        result = runner.invoke(init_app, [str(temp_directory)])

        assert result.exit_code == 0
        assert "Failed to generate uv.lock" in result.output

    @pytest.mark.it("⚠️  Should handle uv not found gracefully")
    def test_handles_uv_not_found(
        self,
        mocker: MagicMock,
        temp_directory: Path,
        project_name: str,
        project_title: str,
    ):
        mocker.patch(
            "fastgear_cli.cli.commands.init.ask_project_name",
            return_value=project_name,
        )
        mocker.patch(
            "fastgear_cli.cli.commands.init.confirm_project_title",
            return_value=project_title,
        )
        mocker.patch("fastgear_cli.cli.commands.init.typer.confirm", return_value=True)
        mocker.patch("fastgear_cli.cli.commands.init.create_project")
        mocker.patch(
            "fastgear_cli.cli.commands.init.subprocess.run",
            side_effect=FileNotFoundError,
        )

        result = runner.invoke(init_app, [str(temp_directory)])

        assert result.exit_code == 0
        assert "uv not found" in result.output

    @pytest.mark.it("✅  Should display success message with project name")
    def test_displays_success_message(
        self,
        mocker: MagicMock,
        temp_directory: Path,
        project_name: str,
        project_title: str,
    ):
        mocker.patch(
            "fastgear_cli.cli.commands.init.ask_project_name",
            return_value=project_name,
        )
        mocker.patch(
            "fastgear_cli.cli.commands.init.confirm_project_title",
            return_value=project_title,
        )
        mocker.patch("fastgear_cli.cli.commands.init.typer.confirm", return_value=True)
        mocker.patch("fastgear_cli.cli.commands.init.create_project")
        mocker.patch("fastgear_cli.cli.commands.init.subprocess.run")

        result = runner.invoke(init_app, [str(temp_directory)])

        assert result.exit_code == 0
        assert "created successfully" in result.output
        assert project_name in result.output
