"""

"""

from core.ast_nodes.stmts import Stmt

class Print(Stmt):
    def __init__(self, token, expr) -> None:
        super().__init__(token)
        self.expr = expr

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitPrint(self, *args, **kwargs)