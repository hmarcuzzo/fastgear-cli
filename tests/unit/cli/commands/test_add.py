from pathlib import Path

import pytest
from typer.testing import CliRunner

from fastgear_cli.cli.commands.add import add_app


@pytest.fixture
def temp_path(tmp_path: Path) -> Path:
    return tmp_path


runner = CliRunner()


@pytest.mark.describe("🧪  AddCommand")
class TestAddCommand:
    @pytest.mark.it("✅  Should create entity files using folders by default")
    def test_creates_entity_files_using_folders(self, temp_path: Path):
        result = runner.invoke(add_app, ["entity", "customer", "--path", str(temp_path)])

        assert result.exit_code == 0
        assert (temp_path / "entities/__init__.py").exists()
        entity_file = temp_path / "entities/customer_entity.py"
        assert entity_file.exists()
        assert "class Customer" in entity_file.read_text(encoding="utf-8")

    @pytest.mark.it("✅  Should create repository files")
    def test_creates_repository_files(self, temp_path: Path):
        result = runner.invoke(
            add_app,
            [
                "repository",
                "order",
                "--path",
                str(temp_path),
                "--entity-path",
                "src.modules.sales.entities.order_entity.Order",
            ],
        )

        assert result.exit_code == 0
        assert (temp_path / "repositories/__init__.py").exists()
        repository_file = temp_path / "repositories/order_repository.py"
        assert repository_file.exists()
        repository_content = repository_file.read_text(encoding="utf-8")
        assert "from src.modules.sales.entities.order_entity import Order" in repository_content
        assert "AsyncBaseRepository[Order]" in repository_content
        assert "class OrderRepository" in repository_file.read_text(encoding="utf-8")

    @pytest.mark.it("✅  Should ask for entity path when adding repository without flag")
    def test_asks_for_entity_path_when_not_passed(
        self,
        temp_path: Path,
        mocker,
    ):
        mock_text = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_repository_helper.questionary.text"
        )
        mock_text.return_value.ask.return_value = (
            "src.modules.billing.entities.invoice_entity.Invoice"
        )

        result = runner.invoke(add_app, ["repository", "invoice", "--path", str(temp_path)])

        assert result.exit_code == 0
        repository_file = temp_path / "repositories/invoice_repository.py"
        assert repository_file.exists()
        assert (
            "from src.modules.billing.entities.invoice_entity import Invoice"
            in repository_file.read_text(encoding="utf-8")
        )

    @pytest.mark.it("❌  Should fail when repository entity path is not provided")
    def test_fails_when_repository_entity_path_not_provided(
        self,
        temp_path: Path,
        mocker,
    ):
        mock_text = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_repository_helper.questionary.text"
        )
        mock_text.return_value.ask.return_value = ""

        result = runner.invoke(add_app, ["repository", "invoice", "--path", str(temp_path)])

        assert result.exit_code == 1
        assert "Entity path is required when adding a repository." in result.output

    @pytest.mark.it("❌  Should fail with invalid repository entity path")
    def test_fails_with_invalid_repository_entity_path(self, temp_path: Path):
        result = runner.invoke(
            add_app,
            [
                "repository",
                "invoice",
                "--path",
                str(temp_path),
                "--entity-path",
                "invoice_entity",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid entity path." in result.output

    @pytest.mark.it("✅  Should create flat entity file when requested")
    def test_creates_flat_entity_file(self, temp_path: Path):
        result = runner.invoke(
            add_app,
            ["entity", "customer", "--path", str(temp_path), "--no-use-folders"],
        )

        assert result.exit_code == 0
        entity_file = temp_path / "customer_entity.py"
        assert entity_file.exists()
        assert not (temp_path / "entities").exists()

    @pytest.mark.it("✅  Should normalize module names")
    def test_normalizes_element_names(self, temp_path: Path):
        result = runner.invoke(add_app, ["entity", "UserProfile", "--path", str(temp_path)])

        assert result.exit_code == 0
        entity_file = temp_path / "entities/user_profile_entity.py"
        assert entity_file.exists()
        assert "class UserProfile" in entity_file.read_text(encoding="utf-8")

    @pytest.mark.it("✅  Should support dry run")
    def test_dry_run(self, temp_path: Path):
        result = runner.invoke(
            add_app,
            ["entity", "customer", "--path", str(temp_path), "--dry-run"],
        )

        assert result.exit_code == 0
        assert "Dry run mode" in result.output
        assert not (temp_path / "entities/customer_entity.py").exists()

    @pytest.mark.it("✅  Should use current directory when path is not provided")
    def test_uses_current_directory_when_path_not_provided(
        self,
        temp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(temp_path)
        result = runner.invoke(add_app, ["entity", "billing"])

        assert result.exit_code == 0
        assert (temp_path / "entities/billing_entity.py").exists()

    @pytest.mark.it("✅  Should update entities __init__ when it already exists")
    def test_updates_entities_init_when_it_already_exists(self, temp_path: Path):
        existing_init = temp_path / "entities/__init__.py"
        existing_init.parent.mkdir(parents=True, exist_ok=True)
        existing_init.write_text(
            'from .customer_entity import Customer\n\n__all__ = ["Customer"]\n',
            encoding="utf-8",
        )

        result = runner.invoke(add_app, ["entity", "billing", "--path", str(temp_path)])

        assert result.exit_code == 0
        init_content = existing_init.read_text(encoding="utf-8")
        assert "from .billing_entity import Billing" in init_content
        assert '"Customer"' in init_content
        assert '"Billing"' in init_content

    @pytest.mark.it("❌  Should fail with invalid element")
    def test_fails_with_invalid_element(self, temp_path: Path):
        result = runner.invoke(add_app, ["invalid", "customer", "--path", str(temp_path)])

        assert result.exit_code == 1
        assert "Invalid element type" in result.output
