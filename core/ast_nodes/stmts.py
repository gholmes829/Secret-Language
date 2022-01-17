"""

"""

from icecream import ic

from core.ast_nodes.node import ASTNode

# stmts
class Stmt(ASTNode):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='lightblue', **kwargs)

# control
class If(Stmt):
    def __init__(self, meta, branch_seq) -> None:
        super().__init__(meta)
        self.branch_seq = branch_seq

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitIf(self, *args, **kwargs)

class Branch(Stmt):
    def __init__(self, meta, cond, body, branch_type) -> None:
        super().__init__(meta)
        self.cond = cond
        self.body = body
        self.branch_type = branch_type

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitBranch(self, *args, **kwargs)


class While(Stmt):
    def __init__(self, meta, condition, body) -> None:
        super().__init__(meta)
        self.condition = condition
        self.body = body

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitWhile(self, *args, **kwargs)

class Return(Stmt):
    def __init__(self, meta, expr) -> None:
        super().__init__(meta)
        self.expr = expr
        self.value = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitReturn(self, *args, **kwargs)


# assignment
class AssignDecl(Stmt):
    def __init__(self, meta, lhs, rhs, mutability, scope, execution) -> None:
        super().__init__(meta)
        self.lhs = lhs
        self.rhs = rhs
        # modifiers, default None
        self.mutability = mutability
        self.scope = scope
        self.execution = execution
    
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitAssignDecl(self, *args, **kwargs)

class Assign(Stmt):
    def __init__(self, meta, lhs, rhs) -> None:
        super().__init__(meta)
        self.lhs = lhs
        self.rhs = rhs
    
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitAssign(self, *args, **kwargs)