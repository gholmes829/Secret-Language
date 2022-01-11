"""

"""

import lark
from icecream import ic

import semantic_analysis as sa
import ast_nodes as nodes


class AST:
    def __init__(self, root) -> None:
        self.root = root
        self.symbol_table = sa.SymbolTable()
        self.root.bind_symbols(self.symbol_table)

    def unparsed(self):
        return self.root.unparsed(0)

    def to_dot(self):
        return self.root.to_dot()[0].to_string()

    def interpret(self):
        exit_code = None
        try:
            self.root.interpret(self.symbol_table)
        except nodes.ReturnInterrupt as RI:
            exit_code = int(RI.ret_val)
        else:
            raise ValueError('Did not recieve any exit code...')
        
        return exit_code
        



@lark.v_args(inline=True)
class ASTBuilder(lark.visitors.Transformer_InPlaceRecursive):
    def __init__(self) -> None:
        super().__init__()

    root = lambda _, *args, **kwargs: AST(nodes.Root(*args, **kwargs))

    fn_def = nodes.FnDef
    typed_formal = nodes.typed_formal

    scoped_id = simple_id = nodes.ID

    assign_stmt = nodes.AssignStmt
    
    num = nodes.NumLit
    string = nodes.StrLit
    boolean = nodes.BoolLit

    user_fn_call = nodes.Call
    
    print_call = nodes.Print

    bin_op = nodes.BinaryOperation

    for_stmt = nodes.For
    if_stmt = nodes.If
    while_stmt = nodes.While
    return_stmt = nodes.Return

    obj_type = nodes.ObjType

    