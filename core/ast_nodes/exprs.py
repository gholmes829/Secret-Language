"""

"""

import lark
from icecream import ic
from pydot import Node

from core.ast_nodes.node import ASTNode, NodeList
from core.ast_nodes.types import ClassType, FnType, ObjectType


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
    ops = {
        '!': (lambda opd: not opd, 'l_not'),
        '-': (lambda opd: -opd, 'negate'),
    }

    def __init__(self, meta, operation, operand) -> None:
        super().__init__(meta)
        self.op_str = operation
        self.operand = operand
        self.op, self.name = UnaryOp.ops[operation]
        self.opd_cast, self.res_cast = None, None
    
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
        'and': (lambda lhs, rhs: lhs and rhs, 'l_and'),
        'or': (lambda lhs, rhs: lhs or rhs, 'l_or'),
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

    def __init__(self, meta, lhs, op_str, rhs) -> None:
        super().__init__(meta)
        self.op_str = op_str
        self.lhs, self.rhs = lhs, rhs
        self.op, self.op_name = BinOp.ops[op_str]
        self.lhs_cast, self.rhs_cast, self.res_cast = None, None, None


    def accept(self, visitor, *args, **kwargs):
        return visitor.visitBinOp(self, *args, **kwargs)

# fn calls
class Call(Expr):
    def __init__(self, meta, name, actuals) -> None:
        super().__init__(meta)
        self.name = name
        self.actuals = NodeList(meta, list(filter(lambda arg: arg, actuals)), 'actuals')
        if isinstance(self.actuals, NodeList) and len(self.actuals) == 1 and isinstance(self.actuals[0], NodeList):
            self.actuals = self.actuals[0]

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitCall(self, *args, **kwargs)

    def __repr__(self):
        return f'<CallNode "{self.name}" w/ {len(self.actuals)} actuals at {id(self)} >'


# references
class Reference(Expr):
    dot_node_kwargs = Expr.dot_node_kwargs | dict(fillcolor='lightgoldenrod', shape='rectangle')
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

class ID(Reference):
    def __init__(self, meta, id_token, **kwargs) -> None:
        super().__init__(meta)
        assert not isinstance(id_token, ID), ic(id_token, id_token.name)
        self.name = id_token
        self.mods = kwargs

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitID(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<ID "{self.name}" at {id(self)}>'

class ScopedID(Reference):
    def __init__(self, meta, name, object, id_tokens) -> None:
        super().__init__(meta)
        self.name = name
        self.object = object
        self.components = id_tokens

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitScopedID(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<ScopedID "{self.name}" at {id(self)}>'

class ThisID(Reference):
    def __init__(self, meta, name, object, id_tokens) -> None:
        super().__init__(meta)
        self.name = name
        self.object = object
        assert object.name == 'this'
        self.components = id_tokens

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitThisID(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<ThisID at {id(self)}>'

# object values
class Object(Expr):
    def __init__(self, meta, obj_type) -> None:
        super().__init__(meta)
        self.type = obj_type

    def accept(self, visitor, *args, **kwargs):
        raise NotImplementedError


class FnObj(Object):  # inherit from new Obj (differentiate primative from obj maybe)
    def __init__(self, meta, decorator, generics, mutability_mod, scope_mod, ret_type, formals, body) -> None:
        super().__init__(meta, FnType(meta, mutability_mod, scope_mod, ret_type, [formal.type for formal in (formals or [])]))
        self.identifier = str(id(self))
        self.generics = generics
        self.mutability_mod = mutability_mod
        self.scope_mod = scope_mod
        self.decorator = decorator
        self.formals = formals or []
        self.body = body

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFnObj(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<"fn_obj" at {id(self)}>'


class MethodObj(Object):
    def __init__(self, meta, decorator, generics, mutability_mod, scope_mod, ret_type, formals, body) -> None:
        super().__init__(meta, FnType(meta, mutability_mod, scope_mod, ret_type, [formal.type for formal in (formals or [])]))
        self.identifier = str(id(self))
        self.generics = generics
        self.mutability_mod = mutability_mod
        self.scope_mod = scope_mod
        self.decorator = decorator
        self.formals = formals or []
        self.body = body

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitMethodObj(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<"method_obj" at {id(self)}>'

class ClassObj(Object):
    def __init__(self, meta, decorator, generics, id_, inheritance, cls_assignments):
        super().__init__(meta, ClassType(meta, id_))
        self.decorator = decorator
        self.generics = generics
        self.name = id_
        self.inheritance = inheritance
        self.body = cls_assignments

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitClassObj(self, *args, **kwargs)


# literals
class Literal(Expr):
    dot_node_kwargs = Expr.dot_node_kwargs | dict(fillcolor='lightgreen', shape='diamond')
    def __init__(self, token, value, lit_type) -> None:
        super().__init__(token)
        self.value = value
        self.type = lit_type

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitLiteral(self, *args, **kwargs)

    def __repr__(self):
        return f'<"{__class__}" obj w/ val = "{self.value}" at {id(self)}>'

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
        return visitor.visitNone(self, *args, **kwargs)