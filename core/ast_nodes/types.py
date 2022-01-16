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


class FnSignature(ObjectType):
    def __init__(self, scope_modifier, signature, execution_modifier) -> None:
        self.identifier = str(id(self))
        self.scope_modifier = scope_modifier
        self.signature = signature
        self.execution_modifier = execution_modifier
        self.type = self
        self.formal_types, self.ret_type = self.signature

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFnSignature(self, *args, **kwargs)

    def __repr__(self) -> str:
        return f'<fn_signature at {id(self)}>'