import pytest

from fastgear_cli.core.utils.init_content_merge_utils import (
    convert_lines_to_content,
    ensure_import_line,
    merge_required_line,
    merge_symbol_list_assignment,
    parse_symbol_list_assignment,
)


@pytest.mark.describe("🧪  ConvertLinesToContent")
class TestConvertLinesToContent:
    @pytest.mark.it("✅  Should return empty string for empty list")
    def test_return_empty_string_for_empty_list(self):
        result = convert_lines_to_content([])

        assert result == ""

    @pytest.mark.it("✅  Should join lines with newline and trailing newline")
    def test_join_lines_with_trailing_newline(self):
        result = convert_lines_to_content(["from .foo import Bar", "", "__all__ = ['Bar']"])

        assert result == "from .foo import Bar\n\n__all__ = ['Bar']\n"

    @pytest.mark.it("✅  Should strip trailing whitespace from last line")
    def test_strip_trailing_whitespace(self):
        result = convert_lines_to_content(["line1", "line2   "])

        assert result == "line1\nline2\n"


@pytest.mark.describe("🧪  EnsureImportLine")
class TestEnsureImportLine:
    @pytest.mark.it("✅  Should return unchanged lines when import already exists")
    def test_return_unchanged_when_import_exists(self):
        lines = ["from .foo import Bar", "", "x = 1"]

        result = ensure_import_line(lines.copy(), "from .foo import Bar")

        assert "from .foo import Bar" in result
        assert result.count("from .foo import Bar") == 1

    @pytest.mark.it("✅  Should insert import after existing imports")
    def test_insert_import_after_existing_imports(self):
        lines = ["from .foo import Bar", "", "x = 1"]

        result = ensure_import_line(lines.copy(), "from .baz import Qux")

        assert "from .baz import Qux" in result
        baz_idx = result.index("from .baz import Qux")
        x_idx = result.index("x = 1")
        assert baz_idx < x_idx

    @pytest.mark.it("✅  Should insert import at beginning when no imports exist")
    def test_insert_import_at_beginning_when_no_imports(self):
        lines = ["x = 1", "y = 2"]

        result = ensure_import_line(lines.copy(), "from .foo import Bar")

        assert result[0] == "from .foo import Bar"


@pytest.mark.describe("🧪  MergeRequiredLine")
class TestMergeRequiredLine:
    @pytest.mark.it("✅  Should return unchanged content when line already exists")
    def test_return_unchanged_when_line_exists(self):
        content = "from .foo import Bar\nx = 1\n"

        result = merge_required_line(current=content, required_line="x = 1")

        assert result == content

    @pytest.mark.it("✅  Should insert import line into import section")
    def test_insert_import_line(self):
        content = "from .foo import Bar\n\nx = 1\n"

        result = merge_required_line(
            current=content,
            required_line="from .baz import Qux",
        )

        assert "from .baz import Qux" in result
        assert "from .foo import Bar" in result

    @pytest.mark.it("✅  Should append non-import line at end when no anchor")
    def test_append_non_import_line_at_end(self):
        content = "x = 1\n"

        result = merge_required_line(current=content, required_line="y = 2")

        assert result.endswith("y = 2\n")

    @pytest.mark.it("✅  Should insert line after anchor when anchor exists")
    def test_insert_line_after_anchor(self):
        content = "router = APIRouter()\nrouter.include_router(foo_router)\n"

        result = merge_required_line(
            current=content,
            required_line="router.include_router(bar_router)",
            anchor_line="router = APIRouter()",
        )

        lines = result.splitlines()
        anchor_idx = lines.index("router = APIRouter()")
        assert lines[anchor_idx + 1] == "router.include_router(bar_router)"

    @pytest.mark.it("✅  Should append line when anchor is not found")
    def test_append_line_when_anchor_not_found(self):
        content = "x = 1\n"

        result = merge_required_line(
            current=content,
            required_line="y = 2",
            anchor_line="missing_anchor = True",
        )

        assert "y = 2" in result


@pytest.mark.describe("🧪  MergeSymbolListAssignment")
class TestMergeSymbolListAssignment:
    @pytest.mark.it("✅  Should add symbol to existing list assignment")
    def test_add_symbol_to_existing_list(self):
        content = "billing_entities = [Billing]\n"

        result = merge_symbol_list_assignment(
            current=content,
            list_name="billing_entities",
            symbol_name="Invoice",
        )

        assert "billing_entities = [Billing, Invoice]" in result

    @pytest.mark.it("✅  Should not duplicate symbol in existing list")
    def test_not_duplicate_symbol(self):
        content = "billing_entities = [Billing]\n"

        result = merge_symbol_list_assignment(
            current=content,
            list_name="billing_entities",
            symbol_name="Billing",
        )

        assert result.count("Billing") == 1

    @pytest.mark.it("✅  Should create new list assignment when none exists")
    def test_create_new_list_assignment(self):
        content = "x = 1\n"

        result = merge_symbol_list_assignment(
            current=content,
            list_name="entities",
            symbol_name="Customer",
        )

        assert "entities = [Customer]" in result

    @pytest.mark.it("✅  Should handle multiline list assignment")
    def test_handle_multiline_list_assignment(self):
        content = "billing_entities = [\n    Billing\n]\n"

        result = merge_symbol_list_assignment(
            current=content,
            list_name="billing_entities",
            symbol_name="Invoice",
        )

        assert "Billing" in result
        assert "Invoice" in result


@pytest.mark.describe("🧪  ParseSymbolListAssignment")
class TestParseSymbolListAssignment:
    @pytest.mark.it("✅  Should parse valid assignment with symbols")
    def test_parse_valid_assignment(self):
        result = parse_symbol_list_assignment("billing_entities = [Billing, Invoice]")

        assert result is not None
        list_name, symbols = result
        assert list_name == "billing_entities"
        assert symbols == ["Billing", "Invoice"]

    @pytest.mark.it("✅  Should parse assignment with single symbol")
    def test_parse_single_symbol(self):
        result = parse_symbol_list_assignment("entities = [Customer]")

        assert result is not None
        list_name, symbols = result
        assert list_name == "entities"
        assert symbols == ["Customer"]

    @pytest.mark.it("✅  Should parse assignment with empty list")
    def test_parse_empty_list(self):
        result = parse_symbol_list_assignment("entities = []")

        assert result is not None
        list_name, symbols = result
        assert list_name == "entities"
        assert symbols == []

    @pytest.mark.it("✅  Should return None for non-assignment lines")
    @pytest.mark.parametrize(
        "line",
        [
            "from .foo import Bar",
            "router.include_router(bar_router)",
            "# a comment",
            "",
        ],
    )
    def test_return_none_for_non_assignment(self, line: str):
        result = parse_symbol_list_assignment(line)

        assert result is None
