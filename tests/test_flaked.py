# -*- coding: utf-8 -*-
import argparse
import sys

import flake8
import mock
import pytest
from flake8.plugins.manager import LOG

import flaked
from flaked import DFileChecker, parse_mako

mako_source = [
    (
        """
<%!
  from static import static, istatic
  from corelib.cdn import image_url
  from socket import gethostname
%>
<%def name="footer()">
  <div id="footer">
    <%include file="/widgets/footer.html"/>
  </div>
</%def>
"""
    ),
]


@pytest.mark.parametrize("source", mako_source)
def test_parse_mako(source):
    mako_imports = parse_mako(source)
    assert all(["from" or "import" in impo for impo in mako_imports])


# copy test case from flake8 tests/*


def options(**kwargs):
    """Generate argparse.Namespace for our Application."""
    kwargs.setdefault("verbose", 0)
    kwargs.setdefault("output_file", None)
    kwargs.setdefault("count", False)
    kwargs.setdefault("exit_zero", False)
    return argparse.Namespace(**kwargs)


@pytest.fixture
def application():
    """Create an application."""
    return flaked.Application()


@pytest.mark.parametrize(
    "result_count, catastrophic, exit_zero, value",
    [
        (0, False, False, False),
        (0, True, False, True),
        (2, False, False, True),
        (2, True, False, True),
        (0, True, True, True),
        (2, False, True, False),
        (2, True, True, True),
    ],
)
def test_exit_does_raise(result_count, catastrophic, exit_zero, value, application):
    """Verify Application.exit doesn't raise SystemExit."""
    application.result_count = result_count
    application.catastrophic_failure = catastrophic
    application.options = options(exit_zero=exit_zero)

    with pytest.raises(SystemExit) as excinfo:
        application.exit()

    assert excinfo.value.args[0] is value


def test_returns_specified_plugin(application):
    """Verify we get the plugin we want."""
    desired = mock.Mock()
    execute = desired.execute
    application.formatting_plugins = {
        "default": mock.Mock(),
        "desired": desired,
    }

    with mock.patch.object(LOG, "warning") as warning:
        assert execute is application.formatter_for("desired")

    assert warning.called is False


def test_prelim_opts_args(application):
    """Verify we get sensible prelim opts and args."""
    opts, args = application.parse_preliminary_options(
        ["--foo", "--verbose", "src", "setup.py", "--statistics", "--version"]
    )

    assert opts.verbose
    assert args == ["--foo", "src", "setup.py", "--statistics", "--version"]


def test_prelim_opts_ignore_help(application):
    """Verify -h/--help is not handled."""
    # GIVEN

    # WHEN
    _, args = application.parse_preliminary_options(["--help", "-h"])

    # THEN
    assert args == ["--help", "-h"]


def test_prelim_opts_handles_empty(application):
    """Verify empty argv lists are handled correctly."""
    irrelevant_args = ["myexe", "/path/to/foo"]
    with mock.patch.object(sys, "argv", irrelevant_args):
        opts, args = application.parse_preliminary_options([])

        assert args == []


@mock.patch("flake8.checker.FileChecker._make_processor", return_value=None)
def test_repr(*args):
    """Verify we generate a correct repr."""
    file_checker = DFileChecker(
        "example.py",
        checks={},
        options=object(),
    )
    assert repr(file_checker) == "FileChecker for example.py"


def test_nonexistent_file():
    """Verify that checking non-existent file results in an error."""
    c = DFileChecker("foobar.py", checks={}, options=object())

    assert c.processor is None
    assert not c.should_process
    assert len(c.results) == 1
    error = c.results[0]
    assert error[0] == "E902"


def test_raises_exception_on_failed_plugin(tmp_path, default_options):
    """Checks that a failing plugin results in PluginExecutionFailed."""
    foobar = tmp_path / "foobar.py"
    foobar.write_text("I exist!")  # Create temp file
    plugin = {
        "name": "failure",
        "plugin_name": "failure",  # Both are necessary
        "parameters": dict(),
        "plugin": mock.MagicMock(side_effect=ValueError),
    }
    """Verify a failing plugin results in an plugin error"""
    fchecker = DFileChecker(str(foobar), checks=[], options=default_options)
    with pytest.raises(flake8.exceptions.PluginExecutionFailed):
        fchecker.run_check(plugin)
