"""

"""

import lark
from icecream import ic

from core.ast_nodes.node import ASTNode
from core.ast_nodes.types import FnType


class Expr(ASTNode):
    dot_node_kwargs = ASTNode.dot_node_kwargs | dict(fillcolor='darksalmon')
    def __init__(self, meta) -> None:
        super().__init__(meta)
        self._value = None
        self._type = None

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, _value):
        self._value = _value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type


# operations
class UnaryOp(Expr):
    def __init__(self, meta, operation, operand) -> None:
        super().__init__(meta)
        self.operation = operation
        self.operand = operand
    
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitUnaryOp(self, *args, **kwargs)

class BinOp(Expr):
    ops = {
        '+': (lambda lhs, rhs: lhs + rhs, 'addition'),
        '-': (lambda lhs, rhs: lhs - rhs, 'subtraction'),
        '*': (lambda lhs, rhs: lhs * rhs, 'multiplication'),
        '/': (lambda lhs, rhs: lhs / rhs, 'division'),
        '==': (lambda lhs, rhs: lhs == rhs, 'eq'),
        '!=': (lambda lhs, rhs: lhs != rhs, 'neq'),
        '<': (lambda lhs, rhs: lhs < rhs, 'lt'),
        '<=': (lambda lhs, rhs: lhs <= rhs, 'lte'),
        '>': (lambda lhs, rhs: lhs > rhs, 'gt'),
        '>=': (lambda lhs, rhs: lhs >= rhs, 'gte'),
        'or': (lambda lhs, rhs: lhs or rhs, 'l_or'),
        'and': (lambda lhs, rhs: lhs and rhs, 'l_and'),
    }

    type_resolutions = {
        ('+', float, float): (float, float, float),
        ('+', float, str): (str, str, str),
        ('+', str, str): (str, str, str),
        ('+', str, float): (str, str, str),
        ('-', float, float): (float, float, float),
        ('*', float, float): (float, float, float),
        ('/', float, float): (float, float, float),
        ('>', float, float): (float, float, bool),
        ('>=', float, float): (float, float, bool),
        ('<', float, float): (float, float, bool),
        ('<=', float, float): (float, float, bool),
        ('==', float, float): (float, float, bool),
        ('==', str, str): (str, str, bool),
        ('!=', float, float): (float, float, bool),
        ('and', bool, bool): (bool, bool, bool),
        ('or', bool, bool): (bool, bool, bool),
    }

    def __init__(self, meta, lhs, operation, rhs) -> None:
        super().__init__(meta)
        self.op_str = operation
        self.op, self.op_name = BinOp.ops[operation]
        self.lhs, self.rhs = lhs, rhs

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitBinOp(self, *args, **kwargs)

# fn calls
class Call(Expr):
    def __init__(self, meta, identifier, actuals) -> None:
        super().__init__(meta)
        self.identifier = identifier
        self.actuals = actuals
        self.values = []

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitCall(self, *args, **kwargs)

    @property
    def value(self):
        return self.values.pop()

    @value.setter
    def value(self, value):
        self.values.append(value)


# references
class Reference(Expr):
    dot_node_kwargs = Expr.dot_node_kwargs | dict(fillcolor='lightgoldenrod', shape='rectangle')
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

class ID(Reference):
    def __init__(self, meta, id_token) -> None:
        super().__init__(meta)
        self.name = id_token.value

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitID(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<ID "{self.name}" at {id(self)}>'


# literals
class Literal(Expr):
    dot_node_kwargs = Expr.dot_node_kwargs | dict(fillcolor='lightgreen', shape='diamond')
    def __init__(self, token, value, lit_type) -> None:
        super().__init__(token)
        self.value = value
        self.type = lit_type

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitLiteral(self, *args, **kwargs)

# literals
class NumLit(Literal):
    type = float
    def __init__(self, token) -> None:
        super().__init__(token, float(token), float)

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitNumLit(self, *args, **kwargs)


class StrLit(Literal):
    def __init__(self, token: lark.Token) -> None:
        super().__init__(token, token.value[1:-1], str)

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitStrLit(self, *args, **kwargs)


class BoolLit(Literal):
    token_to_bool = {'true': True, 'false': False}
    def __init__(self, token) -> None:
        super().__init__(token, BoolLit.token_to_bool[token], bool)

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitBoolLit(self, *args, **kwargs)

class None_(Literal):
    def __init__(self, token) -> None:
        super().__init__(token, token, None)

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitNoneLit(self, *args, **kwargs)


# object values
class Object(Expr):
    def __init__(self, meta, obj_type) -> None:
        super().__init__(meta)
        self.type = obj_type

    def accept(self, visitor, *args, **kwargs):
        raise NotImplementedError


class FnObj(Object):  # inherit from new Obj (differentiate primative from obj maybe)
    def __init__(self, meta, decorator, generics, mutability_mod, scope_mod, ret_type, formals, body) -> None:
        super().__init__(meta, FnType(mutability_mod, scope_mod, ret_type, [formal.type for formal in (formals or [])]))
        self.identifier = str(id(self))
        self.generics = generics
        self.mutability_mod = mutability_mod
        self.scope_mod = scope_mod
        self.decorator = decorator
        self.formals = formals
        self.body = body

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFnObj(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<"fn_obj" at {id(self)}>'