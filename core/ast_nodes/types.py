"""

"""

from icecream import ic

from core.ast_nodes.node import ASTNode

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
    }

    inv_data_types = {v: k for k, v in data_types.items()}

    def __init__(self, base_token, value, execution_modifier) -> None:
        super().__init__(base_token)
        self.type = PrimitiveType.data_types[value]
        self.execution_modifier = execution_modifier

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitPrimitiveType(self, *args, **kwargs)


class FnType(ObjectType):
    def __init__(self, mutability_mod, scope_mod, ret_type, formal_types) -> None:
        self.identifier = str(id(self))
        self.mutability_mod = mutability_mod
        self.scope_modifier = scope_mod
        self.ret_type = ret_type
        self.formal_types = formal_types

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFnType(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<"fn_type" at {id(self)}>'