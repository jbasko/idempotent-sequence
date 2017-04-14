import ast
import collections
import functools
import importlib
import logging
import types

from idemseq.base import FunctionWrapper, Empty

log = logging.getLogger(__name__)


class Module(object):
    """
    
    a module consists of:
        * exposed_functions -- an ordered collection of functions that 
          can be invoked individually and sequentially
        * providers -- a collection of functions that fulfill dependencies
        * dependencies -- a mapping of names of dependencies to providers that fulfill them
    
    """

    _context_class = dict

    class AstVisitor(ast.NodeVisitor):
        def __init__(self, **callbacks):
            for k, v in callbacks.items():
                setattr(self, k, v)

    def __init__(self, module_or_name, context=None):
        self._mod = None
        if isinstance(module_or_name, types.ModuleType):
            self._mod = module_or_name
            self._mod_name = self._mod.__name__
        else:
            self._mod_name = module_or_name
            self._mod = importlib.import_module(self._mod_name)
        self._mod_filename = self._mod.__file__

        self._all_functions = collections.OrderedDict()
        self._exposed_functions = []
        self._providers = collections.OrderedDict()
        self._dependencies = collections.OrderedDict()

        # Wrappers around the original functions.
        # These wrappers are called with no args or kwargs.
        # Args and kwargs passed to the original functions are taken
        # from context or generated on the fly using the declared providers.
        self._executables = {}

        self._context = context or self._context_class()

        self._load()

    def __getattr__(self, item):
        if item in self._exposed_functions:
            return self._get_executable(self._all_functions[item])
        else:
            raise AttributeError(item)

    def _load(self):
        if self._all_functions:
            raise RuntimeError('Module already loaded')

        def register_function_definition(node):
            func = FunctionWrapper(getattr(self._mod, node.name))
            self._all_functions[node.name] = func
            for dep_name, dep_default in func.get_dependencies():
                if dep_name not in self._dependencies:
                    self._dependencies[dep_name] = None

        visitor = self.AstVisitor(visit_FunctionDef=register_function_definition)
        with open(self._mod_filename) as f:
            visitor.visit(ast.parse(f.read(), filename=self._mod_filename))

        for dep_name in self._dependencies.keys():
            provider_names = (
                dep_name,
                'get_{}'.format(dep_name),
                '_{}'.format(dep_name),
                '_get_{}'.format(dep_name),
            )
            for provider_name in provider_names:
                if provider_name in self._all_functions:
                    if self._dependencies[dep_name]:
                        log.warning(
                            'More than one provider detected for {}, '
                            'ignoring {}'.format(dep_name, provider_name)
                        )
                        continue
                    self._dependencies[dep_name] = self._all_functions[provider_name]
                    self._providers[provider_name] = self._all_functions[provider_name]

        for func_name, func in self._all_functions.items():
            if func_name not in self._providers and not func_name.startswith('_'):
                self._exposed_functions.append(func_name)

    def _get_executable(self, func):
        if func.name not in self._executables:
            self._executables[func.name] = self._create_executable(func)
        return self._executables[func.name]

    def _create_executable(self, func):
        assert isinstance(func, FunctionWrapper)

        @functools.wraps(func)
        def executable():
            kwargs = {}

            for dep_name, dep_default in func.get_dependencies():
                if dep_name not in self._context:
                    provider = self._dependencies[dep_name]
                    if provider:
                        self._context[dep_name] = self._get_executable(provider)()

                dep_value = self._context.get(dep_name, dep_default)
                if dep_value is not Empty:
                    kwargs[dep_name] = dep_value

            return func(**kwargs)

        return executable
