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

    @pytest.mark.it("✅  Should create service files without repository")
    def test_creates_service_files_without_repository(
        self,
        temp_path: Path,
        mocker,
    ):
        mock_confirm = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_service_helper.questionary.confirm"
        )
        mock_confirm.return_value.ask.return_value = False

        result = runner.invoke(add_app, ["service", "billing", "--path", str(temp_path)])

        assert result.exit_code == 0
        assert (temp_path / "services/__init__.py").exists()
        service_file = temp_path / "services/billing_service.py"
        assert service_file.exists()
        service_content = service_file.read_text(encoding="utf-8")
        assert "class BillingService" in service_content
        assert "pass" in service_content
        assert "import" not in service_content

    @pytest.mark.it("✅  Should create service files with repository via option")
    def test_creates_service_files_with_repository_option(self, temp_path: Path):
        result = runner.invoke(
            add_app,
            [
                "service",
                "order",
                "--path",
                str(temp_path),
                "--repository-path",
                "src.modules.sales.repositories.order_repository.OrderRepository",
            ],
        )

        assert result.exit_code == 0
        service_file = temp_path / "services/order_service.py"
        assert service_file.exists()
        service_content = service_file.read_text(encoding="utf-8")
        assert (
            "from src.modules.sales.repositories.order_repository import OrderRepository"
            in service_content
        )
        assert "def __init__(self, repository: OrderRepository = None)" in service_content
        assert "self.repository = repository or OrderRepository()" in service_content

    @pytest.mark.it("✅  Should ask for repository path when adding service and user wants it")
    def test_asks_for_repository_path_when_adding_service(
        self,
        temp_path: Path,
        mocker,
    ):
        mock_confirm = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_service_helper.questionary.confirm"
        )
        mock_confirm.return_value.ask.return_value = True
        mock_text = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_service_helper.questionary.text"
        )
        mock_text.return_value.ask.return_value = (
            "src.modules.billing.repositories.invoice_repository.InvoiceRepository"
        )

        result = runner.invoke(add_app, ["service", "invoice", "--path", str(temp_path)])

        assert result.exit_code == 0
        service_file = temp_path / "services/invoice_service.py"
        assert service_file.exists()
        assert (
            "from src.modules.billing.repositories.invoice_repository import InvoiceRepository"
            in service_file.read_text(encoding="utf-8")
        )

    @pytest.mark.it("❌  Should fail with invalid service repository path")
    def test_fails_with_invalid_service_repository_path(self, temp_path: Path):
        result = runner.invoke(
            add_app,
            [
                "service",
                "invoice",
                "--path",
                str(temp_path),
                "--repository-path",
                "invoice_repository",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid repository path." in result.output

    @pytest.mark.it("✅  Should create controller files without service")
    def test_creates_controller_files_without_service(
        self,
        temp_path: Path,
        mocker,
    ):
        mock_confirm = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_controller_helper.questionary.confirm"
        )
        mock_confirm.return_value.ask.return_value = False

        result = runner.invoke(add_app, ["controller", "billing", "--path", str(temp_path)])

        assert result.exit_code == 0
        assert (temp_path / "controllers/__init__.py").exists()
        init_content = (temp_path / "controllers/__init__.py").read_text(encoding="utf-8")
        assert "from .billing_controller import billing_router" in init_content
        assert "billing_router" in init_content
        controller_file = temp_path / "controllers/billing_controller.py"
        assert controller_file.exists()
        controller_content = controller_file.read_text(encoding="utf-8")
        assert "from fastapi import APIRouter" in controller_content
        assert "from fastgear.decorators import controller" in controller_content
        assert "billing_router = APIRouter(tags=[" in controller_content
        assert "@controller(billing_router)" in controller_content
        assert "class BillingController" in controller_content
        assert "pass" in controller_content

    @pytest.mark.it("✅  Should create controller files with service via option")
    def test_creates_controller_files_with_service_option(self, temp_path: Path):
        result = runner.invoke(
            add_app,
            [
                "controller",
                "order",
                "--path",
                str(temp_path),
                "--service-path",
                "src.modules.sales.services.order_service.OrderService",
            ],
        )

        assert result.exit_code == 0
        controller_file = temp_path / "controllers/order_controller.py"
        assert controller_file.exists()
        controller_content = controller_file.read_text(encoding="utf-8")
        assert "from fastapi import APIRouter" in controller_content
        assert "from fastgear.decorators import controller" in controller_content
        assert "order_router = APIRouter(tags=[" in controller_content
        assert "@controller(order_router)" in controller_content
        assert (
            "from src.modules.sales.services.order_service import OrderService"
            in controller_content
        )
        assert "def __init__(self, service: OrderService = None)" in controller_content
        assert "self.service = service or OrderService()" in controller_content

    @pytest.mark.it("✅  Should ask for service path when adding controller and user wants it")
    def test_asks_for_service_path_when_adding_controller(
        self,
        temp_path: Path,
        mocker,
    ):
        mock_confirm = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_controller_helper.questionary.confirm"
        )
        mock_confirm.return_value.ask.return_value = True
        mock_text = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_controller_helper.questionary.text"
        )
        mock_text.return_value.ask.return_value = (
            "src.modules.billing.services.invoice_service.InvoiceService"
        )

        result = runner.invoke(add_app, ["controller", "invoice", "--path", str(temp_path)])

        assert result.exit_code == 0
        controller_file = temp_path / "controllers/invoice_controller.py"
        assert controller_file.exists()
        assert (
            "from src.modules.billing.services.invoice_service import InvoiceService"
            in controller_file.read_text(encoding="utf-8")
        )

    @pytest.mark.it("❌  Should fail with invalid controller service path")
    def test_fails_with_invalid_controller_service_path(self, temp_path: Path):
        result = runner.invoke(
            add_app,
            [
                "controller",
                "invoice",
                "--path",
                str(temp_path),
                "--service-path",
                "invoice_service",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid service path." in result.output

    @pytest.mark.it("✅  Should update controllers __init__ when it already exists")
    def test_updates_controllers_init_when_it_already_exists(
        self,
        temp_path: Path,
        mocker,
    ):
        mock_confirm = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_controller_helper.questionary.confirm"
        )
        mock_confirm.return_value.ask.return_value = False

        existing_init = temp_path / "controllers/__init__.py"
        existing_init.parent.mkdir(parents=True, exist_ok=True)
        existing_init.write_text(
            'from .customer_controller import customer_router\n\n__all__ = ["customer_router"]\n',
            encoding="utf-8",
        )

        result = runner.invoke(add_app, ["controller", "billing", "--path", str(temp_path)])

        assert result.exit_code == 0
        init_content = existing_init.read_text(encoding="utf-8")
        assert "from .billing_controller import billing_router" in init_content
        assert '"customer_router"' in init_content
        assert '"billing_router"' in init_content
