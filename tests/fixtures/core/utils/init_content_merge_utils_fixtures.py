import pytest


@pytest.fixture
def empty_content() -> str:
    return ""


@pytest.fixture
def single_import_content() -> str:
    return "from .customer_entity import Customer\n"


@pytest.fixture
def content_with_all_list() -> str:
    return 'from .customer_entity import Customer\n\n__all__ = ["Customer"]\n'


@pytest.fixture
def content_with_symbol_list() -> str:
    return "from .entities import Billing\n\nbilling_entities = [Billing]\n"


@pytest.fixture
def content_with_router() -> str:
    return (
        "from fastapi import APIRouter\n"
        "from .controllers import billing_router\n"
        "\n"
        "billing_module_router = APIRouter()\n"
        "billing_module_router.include_router(billing_router)\n"
    )
