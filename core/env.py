"""

"""

# add fixed hook to access globals
# rethink fn definition: num fn(num a) { return a * 2 } === var fn = (num a) => { return a } 
# ^ in other words, leverage function object-ness
# for fn calls, each fn call gets own env to protect recursions
# need to add None type

import abc

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
    def __init__(self, name, formal_types, ret_type, body, formals) -> None:
        super().__init__()
        self.name = name
        self.formal_types = formal_types
        self.ret_type = ret_type
        self.body = body
        self.formals = formals


class ClsSymbol(SemSymbol):
    def __init__(self, name, ret_type) -> None:
        super().__init__()
        self.name = name
        self.ret_type = ret_type


class ScopeTable:
    def __init__(self, name) -> None:
        self.name = name
        self.table = {}

    def add_var(self, name, var_type):
        sym = VarSymbol(name, var_type)
        self.table[name] = sym
        return sym

    def add_fn(self, name, formal_types, ret_type, body, formals):
        sym = FnSymbol(name, formal_types, ret_type, body, formals)
        self.table[name] = sym
        return sym

    def add_cls(self, name, ret_type):
        sym = ClsSymbol(name, ret_type)
        self.table[name] = sym
        return sym

    def __getitem__(self, key):
        return self.table[key]

    def __contains__(self, key):
        return key in self.table


class SymbolTable:
    def __init__(self) -> None:
        self.symbols = {}
        self.table_chain = []  # global scope
        self.chain_path = ()

    def enter_scope(self, scope_name):
        self.table_chain.append(ScopeTable(scope_name))
        self.chain_path += (scope_name,)

    def leave_scope(self):
        self.table_chain.pop()
        self.chain_path = self.chain_path[:-1]

    def get_current_scope(self):
        return self.table_chain[-1]

    def add_var(self, name, var_type):
        sym = self.get_current_scope().add_var(name, var_type)
        self.symbols[self.chain_path + (str(name),)] = sym
        return sym

    def add_fn(self, name, formal_types, ret_type, body, formals):
        sym = self.get_current_scope().add_fn(name, formal_types, ret_type, body, formals)
        self.symbols[self.chain_path + (str(name),)] = sym
        return sym

    def add_cls(self, name, ret_type):
        sym = self.get_current_scope().add_cls(name, ret_type)
        self.symbols[self.chain_path + (str(name),)] = sym
        return sym

    def __getitem__(self, key):
        for scope in self.table_chain:
            if key in scope.table:
                return scope.table[key]
        if key in self.symbols:
            return self.symbols[key]
        raise KeyError

    def __contains__(self, key):
        for scope in self.table_chain:
            if key in scope.table:
                return True
        raise KeyError