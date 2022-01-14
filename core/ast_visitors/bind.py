"""

"""

from core.ast_visitors.visitor import Visitor


class Binder(Visitor):
    def __init__(self) -> None:
        super().__init__()

    def visitRoot(self, root_node, symbol_table):
        symbol_table.enter_scope('globals')
        for stmt in root_node.stmts:
            stmt.accept(self, symbol_table)
        symbol_table.leave_scope()
        assert not symbol_table.table_chain

    def visitPrint(self, print_node, symbol_table):
        print_node.expr.accept(self, symbol_table)

    def visitID(self, id_node, symbol_table):
        try:
            id_node.symbol = symbol_table[id_node.name]
            id_node._type = id_node.symbol.type
        except KeyError:
            assert id_node.type, (id_node.name, id_node.type)
            id_node.symbol = symbol_table.add_var(id_node.name, id_node.type)

    def visitAssign(self, assign_node, symbol_table):
        assign_node.rhs.accept(self, symbol_table)
        assign_node.lhs.type = assign_node.rhs.type
        assign_node.lhs.accept(self, symbol_table)

    def visitBinOp(self, bin_op_node, symbol_table):
        bin_op_node.lhs.accept(self, symbol_table)
        bin_op_node.rhs.accept(self, symbol_table)
        bin_op_node.lhs_cast, bin_op_node.rhs_cast, bin_op_node.type = \
            bin_op_node.type_resolutions[bin_op_node.op_str, bin_op_node.lhs.type, bin_op_node.rhs.type]

    def visitFnDef(self, fn_def_node, symbol_table):
        sym = symbol_table.add_fn(fn_def_node.name, [formal.type for formal in fn_def_node.formals], fn_def_node.ret_type.type, fn_def_node.body, fn_def_node.formals)
        fn_def_node.symbol = sym
        symbol_table.enter_scope(str(fn_def_node.name))
        for formal in fn_def_node.formals:
            formal.accept(self, symbol_table)
        for stmt in fn_def_node.body:
            stmt.accept(self, symbol_table)
        symbol_table.leave_scope()

    def visitCall(self, call_node, symbol_table):
        for actual in call_node.actuals:
            actual.accept(self, symbol_table)

        call_node.type = symbol_table[call_node.identifier.name].ret_type

    def visitReturn(self, return_node, symbol_table):
        return_node.expr.accept(self, symbol_table)

    def visitIf(self, if_node, symbol_table):
        for cond, body, block_type in if_node.if_sequence:
            if cond:
                cond.accept(self, symbol_table)

            for stmt in body:
                stmt.accept(self, symbol_table)   

    def visitFor(self, for_node, symbol_table):
        for_node.iterable.accept(self, symbol_table)
        for_node.identifier.type = for_node.iterable.type
        for_node.identifier.accept(self, symbol_table)
        for stmt in for_node.body:
            stmt.accept(self, symbol_table)


    def visitWhile(self, while_node, symbol_table):
        while_node.condition.accept(self, symbol_table)
        for stmt in while_node.body:
            stmt.accept(self, symbol_table)

    def visitObjType(self, obj_type_node, symbol_table):
        raise NotImplementedError

    def visitLiteral(self, literal_node, symbol_table):
        raise NotImplementedError

    def visitNumLit(self, num_lit_node, symbol_table):
        pass

    def visitStrLit(self, str_lit_node, symbol_table):
        pass

    def visitBoolLit(self, bool_lit_node, symbol_table):
        pass