import ast
import importlib
import os.path
import types


class Parser(ast.NodeVisitor):
    def __init__(self):
        super(Parser, self).__init__()
        self.functions = []

    def visit_FunctionDef(self, node):
        self.functions.append(node.name)


class Inspector(object):
    def __init__(self, module_or_name):
        self._mod = None
        if isinstance(module_or_name, types.ModuleType):
            self._mod = module_or_name
            self.mod_name = self._mod.__name__
        else:
            self.mod_name = module_or_name
        self._mod_filename = None
        self._ast = None
        self._parser = None

    @property
    def mod_filename(self):
        if self._mod_filename is None:
            direct_path = self.mod_name.replace('.', '/') + '.py'
            if os.path.exists(direct_path):
                self._mod_filename = direct_path
            else:
                self._mod_filename = self.mod.__file__
        return self._mod_filename

    @property
    def mod(self):
        if self._mod is None:
            self._mod = importlib.import_module(self.mod_name)
        return self._mod

    @property
    def ast(self):
        if self._ast is None:
            with open(self.mod_filename) as f:
                self._ast = ast.parse(f.read(), filename=self.mod_filename)
        return self._ast

    @property
    def parser(self):
        if self._parser is None:
            self._parser = Parser()
            self._parser.visit(self.ast)
        return self._parser

    def get_function_names(self):
        return self.parser.functions
