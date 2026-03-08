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

    @pytest.mark.it("✅  Should create repository without entity when user declines prompt")
    def test_creates_repository_without_entity_when_user_declines_prompt(
        self,
        temp_path: Path,
        mocker,
    ):
        mock_confirm = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_repository_helper.questionary.confirm"
        )
        mock_confirm.return_value.ask.return_value = False
        mock_text = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_repository_helper.questionary.text"
        )

        result = runner.invoke(add_app, ["repository", "invoice", "--path", str(temp_path)])

        assert result.exit_code == 0
        mock_text.assert_not_called()
        repository_file = temp_path / "repositories/invoice_repository.py"
        assert repository_file.exists()
        content = repository_file.read_text(encoding="utf-8")
        assert "from src.modules" not in content
        assert "from .entities" not in content
        assert "from ..entities" not in content
        assert "class InvoiceRepository:" in content
        assert "pass" in content

    @pytest.mark.it("✅  Should ask entity path when adding repository and user wants it")
    def test_asks_entity_path_when_adding_repository_and_user_wants_it(
        self,
        temp_path: Path,
        mocker,
    ):
        mock_confirm = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_repository_helper.questionary.confirm"
        )
        mock_confirm.return_value.ask.return_value = True
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

    @pytest.mark.it("✅  Should inject service into controller when both are selected for module")
    def test_injects_service_into_controller_when_both_selected_for_module(
        self,
        temp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(temp_path)
        modules_root = temp_path / "src" / "modules"

        result = runner.invoke(
            add_app,
            [
                "module",
                "billing",
                "--path",
                str(modules_root),
                "--module-components",
                "service,controller",
            ],
        )

        assert result.exit_code == 0
        assert (modules_root / "billing" / "__init__.py").exists()
        controller_file = modules_root / "billing" / "controllers" / "billing_controller.py"
        assert controller_file.exists()
        content = controller_file.read_text(encoding="utf-8")
        assert "from src.modules.billing.services import BillingService" in content
        assert "def __init__(self, service: BillingService = None)" in content
        assert "self.service = service or BillingService()" in content

    @pytest.mark.it(
        "✅  Should create controller without service when service is not selected in module"
    )
    def test_creates_controller_without_service_when_service_not_selected_in_module(
        self,
        temp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(temp_path)
        modules_root = temp_path / "src" / "modules"

        result = runner.invoke(
            add_app,
            [
                "module",
                "billing",
                "--path",
                str(modules_root),
                "--module-components",
                "controller",
            ],
        )

        assert result.exit_code == 0
        controller_file = modules_root / "billing" / "controllers" / "billing_controller.py"
        assert controller_file.exists()
        content = controller_file.read_text(encoding="utf-8")
        assert "from src.modules.billing.services import BillingService" not in content
        assert "self.service = service or BillingService()" not in content
        assert "class BillingController" in content
        assert "pass" in content

    @pytest.mark.it("✅  Should inject repository into service when both are selected for module")
    def test_injects_repository_into_service_when_both_selected_for_module(
        self,
        temp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(temp_path)
        modules_root = temp_path / "src" / "modules"

        result = runner.invoke(
            add_app,
            [
                "module",
                "billing",
                "--path",
                str(modules_root),
                "--module-components",
                "service,repository",
            ],
        )

        assert result.exit_code == 0
        service_file = modules_root / "billing" / "services" / "billing_service.py"
        assert service_file.exists()
        content = service_file.read_text(encoding="utf-8")
        assert "from src.modules.billing.repositories import BillingRepository" in content
        assert "def __init__(self, repository: BillingRepository = None)" in content
        assert "self.repository = repository or BillingRepository()" in content

    @pytest.mark.it(
        "✅  Should create service without repository when repository is not selected in module"
    )
    def test_creates_service_without_repository_when_repository_not_selected_in_module(
        self,
        temp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(temp_path)
        modules_root = temp_path / "src" / "modules"

        result = runner.invoke(
            add_app,
            [
                "module",
                "billing",
                "--path",
                str(modules_root),
                "--module-components",
                "service",
            ],
        )

        assert result.exit_code == 0
        service_file = modules_root / "billing" / "services" / "billing_service.py"
        assert service_file.exists()
        content = service_file.read_text(encoding="utf-8")
        assert "from src.modules.billing.repositories import BillingRepository" not in content
        assert "self.repository = repository or BillingRepository()" not in content
        assert "class BillingService" in content
        assert "pass" in content

    @pytest.mark.it("✅  Should inject entity into repository when both are selected for module")
    def test_injects_entity_into_repository_when_both_selected_for_module(
        self,
        temp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(temp_path)
        modules_root = temp_path / "src" / "modules"

        result = runner.invoke(
            add_app,
            [
                "module",
                "billing",
                "--path",
                str(modules_root),
                "--module-components",
                "repository,entity",
            ],
        )

        assert result.exit_code == 0
        repository_file = modules_root / "billing" / "repositories" / "billing_repository.py"
        assert repository_file.exists()
        content = repository_file.read_text(encoding="utf-8")
        assert "from src.modules.billing.entities import Billing" in content
        assert "class BillingRepository(AsyncBaseRepository[Billing])" in content
        assert "super().__init__(Billing)" in content

    @pytest.mark.it(
        "✅  Should create repository without entity when entity is not selected in module"
    )
    def test_creates_repository_without_entity_when_entity_not_selected_in_module(
        self,
        temp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(temp_path)
        modules_root = temp_path / "src" / "modules"

        result = runner.invoke(
            add_app,
            [
                "module",
                "billing",
                "--path",
                str(modules_root),
                "--module-components",
                "repository",
            ],
        )

        assert result.exit_code == 0
        repository_file = modules_root / "billing" / "repositories" / "billing_repository.py"
        assert repository_file.exists()
        content = repository_file.read_text(encoding="utf-8")
        assert "from src.modules.billing.entities import Billing" not in content
        assert "class BillingRepository:" in content
        assert "pass" in content

    @pytest.mark.it("✅  Should create only selected module components")
    def test_creates_only_selected_module_components(
        self,
        temp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(temp_path)
        modules_root = temp_path / "src" / "modules"

        result = runner.invoke(
            add_app,
            [
                "module",
                "billing",
                "--path",
                str(modules_root),
                "--module-components",
                "entity,service",
            ],
        )

        assert result.exit_code == 0
        assert (modules_root / "billing" / "entities" / "__init__.py").exists()
        assert (modules_root / "billing" / "entities" / "billing_entity.py").exists()
        assert (modules_root / "billing" / "services" / "billing_service.py").exists()
        assert not (modules_root / "billing" / "controllers").exists()
        assert not (modules_root / "billing" / "repositories").exists()

    @pytest.mark.it("✅  Should ask module components when option is not provided")
    def test_asks_module_components_when_option_is_not_provided(
        self,
        temp_path: Path,
        mocker,
        monkeypatch: pytest.MonkeyPatch,
    ):
        monkeypatch.chdir(temp_path)
        modules_root = temp_path / "src" / "modules"

        mock_checkbox = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_module_helper.questionary.checkbox"
        )
        mock_checkbox.return_value.ask.return_value = ["controller", "entity"]
        mock_confirm = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_controller_helper.questionary.confirm"
        )
        mock_confirm.return_value.ask.return_value = False

        result = runner.invoke(add_app, ["module", "sales", "--path", str(modules_root)])

        assert result.exit_code == 0
        assert (modules_root / "sales" / "entities" / "sales_entity.py").exists()
        assert (modules_root / "sales" / "controllers" / "sales_controller.py").exists()

    @pytest.mark.it("❌  Should fail when module component is invalid")
    def test_fails_when_module_component_is_invalid(self, temp_path: Path):
        result = runner.invoke(
            add_app,
            [
                "module",
                "sales",
                "--path",
                str(temp_path),
                "--module-components",
                "invalid",
            ],
        )

        assert result.exit_code == 1
        assert "Invalid module component" in result.output

    @pytest.mark.it("❌  Should fail when module has no selected components")
    def test_fails_when_module_has_no_selected_components(
        self,
        temp_path: Path,
        mocker,
    ):
        mock_checkbox = mocker.patch(
            "fastgear_cli.cli.commands.helpers.add_module_helper.questionary.checkbox"
        )
        mock_checkbox.return_value.ask.return_value = []

        result = runner.invoke(add_app, ["module", "sales", "--path", str(temp_path)])

        assert result.exit_code == 1
        assert "At least one component is required for module." in result.output

    @pytest.mark.it("❌  Should fail when module-components is used with non-module element")
    def test_fails_when_module_components_used_with_non_module(self, temp_path: Path):
        result = runner.invoke(
            add_app,
            [
                "entity",
                "sales",
                "--path",
                str(temp_path),
                "--module-components",
                "entity",
            ],
        )

        assert result.exit_code == 1
        assert "--module-components can only be used with element type module." in result.output
