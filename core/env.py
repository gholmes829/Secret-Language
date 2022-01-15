"""

"""

import abc
from icecream import ic

class SemSymbol(metaclass = abc.ABCMeta):
    def __init__(self) -> None:
        pass


class VarSymbol(SemSymbol):
    def __init__(self, name, var_type) -> None:
        super().__init__()
        self.name = name
        self.type = var_type
        self.value = None


class FnSymbol(SemSymbol):
    def __init__(self, identifier, ret_type, body, formals) -> None:
        super().__init__()
        self.identifier = identifier
        self.ret_type = ret_type
        self.body = body
        self.formals = formals
        self.formal_types = [formal.type for formal in formals]


class ScopeTable:
    def __init__(self, name, prev_scope) -> None:
        self.name = name
        self.prev_scope = prev_scope
        self.depth = prev_scope.depth + 1 if prev_scope else 0
        self.chain_name = prev_scope.chain_name + f'.{name}' if prev_scope else name
        self.table = {}

    def add_primitive(self, name, var_type):
        sym = VarSymbol(name, var_type)
        self.table[name] = sym
        return sym

    def add_fn(self, identifier, ret_type, body, formals):
        sym = FnSymbol(identifier, ret_type, body, formals)
        self.table[identifier] = sym
        return sym

    def __getitem__(self, key):
        return self.table[key]

    def __contains__(self, key):
        return key in self.table

    def __repr__(self):
        return f'<{self.chain_name} -> {repr(self.table)}>'


class SymbolTable:
    def __init__(self) -> None:
        self.curr_scope = None
        self.symbols = {}

    def enter_scope(self, scope_name):
        self.curr_scope = ScopeTable(scope_name, self.curr_scope)
        return self

    def leave_scope(self):
        self.curr_scope = self.curr_scope.prev_scope
        
    def add_primitive(self, name, var_type):
        sym = self.curr_scope.add_primitive(name, var_type)
        self.symbols[self.curr_scope.chain_name + f'.{name}'] = sym
        return sym

    def add_fn(self, identifier, ret_type, body, formals):
        sym = self.curr_scope.add_fn(identifier, ret_type, body, formals)
        self.symbols[self.curr_scope.chain_name + f'.{identifier}'] = sym
        return sym

    def __getitem__(self, key):
        tmp_scope = self.curr_scope
        while tmp_scope:
            try:
                return tmp_scope[key]
            except KeyError:
                tmp_scope = tmp_scope.prev_scope

    def __contains__(self, key):
        tmp_scope = self.curr_scope
        while tmp_scope:
            if key in tmp_scope:
                return True
            tmp_scope = tmp_scope.prev_scope

    def __enter__(self) -> None:
        return self

    def __exit__(self, *_: list) -> None:
        self.leave_scope()

    def __repr__(self) -> str:
        scopes = []
        tmp_scope = self.curr_scope

        while tmp_scope:
            scopes.append(repr(tmp_scope))
            tmp_scope = tmp_scope.prev_scope
        joined = ", ".join(reversed(scopes))
        return f'<scopes -> [{joined}]>'