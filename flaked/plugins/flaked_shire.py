# -*- coding: utf-8 -*-
from ast import NodeVisitor

__version__ = "0.1.4"

SHIRE_MODULES = ("luz", "luzong", "corelib")

MESSAGE = "SH00 shire old style import found"


class ShireImportVisitor(NodeVisitor):
    def __init__(self):
        super(ShireImportVisitor, self).__init__()
        self.imports = []

    def visit_ImportFrom(self, node):
        n_modules = node.module.split(".") if node.module else []
        if len(set(n_modules).intersection(SHIRE_MODULES)) > 0:
            self.imports.append(node)

    def visit_Import(self, node):
        for n_name in node.names:
            if n_name.name in SHIRE_MODULES:
                self.imports.append(node)


class ShireChecker:
    name = "flaked-shire"
    version = __version__

    def __init__(self, tree, filename):
        self.tree = tree
        self.filename = filename

    def run(self):
        visitor = ShireImportVisitor()
        visitor.visit(self.tree)
        if not visitor.imports:
            return

        for import_node in visitor.imports:
            yield (
                import_node.lineno,
                0,
                MESSAGE,
                type(self),
            )
