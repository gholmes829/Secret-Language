"""

"""

from icecream import ic

from core.nodes.node import ASTNode

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
    def __init__(self, meta, condition, body, else_block) -> None:
        super().__init__(meta)
        self.condition = condition
        self.body = body
        self.else_block = else_block

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

class SetStmt(Stmt):
    def __init__(self, meta, lhs, rhs) -> None:
        super().__init__(meta)
        self.lhs = lhs
        self.rhs = rhs
    
    def accept(self, visitor, *args, **kwargs):
        return visitor.visitSetStmt(self, *args, **kwargs)


class TryCatch(Stmt):
    def __init__(self, meta, try_, catch, finally_) -> None:
        super().__init__(meta)
        self.try_ = try_
        self.catch = catch
        self.finally_ = finally_

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitTryCatch(self, *args, **kwargs)

class Try(Stmt):
    def __init__(self, meta, body) -> None:
        super().__init__(meta)
        self.body = body

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitTry(self, *args, **kwargs)

class Catch(Stmt):
    def __init__(self, meta, exception, alias, body) -> None:
        super().__init__(meta)
        self.exception = Exception  # exception
        self.alias = alias
        self.body = body

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitCatch(self, *args, **kwargs)