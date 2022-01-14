"""

"""

# try to compose nodes as other nodes "desugar"

import lark
from icecream import ic
from core.ast_nodes.stmts import AssignStmt

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

    def root(self, stmts):
        return AST(ast_nodes.Root(stmts.children))

    print_call = ast_nodes.Print

    def bin_op(self, lhs, operation_token, rhs):
        return ast_nodes.BinOp(lhs, operation_token.value, rhs)

    def scoped_id(self, id_token):
        return ast_nodes.ID(id_token.value)

    simple_id = scoped_id

    assign_stmt = ast_nodes.AssignStmt

    def fn_def(self, decorator, ret_type, identifier, formals, body):
        fn_type = ast_nodes.FnType(
            decorator,
            ret_type,
            formals.children if formals else [],
            body.children
        )
        
        return AssignStmt(identifier, fn_type)

    def typed_formal(self, type_node, id_node):
        id_node.type = type_node.type
        return id_node

    user_fn_call = ast_nodes.Call

    return_stmt = ast_nodes.Return
    
    def if_stmt(self, if_block, else_if_blocks, else_block):
        if_sequence = [(if_block.children[0], if_block.children[1].children, 'if')]

        if else_if_blocks:
            for else_if_block in else_if_blocks.children:
                else_if_cond = else_if_block.children[0]
                else_if_body_stmts = else_if_block.children[1].children
                if_sequence.append((else_if_cond, else_if_body_stmts, 'else if'))
        
        if else_block:
            else_body_stmts = else_block.children[0].children
            if_sequence.append((ast_nodes.BoolLit(True), else_body_stmts, 'else'))
            
        return ast_nodes.If(if_sequence)

    def while_stmt(self, condition, body):
        return ast_nodes.While(condition, body.children if body else [])

    for_stmt = ast_nodes.For

    def obj_type(self, scope_modifier, obj_type_token, execution_modifier):
        if isinstance(obj_type_token, lark.Tree):
            _, input_types, ret_type = obj_type_token.children
            return ast_nodes.FnSignature(
                scope_modifier,
                (input_types.children if input_types else [], ret_type),
                execution_modifier
            )
        else:
            return ast_nodes.PrimitiveType(scope_modifier, obj_type_token.value, execution_modifier)

    def num(self, num_token):
        return ast_nodes.NumLit(float(num_token.value))

    def string(self, str_token):
        return ast_nodes.StrLit(str_token.value[1:-1])

    def boolean(self, bool_token):
        return ast_nodes.BoolLit({'true': True, 'false': False}[bool_token.value])
    