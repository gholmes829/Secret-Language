"""

"""

from icecream import ic

from core.nodes.node import ASTNode

class ObjectType(ASTNode):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)


# types
class PrimitiveType(ObjectType):

    data_types = {
        'num': float,
        'str': str,
        'bool': bool,
        'none': None,
        'void': 'void',
    }

    inv_data_types = {v: k for k, v in data_types.items()}

    def __init__(self, base_token, _type, execution_modifier) -> None:
        super().__init__(base_token)
        self.raw_type = _type
        self.type = PrimitiveType.data_types[_type.value]
        self.execution_modifier = execution_modifier

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitPrimitiveType(self, *args, **kwargs)


class FnType(ObjectType):
    def __init__(self, meta, mutability_mod, scope_mod, ret_type, formal_types) -> None:
        super().__init__(meta)
        self.identifier = str(id(self))
        self.mutability_mod = mutability_mod
        self.scope_modifier = scope_mod
        self.ret_type = ret_type
        self.formal_types = formal_types
        self.type = self

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFnType(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<"fn_type" at {id(self)}>'

class ClassType(ObjectType):
    def __init__(self, meta, cls_name) -> None:
        super().__init__(meta)
        self.ret_type = cls_name

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFnType(self, *args, **kwargs)