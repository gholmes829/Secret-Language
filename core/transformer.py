"""

"""

import lark
from icecream import ic

from core import ast_nodes
from core.ast_manager import AST
from core.ast_nodes import AssignStmt


@lark.v_args(inline=True)
class ASTBuilder(lark.visitors.Transformer_InPlaceRecursive):
    def __init__(self) -> None:
        super().__init__()

    def root(self, stmts):
        return AST(ast_nodes.Root(stmts.children))

    def print_call(self, _, expr):
        return ast_nodes.Print(expr)

    def bin_op(self, lhs, operation_token, rhs):
        return ast_nodes.BinOp(lhs, operation_token.value, rhs)

    def scoped_id(self, id_token):
        return ast_nodes.ID(id_token.value)

    def simple_id(self, id_token):
        return ast_nodes.ID(id_token.value)

    def assign_stmt(self, identifier, expr):
        assign_node = ast_nodes.AssignStmt(identifier, expr)
        return assign_node

    def assign_decl_stmt(self, mutability_modifier, scope_modifier, execution_modifier, identifier, expr):
        return ast_nodes.AssignStmt(identifier, expr)  # TODO: add remaining info in new class

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

    def actual(self, expr):
        return expr

    def fn_call(self, identifier, actuals):
        return ast_nodes.Call(identifier, actuals)

    def return_stmt(self, expr):
        if expr:
            return ast_nodes.Return(expr or ast_nodes.Null())
    
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

    def loop_stmt(self, condition, body, else_block):
        return ast_nodes.While(condition, body.children if body else [])

    def for_stmt(self, identifier, iterable, body, else_block):
        return ast_nodes.For(identifier, iterable, body, else_block)

    def obj_type(self, obj_type_token, execution_modifier):
        if isinstance(obj_type_token, lark.Tree):
            _, input_types, ret_type = obj_type_token.children
            return ast_nodes.FnSignature(
                None,
                (input_types.children if input_types else [], ret_type),
                execution_modifier
            )
        else:
            return ast_nodes.PrimitiveType(obj_type_token.value, execution_modifier)

    def num(self, num_token):
        return ast_nodes.NumLit(float(num_token.value))

    def string(self, str_token):
        return ast_nodes.StrLit(str_token.value[1:-1])

    def boolean(self, bool_token):
        return ast_nodes.BoolLit({'true': True, 'false': False}[bool_token.value])

    def null(self, null_token):
        return ast_nodes.Null()