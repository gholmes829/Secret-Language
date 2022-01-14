"""

"""

from core.ast_nodes.node import ASTNode

# stmts
class Stmt(ASTNode):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='lightblue', **kwargs)
        

# statements
class AssignStmt(Stmt):
    def __init__(self, lhs, rhs) -> None:
        super().__init__(None, None)
        self.lhs = lhs
        self.rhs = rhs
        self.lhs.type = rhs.type
    
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitAssign(self, *args, **kwargs)

class FnDef(Stmt):
    def __init__(self, decorator, ret_type, identifier, formals, body) -> None:
        super().__init__(None, None)
        self.decorator = decorator
        self.ret_type = ret_type
        self.identifier = identifier
        self.name = identifier.name
        self.formals = formals.children if formals else []
        self.body = body.children
        self.symbol = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFnDef(self, *args, **kwargs)

class Return(Stmt):
    def __init__(self, expr) -> None:
        super().__init__(expr.start_token, expr.end_token)
        self.expr = expr
        self.value = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitReturn(self, *args, **kwargs)


class If(Stmt):
    def __init__(self, if_sequence) -> None:
        super().__init__(None, None)
        self.if_sequence = if_sequence

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitIf(self, *args, **kwargs)


class For(Stmt):
    def __init__(self, identifier, iterable, body) -> None:
        super().__init__(None, None)
        self.identifier = identifier
        self.iterable = iterable
        self.body = body.children if body else []

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFor(self, *args, **kwargs)


class While(Stmt):
    def __init__(self, condition, body) -> None:
        self.condition = condition
        self.body = body
        super().__init__(None, None)

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitWhile(self, *args, **kwargs)