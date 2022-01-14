"""

"""

import lark
from icecream import ic

import core.env as sa
from core import ast_nodes
from core.ast_visitors import Binder, Unparser, GraphManager, Interpreter
from core import ReturnInterrupt


class AST:
    def __init__(self, root) -> None:
        self.root = root
        self.symbol_table = sa.SymbolTable()
        self.root.accept(Binder(), self.symbol_table)

    def unparsed(self):
        return self.root.accept(Unparser(), 0)

    def to_dot(self):
        graph_manager = GraphManager()
        self.root.accept(graph_manager, graph_manager.graph)
        return graph_manager.graph.to_string()

    def interpret(self):
        interpreter = Interpreter()
        exit_code = None
        try:
            self.root.accept(interpreter, self.symbol_table)
        except ReturnInterrupt as RI:
            exit_code = int(RI.ret_val)
        else:
            raise ValueError('Did not recieve any exit code...')
        
        return exit_code
        


@lark.v_args(inline=True)
class ASTBuilder(lark.visitors.Transformer_InPlaceRecursive):
    def __init__(self) -> None:
        super().__init__()

    root = lambda _, *args, **kwargs: AST(ast_nodes.Root(*args, **kwargs))

    fn_def = ast_nodes.FnDef
    typed_formal = ast_nodes.typed_formal

    scoped_id = simple_id = ast_nodes.ID

    assign_stmt = ast_nodes.AssignStmt
    
    num = ast_nodes.NumLit
    string = ast_nodes.StrLit
    boolean = ast_nodes.BoolLit

    user_fn_call = ast_nodes.Call
    
    print_call = ast_nodes.Print

    bin_op = ast_nodes.BinaryOperation

    for_stmt = ast_nodes.For
    if_stmt = ast_nodes.If
    while_stmt = ast_nodes.While
    return_stmt = ast_nodes.Return

    obj_type = ast_nodes.ObjType

    