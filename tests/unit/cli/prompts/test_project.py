from unittest.mock import MagicMock

import pytest

from fastgear_cli.cli.prompts.project import ask_project_name, confirm_project_title

pytest_plugins = ["tests.fixtures.cli.prompts.project_fixtures"]


@pytest.mark.describe("🧪  ask_project_name")
class TestAskProjectName:
    @pytest.mark.it("✅  Should return user input when valid name is provided")
    def test_returns_valid_project_name(
        self,
        mocker: MagicMock,
        valid_project_name: str,
    ):
        mock_text = mocker.patch("fastgear_cli.cli.prompts.project.questionary.text")
        mock_text.return_value.ask.return_value = valid_project_name

        result = ask_project_name()

        assert result == valid_project_name
        mock_text.assert_called_once()

    @pytest.mark.it("✅  Should call questionary.text with correct prompt message")
    def test_calls_questionary_with_correct_prompt(self, mocker: MagicMock):
        mock_text = mocker.patch("fastgear_cli.cli.prompts.project.questionary.text")
        mock_text.return_value.ask.return_value = "test"

        ask_project_name()

        call_args = mock_text.call_args
        assert call_args[0][0] == "Project name:"

    @pytest.mark.it("✅  Should have validation that rejects empty names")
    def test_validation_rejects_empty_name(self, mocker: MagicMock):
        mock_text = mocker.patch("fastgear_cli.cli.prompts.project.questionary.text")
        mock_text.return_value.ask.return_value = "test"

        ask_project_name()

        call_kwargs = mock_text.call_args[1]
        validator = call_kwargs["validate"]

        assert validator("") == "Name cannot be empty"
        assert validator("   ") == "Name cannot be empty"

    @pytest.mark.it("✅  Should have validation that accepts non-empty names")
    def test_validation_accepts_valid_name(self, mocker: MagicMock):
        mock_text = mocker.patch("fastgear_cli.cli.prompts.project.questionary.text")
        mock_text.return_value.ask.return_value = "test"

        ask_project_name()

        call_kwargs = mock_text.call_args[1]
        validator = call_kwargs["validate"]

        assert validator("my-project") is True
        assert validator("  my-project  ") is True


@pytest.mark.describe("🧪  confirm_project_title")
class TestConfirmProjectTitle:
    @pytest.mark.it("✅  Should return user confirmed title")
    def test_returns_confirmed_title(self, mocker: MagicMock):
        expected_title = "My Custom Title"
        mock_text = mocker.patch("fastgear_cli.cli.prompts.project.questionary.text")
        mock_text.return_value.ask.return_value = expected_title

        result = confirm_project_title("my-project")

        assert result == expected_title

    @pytest.mark.it("✅  Should convert hyphens to spaces and title case")
    def test_converts_hyphens_to_title_case(
        self,
        mocker: MagicMock,
        valid_project_name: str,
    ):
        mock_text = mocker.patch("fastgear_cli.cli.prompts.project.questionary.text")
        mock_text.return_value.ask.return_value = "My Awesome Project"

        confirm_project_title(valid_project_name)

        call_kwargs = mock_text.call_args[1]
        assert call_kwargs["default"] == "My Awesome Project"

    @pytest.mark.it("✅  Should convert underscores to spaces and title case")
    def test_converts_underscores_to_title_case(
        self,
        mocker: MagicMock,
        project_name_with_underscores: str,
    ):
        mock_text = mocker.patch("fastgear_cli.cli.prompts.project.questionary.text")
        mock_text.return_value.ask.return_value = "My Awesome Project"

        confirm_project_title(project_name_with_underscores)

        call_kwargs = mock_text.call_args[1]
        assert call_kwargs["default"] == "My Awesome Project"

    @pytest.mark.it("✅  Should convert mixed separators to spaces and title case")
    def test_converts_mixed_separators_to_title_case(
        self,
        mocker: MagicMock,
        project_name_with_mixed_separators: str,
    ):
        mock_text = mocker.patch("fastgear_cli.cli.prompts.project.questionary.text")
        mock_text.return_value.ask.return_value = "My Awesome Project"

        confirm_project_title(project_name_with_mixed_separators)

        call_kwargs = mock_text.call_args[1]
        assert call_kwargs["default"] == "My Awesome Project"

    @pytest.mark.it("✅  Should call questionary.text with correct prompt message")
    def test_calls_questionary_with_correct_prompt(self, mocker: MagicMock):
        mock_text = mocker.patch("fastgear_cli.cli.prompts.project.questionary.text")
        mock_text.return_value.ask.return_value = "Test"

        confirm_project_title("test")

        call_args = mock_text.call_args
        assert call_args[0][0] == "Project title:"
