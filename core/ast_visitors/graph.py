"""

"""

import pydot

from core.ast_visitors.visitor import Visitor
from core import ast_nodes

# for loop and maybe others need work


class GraphManager(Visitor):
    def __init__(self) -> None:
        super().__init__()
        self.graph = pydot.Graph(graph_type = 'digraph')
        self.graph.set_graph_defaults(dpi = 300)
        self.graph.set_node_defaults(style = 'filled')
        self.graph.set_edge_defaults()

    def visitRoot(self, root_node, graph):
        root_graph_node = root_node.make_pydot_node(label = 'root')
        graph.add_node(root_graph_node)
        global_nodes = [glbl.accept(self, graph) for glbl in root_node.globals]
        
        for global_node in global_nodes:
            assert root_graph_node and global_node
            graph.add_edge(pydot.Edge(root_graph_node, global_node))

        return root_graph_node

    def visitPrint(self, print_node, graph):
        print_graph_node = print_node.make_pydot_node(label = 'print_stmt')
        graph.add_node(print_graph_node)
        expr_node = print_node.expr.accept(self, graph)
        assert print_graph_node and expr_node
        graph.add_edge(pydot.Edge(print_graph_node, expr_node))
        return print_graph_node

    def visitID(self, id_node, graph):
        try:
            id_type = ast_nodes.PrimitiveType.inv_data_types[id_node.type]
        except KeyError:
            id_type = id_node.type

        node = id_node.make_pydot_node(label = f'ID: "{id_node.name}"\nType: {id_type}')
        graph.add_node(node)
        return node

    def visitAssign(self, assign_node, graph):
        assign_graph_node = assign_node.make_pydot_node(label = 'assign_stmt')
        graph.add_node(assign_graph_node)
        lhs_node = assign_node.lhs.accept(self, graph)
        rhs_node = assign_node.rhs.accept(self, graph)
        assert assign_graph_node and lhs_node and rhs_node
        graph.add_edge(pydot.Edge(assign_graph_node, lhs_node))
        graph.add_edge(pydot.Edge(assign_graph_node, rhs_node))
        return assign_graph_node

    def visitBinOp(self, bin_op_node, graph):
        operation_node = bin_op_node.make_pydot_node(label = f'BinOp: "{bin_op_node.op_name}"')
        graph.add_node(operation_node)
        lhs_node = bin_op_node.lhs.accept(self, graph)
        rhs_node = bin_op_node.rhs.accept(self, graph)
        assert operation_node
        assert lhs_node
        assert rhs_node, bin_op_node.rhs
        graph.add_edge(pydot.Edge(operation_node, lhs_node))
        graph.add_edge(pydot.Edge(operation_node, rhs_node))
        return operation_node


    def visitCall(self, call_node, graph):
        # fn def
        call_graph_node = call_node.make_pydot_node(label = f'call: "{call_node.identifier.name}"')
        graph.add_node(call_graph_node)

        # actuals
        actuals_node = pydot.Node(hash(tuple(call_node.actuals) + (call_node.identifier, call_node.type)), label = 'actuals', fillcolor = 'plum')
        graph.add_node(actuals_node)
        assert call_graph_node and actuals_node
        graph.add_edge(pydot.Edge(call_graph_node, actuals_node))

        for actual in call_node.actuals:
            actual_node = actual.accept(self, graph)
            assert actual_node
            graph.add_edge(pydot.Edge(actuals_node, actual_node))
        
        return call_graph_node

    
    def visitReturn(self, return_node, graph):
        return_graph_node = return_node.make_pydot_node(label = 'return_stmt')
        graph.add_node(return_graph_node)

        expr_node = return_node.expr.accept(self, graph)
        assert return_graph_node and expr_node
        graph.add_edge(pydot.Edge(return_graph_node, expr_node))

        return return_graph_node


    def visitIf(self, if_node, graph: pydot.Graph):
        if_stmt_node = if_node.make_pydot_node(label = 'if_stmt')
        graph.add_node(if_stmt_node)

        for cond, body, block_type in if_node.if_sequence:
            base_node = pydot.Node(hash((cond, block_type)), label = block_type, fillcolor = 'plum')
            graph.add_node(base_node)
            assert if_stmt_node and base_node
            graph.add_edge(pydot.Edge(if_stmt_node, base_node))

            if cond:
                cond_node = pydot.Node(hash((cond, block_type, 'condition')), label = 'condition')
                graph.add_node(cond_node)
                assert cond_node
                graph.add_edge(pydot.Edge(base_node, cond_node))

                cond_expr_node = cond.accept(self, graph)
                assert cond_expr_node
                graph.add_edge(pydot.Edge(cond_node, cond_expr_node))
            
            body_node = pydot.Node(hash((tuple(body), block_type)), label = 'body')
            graph.add_node(body_node)
            assert body_node
            graph.add_edge(pydot.Edge(base_node, body_node))

            for stmt in body:
                stmt_node = stmt.accept(self, graph)
                assert stmt_node
                graph.add_edge(pydot.Edge(body_node, stmt_node))

        return if_stmt_node

    def visitFor(self, for_node, graph):
        kw_node = for_node.make_pydot_node(label = 'for')
        graph.add_node(kw_node)

        identifier_node = for_node.identifier.accept(self, graph)
        assert kw_node and identifier_node
        graph.add_edge(pydot.Edge(kw_node, identifier_node))

        iterable_node = for_node.iterable.accept(self, graph)
        assert iterable_node
        graph.add_edge(pydot.Edge(kw_node, iterable_node))
        body_node = pydot.Node(str(hash((tuple(for_node.body), 'for', graph))), label = 'body')
        graph.add_node(body_node)
        assert body_node
        graph.add_edge(pydot.Edge(kw_node, body_node))
        for stmt in for_node.body:
            stmt_node = stmt.accept(self, graph)
            assert stmt_node
            graph.add_edge(pydot.Edge(body_node, stmt_node))

        return kw_node

    def visitWhile(self, while_node, graph):
        kw_node = while_node.make_pydot_node(label = 'while')
        graph.add_node(kw_node)

        cond_base_node = pydot.Node(str(hash((while_node.condition, 'while'))), label = 'condition')
        graph.add_node(cond_base_node)
        assert kw_node and cond_base_node
        graph.add_edge(pydot.Edge(kw_node, cond_base_node))

        condition_node = while_node.condition.accept(self, graph)
        assert condition_node
        graph.add_edge(pydot.Edge(cond_base_node, condition_node))

        body_node = pydot.Node(str(hash((tuple(while_node.body), 'while'))), label = 'body')
        graph.add_node(body_node)
        assert body_node
        graph.add_edge(pydot.Edge(kw_node, body_node))
        for stmt in while_node.body:
            stmt_node = stmt.accept(self, graph)
            assert stmt_node
            graph.add_edge(pydot.Edge(body_node, stmt_node))

        return kw_node

    def visitPrimitiveType(self, obj_type_node, graph):
        num = obj_type_node.make_pydot_node(fillcolor='burlywood', shape='hexagon', label = f'PrimitiveType: "{ast_nodes.PrimitiveType.inv_data_types[obj_type_node.type]}"')
        graph.add_node(num)
        return num

    def visitFnObj(self, fn_type_node, graph):
        # fn def
        fn_type_graph_node = fn_type_node.make_pydot_node(label = f'FnType')
        graph.add_node(fn_type_graph_node)

        # ret type
        ret_type_base_node = pydot.Node(hash((fn_type_node.ret_type, id(fn_type_node))), label = f'return_type')
        graph.add_node(ret_type_base_node)
        graph.add_edge(pydot.Edge(fn_type_graph_node, ret_type_base_node))
        ret_type_node = fn_type_node.ret_type.accept(self, graph)
        assert fn_type_graph_node and ret_type_node
        graph.add_edge(pydot.Edge(ret_type_base_node, ret_type_node))

        # formals
        formals_node = pydot.Node(hash(tuple(fn_type_node.formals) + (id(fn_type_node),)), label = 'formals')
        graph.add_node(formals_node)

        assert formals_node
        graph.add_edge(pydot.Edge(fn_type_graph_node, formals_node))

        for formal in fn_type_node.formals:
            formal_node = formal.accept(self, graph)
            assert formal_node
            graph.add_edge(pydot.Edge(formals_node, formal_node))

        # body
        body_node = pydot.Node(hash(tuple(fn_type_node.body)), label = 'body')
        graph.add_node(body_node)

        assert body_node
        graph.add_edge(pydot.Edge(fn_type_graph_node, body_node))

        for stmt in fn_type_node.body:
            stmt_node = stmt.accept(self, graph)
            assert stmt_node
            graph.add_edge(pydot.Edge(body_node, stmt_node))

        return fn_type_graph_node

    def visitFnType(self, fn_sig_node, graph):
        data = fn_sig_node.make_pydot_node(label = 'fn_type')
        graph.add_node(data)
        return data

    def visitLiteral(self, literal_node, graph):
        data = literal_node.make_pydot_node(label = f'{ast_nodes.PrimitiveType.inv_data_types[literal_node.type]}_lit: "{literal_node.value}"')
        graph.add_node(data)
        return data

    def visitNumLit(self, num_lit_node, graph):
        return super(ast_nodes.NumLit, num_lit_node).accept(self, graph)

    def visitStrLit(self, str_lit_node, graph):
        return super(ast_nodes.StrLit, str_lit_node).accept(self, graph)

    def visitBoolLit(self, bool_lit_node, graph):
        return super(ast_nodes.BoolLit, bool_lit_node).accept(self, graph)

    def visitNone(self, none_node, graph):
        return super(ast_nodes.None_, none_node).accept(self, graph)