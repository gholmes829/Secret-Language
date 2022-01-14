"""

"""

import lark

from core.ast_nodes.node import ASTNode

# expressions
class Expr(ASTNode):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._value = None
        self._type = None

    def make_pydot_node(self, *args, **kwargs):
        if 'fillcolor' not in kwargs:
            kwargs['fillcolor'] = 'darksalmon'
        return super().make_pydot_node(*args, **kwargs)

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


# references
class Reference(Expr):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='lightgoldenrod', shape='rectangle', **kwargs)

class ID(Reference):
    def __init__(self, name) -> None:
        super().__init__(None, None)
        self.name = name
        self.symbol = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitID(self, *args, **kwargs)

    @property
    def value(self):
        return self.symbol.value

    @value.setter
    def value(self, _value):
        self.symbol.value = _value

class BinaryOperation(Expr):
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

    def __init__(self, lhs, op_token, rhs) -> None:
        super().__init__(None, None)
        self.op_str = op_token.value
        self.op, self.op_name = BinaryOperation.ops[op_token.value]
        self.lhs, self.rhs = lhs, rhs

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitBinOp(self, *args, **kwargs)


class Call(Expr):
    def __init__(self, identifier, actuals) -> None:
        super().__init__(None, None)
        self.identifier = identifier
        self.type = None
        self.actuals = actuals.children if actuals else []
        self.values = []

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitCall(self, *args, **kwargs)

    @property
    def value(self):
        return self.values.pop()

    @value.setter
    def value(self, value):
        self.values.append(value)


# literals
class Literal(Expr):
    def __init__(self, token, value, lit_type, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.token = token
        self._value = value
        self._type = lit_type

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitLiteral(self, *args, **kwargs)

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='lightgreen', shape='diamond', **kwargs)

# literals
class NumLit(Literal):
    type = float
    def __init__(self, num_token) -> None:
        super().__init__(num_token, float(num_token.value), float, None, None)

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitNumLit(self, *args, **kwargs)


class StrLit(Literal):
    def __init__(self, string_token: lark.Token) -> None:
        super().__init__(string_token, string_token.value[1:-1], str, None, None)
        self.type = str

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitStrLit(self, *args, **kwargs)


class BoolLit(Literal):
    str_to_val = {
        'true': True,
        'false': False
    }

    def __init__(self, bool_token) -> None:
        value = BoolLit.str_to_val[bool_token.value]
        super().__init__(bool_token, value, bool, None, None)

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitBoolLit(self, *args, **kwargs)