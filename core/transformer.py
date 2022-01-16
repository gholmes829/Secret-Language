"""
Transforms lark tokens and trees into desugared components.
When used as a lark transformer, this class defines how the AST nodes are built.
"""

# type of fn obj is <func> (+args?), type of class obj is <class>, nothing else (I think)
# primitive are immutable, passed by value, else are object, mutable, passed by ref

import lark
from icecream import ic

from core.ast_manager import AST
from core.ast_nodes import *


@lark.v_args(wrapper = lambda fn, rule_token, children, meta: fn(meta, *children))
class ASTBuilder(lark.visitors.Transformer_InPlaceRecursive):
    def __init__(self) -> None:
        super().__init__()

    # GLOBALS
    # =======
    root = lambda _, *args: AST(Root(*args))
    globals = lambda _, meta, *globals: NodeList(meta, globals, 'globals')

    # STATEMENTS
    # ==========
    print_call = Print

    # control
    branch = lambda _, meta, *branches: If(meta, branches)

    def primary_branch(self, meta, supposition_kw, cond, block):
        if supposition_kw == 'unless':
            true_cond = UnaryOp(cond.meta, '!', cond)
        else:
            assert supposition_kw == "if"
            true_cond = cond
        meta.supposition_kw = supposition_kw
        return Branch(meta, true_cond, block)

    secondary_branch = lambda self, *args: self.primary_branch(*args)

    def loop(self, meta, loop_type, cond, body, else_block):
        if loop_type == 'until':
            true_cond = UnaryOp(cond.meta, '!', cond)
        else:
            assert loop_type == 'while'
            true_cond = cond
        meta.loop_type = loop_type
        return While(true_cond, body, else_block)

    for_ = For  # TODO: desugar for_
    return_ = lambda _, meta, expr: Return(meta, expr or None_(meta))

    # assignment
    assign_decl_stmt = AssignDeclStmt
    assign_stmt = AssignStmt

    # definition
    def fn_def(self, meta, decorator, generics, ret_type, identifier, formals, body):
        fn_obj = FnObj(
            meta,
            decorator,
            generics,
            ret_type,
            formals,
            body
        )
        return AssignStmt(meta, identifier, fn_obj)

    formals = lambda _, meta, *formals: NodeList(meta, formals, 'formals')

    def formal(self, meta, type_node, id_node):
        id_node.type = type_node.type
        id_node.meta = meta
        return id_node

    # scoping
    def block(self, meta, body):
        # might need to modify this and loop block
        body.meta = meta
        return body

    body = lambda _, meta, *stmts: NodeList(meta, stmts, 'body')
    loop_body = lambda _, meta, *stmts: NodeList(meta, stmts, 'loop_body')

    # TYPING
    # ======
    def type_(self, meta, type_token, execution_modifier):
        if isinstance(type_token, lark.Tree):
            print('What a strange instance...')
            input('Input: you said you wanted to check this out...')
            _, input_types, ret_type = type_token.children
            return FnSignature(
                meta,
                None,
                (input_types.children if input_types else [], ret_type),
                execution_modifier
            )
        else:
            return PrimitiveType(meta, type_token, execution_modifier)

    # EXPRESSIONS
    # ===========
    bin_op = BinOp

    def paren_expr(self, meta, inner):
        inner.meta = meta
        return inner


    # identifiers
    scoped_id = simple_id = ID

    # call
    call = lambda _, meta, id_, *actuals: Call(meta, id_, actuals)
    actuals = lambda _, meta, *actuals: NodeList(meta, actuals, 'actuals')
    kwarg = AssignStmt

    # literals
    NUMBER = NumLit
    STRING = StrLit
    BOOLEAN = BoolLit
    NONE = None_