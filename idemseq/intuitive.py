import ast

import collections

from idemseq.base import FunctionWrapper, Empty
from idemseq.inspector import Inspector


class IntuitiveModuleParser(ast.NodeVisitor):
    def __init__(self, mod):
        super(IntuitiveModuleParser, self).__init__()
        self.mod = mod

        # Includes private functions
        self.all_functions = collections.OrderedDict()

        # Includes dependencies of private functions
        self.all_dependencies = collections.OrderedDict()

    def visit_FunctionDef(self, node):
        func = FunctionWrapper(getattr(self.mod, node.name))
        self.all_functions[node.name] = func

        for name, default in func.get_dependencies():
            if name not in self.all_dependencies:
                self.all_dependencies[name] = None


class IntuitiveModuleInterpreter(Inspector):
    """
    A module consists of a list of functions.
    
    Functions that start with "_" are private and are never exposed via CLI.
    
    In public functions, arguments that don't have default values provided are considered dependencies 
    that need to be provided either by other functions of the module or by user via command-line options.
    
    Functions that are called <x>(), get_<x>, _<x>, or _get_<x> where <x> is name of a dependency, are
    treated as providers and will be called once per script execution to generate value of x that is then
    added to the context and passed to whoever needs it (mentions it in arguments).
    
    Parameters with default value None are still considered as dependencies, but if no injector is found,
    they become an optional command line option with default value of None.
    """

    def __init__(self, *args, **kwargs):
        super(IntuitiveModuleInterpreter, self).__init__(*args, **kwargs)
        self._parser = IntuitiveModuleParser(self.mod)
        self._parser.visit(self.ast)

    def get_public_functions(self):
        all_providers = collections.OrderedDict()

        for name in self.parser.all_dependencies.keys():
            provider_names = (
                name,
                'get_{}'.format(name),
                '_{}'.format(name),
                '_get_{}'.format(name),
            )
            for p_name in provider_names:
                if p_name in self.parser.all_functions:
                    self.parser.all_dependencies[name] = self.parser.all_functions[p_name]
                    all_providers[p_name] = self.parser.all_functions[p_name]
                    break

        public_functions = []
        for name, func in self.parser.all_functions.items():
            if name not in all_providers:
                public_functions.append(func)

        return public_functions

    def invoke(self):
        all_providers = collections.OrderedDict()

        for name in self.parser.all_dependencies.keys():
            provider_names = (
                name,
                'get_{}'.format(name),
                '_{}'.format(name),
                '_get_{}'.format(name),
            )
            for p_name in provider_names:
                if p_name in self.parser.all_functions:
                    self.parser.all_dependencies[name] = self.parser.all_functions[p_name]
                    all_providers[p_name] = self.parser.all_functions[p_name]
                    break

        public_functions = []
        for name, func in self.parser.all_functions.items():
            if name not in all_providers:
                public_functions.append(func)

        context = {}

        def call_func(f):
            kwargs = {}
            for param_name, param_default in f.get_dependencies():
                if param_name not in context:
                    provider = self.parser.all_dependencies[param_name]
                    if provider:
                        context[param_name] = call_func(provider)
                    else:
                        if param_default is Empty:
                            raise RuntimeError('No provider found for {}'.format(param_name))
                kwargs[param_name] = context.get(param_name, param_default)
            return f(**kwargs)

        for func in public_functions:
            call_func(func)


inspector = IntuitiveModuleInterpreter('idemseq.examples.intuitive_interpretation')
print(inspector)

print(inspector.parser.all_functions)
print(inspector.parser.all_dependencies)

print(inspector.get_public_functions())

inspector.invoke()
