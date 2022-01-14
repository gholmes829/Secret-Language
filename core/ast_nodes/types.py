"""

"""

from core.ast_nodes.node import ASTNode

# types
class ObjType(ASTNode):

    data_types = {
        'num': float,
        'str': str,
        'bool': bool,
        'void': None,
    }

    inv_data_types = {v: k for k, v in data_types.items()}

    def __init__(self, scope_modifier, token, execution_modifier) -> None:
        super().__init__(None, None)
        self.type = ObjType.data_types[token.value]
        self.scope_modifier = scope_modifier
        self.execution_modifier = execution_modifier

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitObjType(self, *args, **kwargs)