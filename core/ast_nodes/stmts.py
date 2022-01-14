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

def typed_formal(_, _type, _identifier):
    _identifier.type = _type.type
    return _identifier

class Return(Stmt):
    def __init__(self, expr) -> None:
        super().__init__(expr.start_token, expr.end_token)
        self.expr = expr
        self.value = None

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitReturn(self, *args, **kwargs)


class If(Stmt):
    def __init__(self, if_block, else_if_blocks, else_block) -> None:
        super().__init__(None, None)
        
        self.if_sequence = []

        if_cond = if_block.children[0]
        if_body_stmts = if_block.children[1].children
        
        self.if_sequence.append((if_cond, if_body_stmts, 'if'))

        if else_if_blocks:
            for else_if_block in else_if_blocks.children:
                else_if_cond = else_if_block.children[0]
                else_if_body_stmts = else_if_block.children[1].children
                self.if_sequence.append((else_if_cond, else_if_body_stmts, 'else if'))

        if else_block:
            else_body_stmts = else_block.children[0].children
            self.if_sequence.append((None, else_body_stmts, 'else'))

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
        self.body = body.children if body else []
        super().__init__(None, None)

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitWhile(self, *args, **kwargs)