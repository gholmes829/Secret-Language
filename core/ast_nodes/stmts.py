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
class AssignDeclStmt(Stmt):
    def __init__(self, meta, lhs, rhs, mutability, scope, execution) -> None:
        super().__init__(meta)
        self.lhs = lhs
        self.rhs = rhs
        self.lhs.type = rhs.type
        # modifiers, default None
        self.mutability = mutability
        self.scope = scope
        self.execution = execution
    
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitAssign(self, *args, **kwargs)

class AssignStmt(Stmt):
    def __init__(self, token, lhs, rhs) -> None:
        super().__init__(token)
        self.token = token
        self.lhs = lhs
        self.rhs = rhs
        self.lhs.type = rhs.type
    
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitAssign(self, *args, **kwargs)


class Return(Stmt):
    def __init__(self, token, expr) -> None:
        super().__init__(token)
        self.expr = expr
        self.value = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitReturn(self, *args, **kwargs)


class If(Stmt):
    def __init__(self, token, if_sequence) -> None:
        super().__init__(token)
        self.if_sequence = if_sequence

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitIf(self, *args, **kwargs)

class Branch(Stmt):
    def __init__(self, token, cond, body) -> None:
        super().__init__(token)
        self.cond = cond
        self.body = body

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitBranch(self, *args, **kwargs)


class For(Stmt):
    def __init__(self, token, identifier, iterable, body, else_block) -> None:
        super().__init__(token)
        self.identifier = identifier
        self.iterable = iterable
        self.body = body
        self.else_block = else_block

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitFor(self, *args, **kwargs)


class While(Stmt):
    def __init__(self, meta, condition, body) -> None:
        super().__init__(meta)
        self.condition = condition
        self.body = body

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitWhile(self, *args, **kwargs)