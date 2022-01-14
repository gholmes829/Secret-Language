"""

"""

from copy import deepcopy

from core.ast_visitors.visitor import Visitor
from core import ast_nodes


class ReturnInterrupt(Exception):
    def __init__(self, ret_val) -> None:
        super().__init__('Returning!!!')
        self.ret_val = ret_val


class Interpreter(Visitor):
    def __init__(self) -> None:
        super().__init__()

    def visitRoot(self, root_node, symbol_table):
        fn_sym = symbol_table['globals', 'main']
        start = None
        for stmt in root_node.stmts:
            if isinstance(stmt, ast_nodes.FnDef) and stmt.symbol == fn_sym:
                start = stmt
                break
        start.accept(self, symbol_table)

    def visitPrint(self, print_node, symbol_table):
        print_node.expr.accept(self, symbol_table)
        print(print_node.expr.value, flush=True)

    def visitID(self, id_node, symbol_table):
        pass

    def visitAssign(self, assign_node, symbol_table):
        assign_node.rhs.accept(self, symbol_table)
        assign_node.lhs.value = assign_node.rhs.value

    def visitBinOp(self, bin_op_node, symbol_table):
        bin_op_node.lhs.accept(self, symbol_table)
        bin_op_node.rhs.accept(self, symbol_table)
        lhs_val = bin_op_node.lhs.value
        rhs_val = bin_op_node.rhs.value
        bin_op_node.value = bin_op_node.type(bin_op_node.op(bin_op_node.lhs_cast(lhs_val), bin_op_node.rhs_cast(rhs_val)))

    def visitFnDef(self, fn_def_node, symbol_table):
        for stmt in fn_def_node.body:
            stmt.accept(self, symbol_table)


    def visitCall(self, call_node, symbol_table):
        for actual in call_node.actuals:
            actual.accept(self, symbol_table)

        fn_sym = deepcopy(symbol_table['globals', call_node.identifier.name])
        fn_body = fn_sym.body
        formals = fn_sym.formals

        for formal, actual in zip(formals, call_node.actuals):
            formal.symbol.value = actual.value

        for stmt in fn_body:
            try:
                stmt.accept(self, symbol_table)
            except ReturnInterrupt as RI:
                call_node.value = RI.ret_val
                break


    def visitReturn(self, return_node, symbol_table):
        return_node.expr.accept(self, symbol_table)
        return_node.value = return_node.expr.value
        raise ReturnInterrupt(return_node.expr.value)


    def visitIf(self, if_node, symbol_table):
        for cond, body, block_type in if_node.if_sequence:
            if cond:
                cond.accept(self, symbol_table)
                if not cond.value:
                    continue
            
            for stmt in body:
                stmt.accept(self, symbol_table)

            break

    def visitFor(self, for_node, symbol_table):
        for_node.identifier.value = 0
        for_node.iterable.accept(self, symbol_table)
        for i in range(int(for_node.iterable.value)):
            for stmt in for_node.body:
                stmt.accept(self, symbol_table)
            for_node.iterable.accept(self, symbol_table)
            for_node.identifier.value = i + 1

    def visitWhile(self, while_node, symbol_table):
        while_node.condition.accept(self, symbol_table)

        while while_node.condition.value:
            for stmt in while_node.body:
                stmt.accept(self, symbol_table)
            while_node.condition.accept(self, symbol_table)

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