"""

"""

from core.ast_visitors.visitor import Visitor
from core import ast_nodes


class Unparser(Visitor):
    def __init__(self) -> None:
        super().__init__()

    def visitRoot(self, print_root, depth):
        return '\n'.join(stmt.accept(self, depth) for stmt in print_root.stmts)

    def visitPrint(self, print_node, depth):
        return depth * '\t' + f'print({print_node.expr.accept(self, depth)})'

    def visitID(self, id_node, depth):
        return str(id_node.name)

    def visitAssign(self, assign_node, depth):
        return depth * '\t' + f'{assign_node.lhs.accept(self, depth)} = {assign_node.rhs.accept(self, depth)}'

    def visitBinOp(self, bin_op_node, depth):
        return f'({bin_op_node.lhs.accept(self, depth)} {bin_op_node.op_str} {bin_op_node.rhs.accept(self, depth)})'

    def visitCall(self, call_node, depth):
        id_unparsed = call_node.identifier.accept(self, depth)
        actuals_unparsed = ", ".join(formal.accept(self, depth) for formal in call_node.actuals)
        return f'{id_unparsed}({actuals_unparsed})'

    def visitReturn(self, return_node, depth):
        return depth * '\t' + f'return {return_node.expr.accept(self, depth)}'

    def visitIf(self, if_node, depth):
        res = ''
        for cond, body, block_type in if_node.if_sequence:
            res += depth * '\t' + block_type
            res += ' ' + cond.accept(self, depth)
            res += ' {\n' + '\n'.join([stmt.accept(self, depth + 1) for stmt in body])
            res += '\n' + (depth * '\t') + '}\n'

        return res

    def visitFor(self, for_node, depth):
        indent_offset = depth * '\t'
        body_unparsed = ('\n' + indent_offset).join(stmt.accept(self, depth + 1) for stmt in for_node.body)
        return depth * '\t' + f'for {for_node.identifier.accept(self, depth)} in {for_node.iterable.accept(self, depth)} {{\n{body_unparsed}\n{indent_offset}}}'

    def visitWhile(self, while_node, depth):
        indent_offset = depth * '\t'

        body_unparsed = ('\n' + indent_offset).join(stmt.accept(self, depth + 1) for stmt in while_node.body)
        return indent_offset + f'while {while_node.condition.accept(self, depth)} {{\n{body_unparsed}\n{indent_offset}}}'

    def visitPrimitiveType(self, obj_type_node, depth):
        return obj_type_node.inv_data_types[obj_type_node.type]

    def visitFnType(self, fn_def_node, depth):
        base_depth_str = depth * '\t'
        ret_type_unparsed = base_depth_str + fn_def_node.ret_type.accept(self, depth)
        formals_unparsed = ', '.join(ast_nodes.PrimitiveType.inv_data_types[formal.type] + ' ' + formal.accept(self, depth) for formal in fn_def_node.formals)
        body_unparsed = '\n'.join(stmt.accept(self, depth + 1) for stmt in fn_def_node.body)

        return f'({formals_unparsed}) -> {ret_type_unparsed} {{\n{body_unparsed}\n{base_depth_str}}}'

    def visitFnSignature(self, fn_sig_node, depth):
        return f'fn[{", ".join([f_type.accept(self, depth) for f_type in fn_sig_node.formal_types])} -> {fn_sig_node.ret_type.accept(self, depth)}]'

    def visitLiteral(self, literal_node, depth):
        raise NotImplementedError

    def visitNumLit(self, num_lit_node, depth):
        return str(num_lit_node.value)

    def visitStrLit(self, str_lit_node, depth):
        return '"' + str_lit_node.value + '"'

    def visitBoolLit(self, bool_lit_node, depth):
        return str(bool_lit_node.value)