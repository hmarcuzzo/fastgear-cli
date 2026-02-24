from unittest.mock import MagicMock

import pytest

from fastgear_cli.cli.prompts.project import (
    ask_agent_tools,
    ask_ci_provider,
    ask_project_name,
    confirm_project_title,
)
from fastgear_cli.core.constants.enums import AgentToolsEnum, CIProviderEnum

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


@pytest.mark.describe("🧪  ask_agent_tools")
class TestAskAgentTools:
    @pytest.mark.it("✅  Should return empty list when user disables agent tools")
    def test_returns_empty_list_when_user_disables_agent_tools(self, mocker: MagicMock):
        mock_confirm = mocker.patch("fastgear_cli.cli.prompts.project.questionary.confirm")
        mock_confirm.return_value.ask.return_value = False
        mock_checkbox = mocker.patch("fastgear_cli.cli.prompts.project.questionary.checkbox")

        result = ask_agent_tools()

        assert result == []
        mock_checkbox.assert_not_called()

    @pytest.mark.it("✅  Should return selected agent tools when enabled")
    def test_returns_selected_agent_tools_when_enabled(self, mocker: MagicMock):
        mock_confirm = mocker.patch("fastgear_cli.cli.prompts.project.questionary.confirm")
        mock_confirm.return_value.ask.return_value = True
        mock_checkbox = mocker.patch("fastgear_cli.cli.prompts.project.questionary.checkbox")
        mock_checkbox.return_value.ask.return_value = [AgentToolsEnum.GITHUB_COPILOT]

        result = ask_agent_tools()

        assert result == [AgentToolsEnum.GITHUB_COPILOT]
        mock_checkbox.assert_called_once_with(
            "Select agent tools:",
            choices=[AgentToolsEnum.GITHUB_COPILOT],
        )

    @pytest.mark.it("✅  Should return empty list when checkbox result is None")
    def test_returns_empty_list_when_checkbox_result_is_none(self, mocker: MagicMock):
        mock_confirm = mocker.patch("fastgear_cli.cli.prompts.project.questionary.confirm")
        mock_confirm.return_value.ask.return_value = True
        mock_checkbox = mocker.patch("fastgear_cli.cli.prompts.project.questionary.checkbox")
        mock_checkbox.return_value.ask.return_value = None

        result = ask_agent_tools()

        assert result == []
        mock_confirm.assert_called_once_with("Use AI agent tools?", default=False)


@pytest.mark.describe("🧪  ask_ci_provider")
class TestAskCIProvider:
    @pytest.mark.it("✅  Should return None when user disables CI")
    def test_returns_none_when_user_disables_ci(self, mocker: MagicMock):
        mock_confirm = mocker.patch("fastgear_cli.cli.prompts.project.questionary.confirm")
        mock_confirm.return_value.ask.return_value = False
        mock_select = mocker.patch("fastgear_cli.cli.prompts.project.questionary.select")

        result = ask_ci_provider()

        assert result is None
        mock_select.assert_not_called()

    @pytest.mark.it("✅  Should return selected CI provider when enabled")
    def test_returns_selected_ci_provider_when_enabled(self, mocker: MagicMock):
        mock_confirm = mocker.patch("fastgear_cli.cli.prompts.project.questionary.confirm")
        mock_confirm.return_value.ask.return_value = True
        mock_select = mocker.patch("fastgear_cli.cli.prompts.project.questionary.select")
        mock_select.return_value.ask.return_value = CIProviderEnum.GITHUB_ACTIONS

        result = ask_ci_provider()

        assert result == CIProviderEnum.GITHUB_ACTIONS
        mock_select.assert_called_once_with(
            "Select CI/CD provider:",
            choices=[CIProviderEnum.GITHUB_ACTIONS],
        )

    @pytest.mark.it("✅  Should call confirm with CI prompt and default true")
    def test_calls_confirm_with_ci_prompt_and_default_true(self, mocker: MagicMock):
        mock_confirm = mocker.patch("fastgear_cli.cli.prompts.project.questionary.confirm")
        mock_confirm.return_value.ask.return_value = False

        ask_ci_provider()

        mock_confirm.assert_called_once_with("Use CI/CD pipeline?", default=True)
