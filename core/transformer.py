"""
Transforms lark tokens and trees into desugared components.
When used as a lark transformer, this class defines how the AST nodes are built.
"""

# type of fn obj is <func> (+args?), type of class obj is <class>, nothing else (I think)
# primitive are immutable, passed by value, else are object, mutable, passed by ref
# make sure that fns wo ret stmt still return None or smth
# for print, desugar by implicitly casting args to str first

import lark
from icecream import ic
from pydot import Node

from core.program import Program
from core.ast_nodes import *


def make_collector(*args, type_ = NodeList):
    return lambda _, meta, *items: type_(meta, items, *args)


@lark.v_args(wrapper = lambda fn, rule_token, children, meta: fn(meta, *children))
class ASTBuilder(lark.visitors.Transformer_InPlaceRecursive):
    def __init__(self) -> None:
        super().__init__()

    # GLOBALS
    root = lambda _, *args: Program(Root(*args))
    globals = make_collector('globals')

    # STATEMENTS
    # control
    branch = make_collector(type_ = If)

    def primary_branch(self, meta, supposition_kw, cond, block):
        if supposition_kw == 'unless':
            true_cond = UnaryOp(cond.meta, '!', cond)
        else:
            assert supposition_kw == "if"
            true_cond = cond
        meta.supposition_kw = supposition_kw
        return Branch(meta, true_cond, block, supposition_kw)

    secondary_branch = lambda self, *args: self.primary_branch(*args)

    def loop(self, meta, loop_type, cond, body, else_block):
        if loop_type == 'until':
            true_cond = UnaryOp(cond.meta, '!', cond)
        else:
            assert loop_type == 'while'
            true_cond = cond
        meta.loop_type = loop_type
        return While(true_cond, body, else_block)

    def for_(self, meta, identifier, iterable, body, else_block):
        # need to implement else_block
        assign_node = AssignDecl(meta, identifier, NumLit('0'), None, None, None)
        cond = BinOp(meta, identifier, '!=', iterable)
        inc = BinOp(meta, identifier, '+', NumLit('1'))
        assign_node2 = Assign(meta, identifier, inc)
        body.nodes += (assign_node2,)
        while_node = While(meta, cond, body)
        return NodeList(meta, [assign_node, while_node], 'while')

    return_ = lambda _, meta, expr: Return(meta, expr or None_(meta))

    # assignment
    def assign_decl(self, meta, declarations, exprs):
        # add support for mult left, one right i.e. a, b, c = (1, 2, 3)
        return NodeList(meta, [AssignDecl(meta, decl, expr, decl.mods['mutability'], decl.mods['scope'], decl.mods['execution']) for decl, expr in zip(declarations, exprs)], 'assign_decl')

    def assign(self, meta, lvals, exprs):
        # curr assumes sizes are equal
        assignments = []
        for lhs, rhs in zip(lvals, exprs):
            if isinstance(lhs, ScopedID):
                assignments.append(SetStmt(meta, lhs, rhs))
            else:
                assignments.append(Assign(meta, lhs, rhs))
        return NodeList(meta, assignments, 'assignments')

    lvals = make_collector('lvals')

    declared_identifiers = make_collector('decl_ids')

    def declared_identifier(self, meta, mutability_modifier, scope_modifier, execution_modifier, simple_id):
        return ID(
                meta,
                simple_id,
                mutability = mutability_modifier,
                scope = scope_modifier,
                execution = execution_modifier,
            )

    # definition
    def fn_def(self, meta, decorator, generics, mutability_mod, scope_mod, ret_type, identifier, formals, body):
        fn_obj = FnObj(
            meta,
            decorator,
            generics,
            mutability_mod,
            scope_mod,
            ret_type,
            formals or NodeList(meta, [], 'formals'),
            body
        )
        fn_obj.name = identifier.name
        return AssignDecl(meta, identifier, fn_obj, None, None, None)

    formals = make_collector('formals')

    def formal(self, meta, type_node, id_node):
        id_node.type = type_node.type
        id_node.meta = meta
        return id_node

    # scoping
    def block(self, meta, body):
        # might need to modify this and loop block
        body.meta = meta
        return body

    body = make_collector('body')
    loop_body = make_collector('loop_body')

    def parameterized_object_type(self, meta, obj_type, parameterization):
        if parameterization:
            obj_type.parameterize(parameterization)
            obj_type.meta = meta
        return obj_type

    def fn_type(self, meta, mutability_mod, scope_mod, formal_types, ret_type):
        return FnType(meta, mutability_mod, scope_mod, ret_type, formal_types or [])

    def anon_fn(self, meta, formals, ret_type, body):
        fn = FnObj(
            meta,
            None,
            None,
            None,
            None,
            ret_type,
            formals or NodeList(meta, [], 'formals'),
            body
        )

        fn.name = id(fn)  # this may be un-ideal
        
        return fn

    def cls_def(self, meta, decorator, generics, id_, inheritance, cls_assignments):
        # should prob break up static vars from methods
        for a in cls_assignments:
            a.belongs_to = id_.name
        return ClassObj(meta, decorator, generics, id_.name, inheritance, cls_assignments)

    cls_stmts = make_collector('cls_stmts')

    def method(self, meta, decorator, generics, mutability_mod, scope_mod, ret_type, identifier, formals, body):
        method_obj = MethodObj(
            meta,
            decorator,
            generics,
            mutability_mod,
            scope_mod,
            ret_type,
            formals or NodeList(meta, [], 'formals'),
            body
        )
        method_obj.name = identifier.name
        return method_obj # AssignDecl(meta, identifier, method_obj, None, None, None)

    # TYPING
    def type_(self, meta, type_token, execution_modifier):
        if isinstance(type_token, FnType):
            assert execution_modifier is None
            return type_token
        else:
            return PrimitiveType(meta, type_token, execution_modifier)

    # EXPRESSIONS
    exprs = make_collector('exprs')
    bin_op = BinOp

    def paren_expr(self, meta, inner):
        inner.meta = meta
        return inner

    # identifiers
    def scoped_id(self, meta, *args):
        joined = '.'.join(args[1:])
        return ScopedID(meta, joined, ID(meta, args[0]), args)

    simple_id = ID

    # call
    call = lambda _, meta, id_, *actuals: Call(meta, id_, actuals)
    actuals = make_collector('actuals')
    kwarg = Assign

    # literals
    NUMBER, STRING, BOOLEAN, NONE = NumLit, StrLit, BoolLit, None_