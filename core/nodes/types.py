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
        'int': int,
        'float': float,
        'str': str,
        'bool': bool,
        'none': None,
        'void': 'void',
    }

    inv_data_types = {v: k for k, v in data_types.items()}

    def __init__(self, meta, primitive_token) -> None:
        super().__init__(meta)
        self.primitive_token = primitive_token
        self.type = PrimitiveType.data_types[primitive_token]

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitPrimitiveType(self, *args, **kwargs)

    def __repr__(self):
        return f'<Type "{self.primitive_token}">'


class FuncType(ObjectType):
    def __init__(self, meta, formal_types, ret_type) -> None:
        super().__init__(meta)
        self.formal_types = formal_types
        self.ret_type = ret_type

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFuncType(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<"([{", ".join(self.formal_types)}] -> {self.ret_type})" at {self.id}>'

class ClassType(ObjectType):
    def __init__(self, meta, cls_name) -> None:
        super().__init__(meta)
        self.ret_type = cls_name

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFnType(self, *args, **kwargs)