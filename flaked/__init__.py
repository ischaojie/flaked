# -*- coding: utf-8 -*-
import argparse
import os
import time

from flake8.checker import LOG, FileChecker, Manager
from flake8.main import options
from flake8.main.application import Application as Flake8Application
from flake8.options import manager
from flake8.processor import FileProcessor
from pygments import lex
from pygments.lexers import MakoLexer
from pygments.token import string_to_tokentype

__version__ = "0.1.0"


def is_import_start(token, value):
    return token == string_to_tokentype("Token.Comment.Preproc") and value == "<%!"


def is_import_end(token, value):
    return token == string_to_tokentype("Token.Comment.Preproc") and value == "%>"


def parse_mako(source):
    imports_section = []
    tokens = lex(source, MakoLexer())

    is_import = False
    for token, value in tokens:
        if is_import_start(token, value):
            is_import = True
            continue
        if is_import_end(token, value):
            break

        if is_import:
            imports_section.append(value)

    # TODO: maybe better
    imports_section = "".join(imports_section).strip().split("\n")
    return [imp.strip() + "\n" for imp in imports_section]


def parse_file(filename, source):
    mako_ext = [".mako", ".html"]
    _, ext = os.path.splitext(filename)
    return parse_mako(source) if ext in mako_ext else ""


# TODO: multiple files not work
class DManager(Manager):
    def make_checkers(self, paths=None):
        super(DManager, self).make_checkers(paths)

        new_checkers = []
        for checker in self.checkers:
            # parse file: if mako file then return python code lines
            source = "".join(checker.processor.read_lines())
            mako_lines = parse_file(checker.filename, source)
            _checker = DFileChecker(
                checker.filename,
                checker.checks,
                self.options,
                mako_lines=mako_lines,
            )
            new_checkers.append(_checker)

        self.checkers = new_checkers
        self._all_checkers = new_checkers
        LOG.info("Checking %s files", len(self.checkers))


class DFileChecker(FileChecker):
    def __init__(self, filename, checks, options, mako_lines=None):
        self.mako_lines = mako_lines
        super(DFileChecker, self).__init__(filename, checks, options)

    def _make_processor(self):
        try:
            return FileProcessor(self.filename, self.options, lines=self.mako_lines)
        except IOError as e:
            message = "{0}: {1}".format(type(e).__name__, e)
            self.report("E902", 0, 0, message)
            return


class Application(Flake8Application):
    def __init__(self, program="flaked", version=__version__):
        self.start_time = time.time()
        self.end_time = None
        self.program = program
        self.version = version
        self.prelim_arg_parser = argparse.ArgumentParser(add_help=False)
        options.register_preliminary_options(self.prelim_arg_parser)

        self.option_manager = manager.OptionManager(
            prog=program,
            version=version,
            parents=[self.prelim_arg_parser],
        )
        options.register_default_options(self.option_manager)

        self.check_plugins = None
        self.formatting_plugins = None
        self.formatter = None
        self.guide = None
        self.file_checker_manager = None
        self.options = None
        self.args = None
        self.result_count = 0
        self.total_result_count = 0
        self.catastrophic_failure = False
        self.running_against_diff = False
        self.parsed_diff = {}

    def make_file_checker_manager(self):
        self.file_checker_manager = DManager(
            style_guide=self.guide,
            arguments=self.args,
            checker_plugins=self.check_plugins,
        )
