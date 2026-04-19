import pytest
from typer.testing import CliRunner

from fastgear_cli import __version__
from fastgear_cli.cli.app import app

runner = CliRunner()


@pytest.mark.describe("🧪  App")
class TestApp:
    @pytest.mark.it("✅  Should print version with --version flag")
    def test_version_long_flag(self):
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert f"v{__version__}" in result.output

    @pytest.mark.it("✅  Should print version with -v flag")
    def test_version_short_flag(self):
        result = runner.invoke(app, ["-v"])

        assert result.exit_code == 0
        assert f"v{__version__}" in result.output
