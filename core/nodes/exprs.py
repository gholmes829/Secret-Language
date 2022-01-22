"""

"""

import lark
from icecream import ic
from pydot import Node

from core.nodes.node import ASTNode, NodeList
from core.nodes.types import ClassType, FuncType, ObjectType


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

    type_resolutions = {
        ('!', bool): (bool, bool),
        ('-', float): (float, float)
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
        ('!=', str, str): (str, str, bool),
        ('==', float, float): (float, float, bool),
        ('==', str, str): (str, str, bool),
        ('!=', float, float): (float, float, bool),
        ('and', bool, bool): (bool, bool, bool),
        ('or', bool, bool): (bool, bool, bool),
    }

    def __init__(self, meta, lhs, op_str, rhs) -> None:
        super().__init__(meta)
        self.op_str = str(op_str)
        self.lhs, self.rhs = lhs, rhs
        self.op, self.op_name = BinOp.ops[op_str]
        self.lhs_cast, self.rhs_cast, self.res_cast = None, None, None


    def accept(self, visitor, *args, **kwargs):
        return visitor.visitBinOp(self, *args, **kwargs)

# fn calls
class Call(Expr):
    def __init__(self, meta, ident, actuals) -> None:
        super().__init__(meta)
        self.ident = ident
        self.actuals = NodeList(meta, list(filter(lambda arg: arg, actuals)), 'actuals')
        if isinstance(self.actuals, NodeList) and len(self.actuals) == 1 and isinstance(self.actuals[0], NodeList):
            self.actuals = self.actuals[0]

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitCall(self, *args, **kwargs)

    def __repr__(self):
        return f'<CallNode "{self.ident}" w/ {len(self.actuals)} actuals at {self.id} >'


class Var(Expr):
    def __init__(self, meta, ident_token) -> None:
        super().__init__(meta)
        self.ident_token = ident_token

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitVar(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<Var "{self.ident_token}" at {self.id}>'

class ScopedID(Expr):
    def __init__(self, meta, name, object, id_tokens) -> None:
        super().__init__(meta)
        self.name = name
        self.object = object
        self.components = id_tokens

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitScopedID(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<ScopedID "{self.name}" at {id(self)}>'

class ThisID(Expr):
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

class SuperID(Expr):
    def __init__(self, meta, name, object, id_tokens) -> None:
        super().__init__(meta)
        self.name = name
        self.object = object
        assert object.name == 'super'
        self.components = id_tokens

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitSuperID(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<SuperID at {id(self)}>'

# object values
class Object(Expr):
    def __init__(self, meta, obj_type) -> None:
        super().__init__(meta)
        self.type = obj_type

    def accept(self, visitor, *args, **kwargs):
        raise NotImplementedError


class FuncObj(Object):  # inherit from new Obj (differentiate primative from obj maybe)
    def __init__(self, meta, ident, formals, ret_type, body) -> None:
        assert formals is not None
        super().__init__(meta, FuncType(meta, [formal.type for formal in formals], ret_type))
        self.ident = ident
        self.formals = formals
        self.ret_type = ret_type
        self.body = body

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFuncObj(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<FuncObj: "{self.ident}" - ([{", ".join(self.formals)}] -> {self.ret_type}) {{...}} at {self.id}>'


class MethodObj(Object):
    def __init__(self, meta, decorator, generics, mutability_mod, scope_mod, ret_type, formals, body) -> None:
        super().__init__(meta, FuncType(meta, mutability_mod, scope_mod, ret_type, [formal.type for formal in (formals or [])]))
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
    def __init__(self, meta, token, value, lit_type) -> None:
        super().__init__(meta)
        self.value = value
        self.type = lit_type

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitLiteral(self, *args, **kwargs)

    def __repr__(self):
        return f'<{self.type.__name__.upper()} = {self.value}>'

# literals
class Float(Literal):
    def __init__(self, meta, token) -> None:
        super().__init__(meta, token, float(token), float)

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFloat(self, *args, **kwargs)

class Int(Literal):
    def __init__(self, meta, token) -> None:
        super().__init__(meta, token, int(token), int)

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitInt(self, *args, **kwargs)


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

class Container(Expr):
    def __init__(self, meta) -> None:
        super().__init__(meta)

class Array(Container):
    def __init__(self, meta, values) -> None:
        super().__init__(meta)
        self.values = [val.value for val in values]
        self.type = type(self.values[0]) if self.values else None  # this will need to be changed later

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitArray(self, *args, **kwargs)

class Index(Expr):
    def __init__(self, meta, base, idx) -> None:
        super().__init__(meta)
        self.base = base
        self.name = base.name
        self.idx = idx

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitIndex(self, *args, **kwargs)
        