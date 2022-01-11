"""

"""


import lark
from abc import ABCMeta, abstractmethod
import pydot
from icecream import ic
from copy import deepcopy

import semantic_analysis as sa

# abstractions
class ASTNode(metaclass = ABCMeta):
    def __init__(self, start_token, end_token) -> None:
        self.start_token = start_token
        self.end_token = end_token

    def to_dot(self, graph: pydot.Graph = None):
        if not graph:
            graph = pydot.Graph(graph_type = 'digraph')
            graph.set_graph_defaults(dpi = 300)
            graph.set_node_defaults(style = 'filled')
            graph.set_edge_defaults()
        return self._to_dot(graph)

    def make_pydot_node(self, *args, **kwargs):
        return pydot.Node(str(hash(self)), *args, **kwargs)

    @abstractmethod
    def interpret(self, symbol_table):
        raise NotImplementedError(type(self))

    @abstractmethod
    def unparsed(self, depth: int = 0):
        raise NotImplementedError

    @abstractmethod
    def _to_dot(self, graph: pydot.Graph = None):
        raise NotImplementedError

    @abstractmethod
    def bind_symbols(self, symbol_table: sa.SymbolTable):
        raise NotImplementedError


# expressions
class Expr(ASTNode):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._value = None
        self._type = None

    def make_pydot_node(self, *args, **kwargs):
        if 'fillcolor' not in kwargs:
            kwargs['fillcolor'] = 'darksalmon'
        return super().make_pydot_node(*args, **kwargs)

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, _value):
        self._value = _value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, type):
        self._type = type


class BinaryOperation(Expr):
    ops = {
        '+': (lambda lhs, rhs: lhs + rhs, 'addition'),
        '-': (lambda lhs, rhs: lhs - rhs, 'subtraction'),
        '*': (lambda lhs, rhs: lhs * rhs, 'multiplication'),
        '/': (lambda lhs, rhs: lhs / rhs, 'division'),
        '==': (lambda lhs, rhs: lhs == rhs, 'eq'),
        '!=': (lambda lhs, rhs: lhs != rhs, 'neq'),
        '<': (lambda lhs, rhs: lhs < rhs, 'lt'),
        '<=': (lambda lhs, rhs: lhs <= rhs, 'lte'),
        '>': (lambda lhs, rhs: lhs > rhs, 'gt'),
        '>=': (lambda lhs, rhs: lhs >= rhs, 'gte'),
        'or': (lambda lhs, rhs: lhs or rhs, 'l_or'),
        'and': (lambda lhs, rhs: lhs and rhs, 'l_and'),
    }

    type_resolutions = {
        ('+', float, float): (float, float, float),
        ('+', float, str): (str, str, str),
        ('+', str, str): (str, str, str),
        ('+', str, float): (str, str, str),
        ('-', float, float): (float, float, float),
        ('*', float, float): (float, float, float),
        ('/', float, float): (float, float, float),
        ('>', float, float): (float, float, bool),
        ('>=', float, float): (float, float, bool),
        ('<', float, float): (float, float, bool),
        ('<=', float, float): (float, float, bool),
        ('==', float, float): (float, float, bool),
        ('==', str, str): (str, str, bool),
        ('!=', float, float): (float, float, bool),
        ('and', bool, bool): (bool, bool, bool),
        ('or', bool, bool): (bool, bool, bool),
    }

    def __init__(self, lhs, op_token, rhs) -> None:
        super().__init__(None, None)
        self.op_str = op_token.value
        self.op, self.op_name = BinaryOperation.ops[op_token.value]
        self.lhs, self.rhs = lhs, rhs

    def bind_symbols(self, symbol_table: sa.SymbolTable):
        self.lhs.bind_symbols(symbol_table)
        self.rhs.bind_symbols(symbol_table)
        self.lhs_cast, self.rhs_cast, self.type = \
            BinaryOperation.type_resolutions[self.op_str, self.lhs.type, self.rhs.type]

    def unparsed(self, depth: int = 0):
        return f'({self.lhs.unparsed(depth)} {self.op_str} {self.rhs.unparsed(depth)})'

    def _to_dot(self, graph: pydot.Graph = None):
        operation_node = self.make_pydot_node(label = f'BinOp: "{self.op_name}"')
        graph.add_node(operation_node)
        lhs_node = self.lhs._to_dot(graph)[1]
        rhs_node = self.rhs._to_dot(graph)[1]
        graph.add_edge(pydot.Edge(operation_node, lhs_node))
        graph.add_edge(pydot.Edge(operation_node, rhs_node))
        return graph, operation_node

    def interpret(self, symbol_table):
        self.lhs.interpret(symbol_table)
        self.rhs.interpret(symbol_table)
        lhs_val = self.lhs.value
        rhs_val = self.rhs.value
        self.unparsed(0)
        self.value = self.type(self.op(self.lhs_cast(lhs_val), self.rhs_cast(rhs_val)))

# references
class Reference(Expr):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='lightgoldenrod', shape='rectangle', **kwargs)

# stmts
class Stmt(ASTNode):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='lightblue', **kwargs)

# types
class ObjType(ASTNode):

    data_types = {
        'num': float,
        'str': str,
        'bool': bool,
        'void': None,
    }

    inv_data_types = {v: k for k, v in data_types.items()}

    def __init__(self, scope_modifier, token, execution_modifier) -> None:
        super().__init__(None, None)
        self.type = ObjType.data_types[token.value]
        self.scope_modifier = scope_modifier
        self.execution_modifier = execution_modifier

    def bind_symbols(self, _):
        pass

    def unparsed(self, depth: int = 0):
        return ObjType.inv_data_types[self.type]

    def interpret(self, symbol_table): pass

    def _to_dot(self, graph: pydot.Graph = None):
        num = super().make_pydot_node(fillcolor='burlywood', shape='hexagon', label = f'ObjType: "{ObjType.inv_data_types[self.type]}"')
        graph.add_node(num)
        return graph, num

# literals
class Literal(Expr):
    def __init__(self, token, value, lit_type, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.token = token
        self._value = value
        self._type = lit_type

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='lightgreen', shape='diamond', **kwargs)

    def bind_symbols(self, _): pass

    def _to_dot(self, graph: pydot.Graph = None):
        data = self.make_pydot_node(label = f'{ObjType.inv_data_types[self.type]}: "{self.value}"')
        graph.add_node(data)
        return graph, data

    def interpret(self, symbol_table): pass

# root of program
class Root(ASTNode):
    def __init__(self, *stmts) -> None:
        super().__init__(None, None)
        self.stmts = stmts

    def unparsed(self, depth: int = 0):
        return '\n'.join(stmt.unparsed(depth) for stmt in self.stmts)

    def bind_symbols(self, symbol_table: sa.SymbolTable):
        symbol_table.enter_scope('globals')
        for stmt in self.stmts:
            stmt.bind_symbols(symbol_table)
        symbol_table.leave_scope()
        assert not symbol_table.table_chain

    def _to_dot(self, graph: pydot.Graph = None):
        root_node = self.make_pydot_node(label = 'root')
        graph.add_node(root_node)
        stmt_nodes = [stmt._to_dot(graph)[1] for stmt in self.stmts]
        for stmt_node in stmt_nodes: graph.add_edge(pydot.Edge(root_node, stmt_node))
        return graph, root_node

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='red', **kwargs)

    def interpret(self, symbol_table):
        fn_sym = symbol_table['globals', 'main']
        start = None
        for stmt in self.stmts:
            if isinstance(stmt, FnDef) and stmt.symbol == fn_sym:
                start = stmt
                break
        start.interpret(symbol_table)


class FnDef(Stmt):
    def __init__(self, decorator, ret_type, identifier, formals, body) -> None:
        super().__init__(None, None)
        self.decorator = decorator
        self.ret_type = ret_type
        self.identifier = identifier
        self.name = identifier.name
        self.formals = formals.children if formals else []
        self.body = body.children
        self.symbol = None

    def unparsed(self, depth: int = 0):
        base_depth_str = depth * '\t'
        ret_type_unparsed = base_depth_str + self.ret_type.unparsed(depth)
        id_unparsed = self.identifier.unparsed(depth)
        formals_unparsed = ', '.join(formal.unparsed(depth) for formal in self.formals)
        body_unparsed = '\n'.join(stmt.unparsed(depth + 1) for stmt in self.body)

        return f'\n{ret_type_unparsed} {id_unparsed}({formals_unparsed}) {{\n{body_unparsed}\n{base_depth_str}}}\n'

    def bind_symbols(self, symbol_table: sa.SymbolTable):
        sym = symbol_table.add_fn(self.name, [formal.type for formal in self.formals], self.ret_type.type, self.body, self.formals)
        self.symbol = sym
        symbol_table.enter_scope(str(self.name))
        for formal in self.formals:
            formal.bind_symbols(symbol_table)
        for stmt in self.body:
            stmt.bind_symbols(symbol_table)
        symbol_table.leave_scope()

    def _to_dot(self, graph: pydot.Graph = None):
        # fn def
        fn_def_node = self.make_pydot_node(label = f'FnDef: "{self.name}"')
        graph.add_node(fn_def_node)

        # ret type
        ret_type_node = self.ret_type._to_dot(graph)[1]
        graph.add_edge(pydot.Edge(fn_def_node, ret_type_node))

        # formals
        formals_node = pydot.Node(hash(tuple(self.formals) + (self.name,)), label = 'formals')
        graph.add_node(formals_node)

        graph.add_edge(pydot.Edge(fn_def_node, formals_node))

        for formal in self.formals:
            formal_node = formal._to_dot(graph)[1]
            graph.add_edge(pydot.Edge(formals_node, formal_node))

        # body
        body_node = pydot.Node(hash(tuple(self.body)), label = 'body')
        graph.add_node(body_node)

        graph.add_edge(pydot.Edge(fn_def_node, body_node))

        for stmt in self.body:
            stmt_node = stmt._to_dot(graph)[1]
            graph.add_edge(pydot.Edge(body_node, stmt_node))

        return graph, fn_def_node

    def interpret(self, symbol_table):
        for stmt in self.body:
            stmt.interpret(symbol_table)


class ID(Reference):
    def __init__(self, name) -> None:
        super().__init__(None, None)
        self.name = name
        self._type = None
        self.symbol = None

    def bind_symbols(self, symbol_table: sa.SymbolTable):
        try:
            self.symbol = symbol_table[self.name]
            self.type = self.symbol.type
        except KeyError:
            assert self.type, (self.name, self.type)
            try: name = self.name
            except: name = str(self.name)
            self.symbol = symbol_table.add_var(name, self.type)


    def unparsed(self, depth: int = 0): return str(self.name)

    def interpret(self, symbol_table): pass

    def _to_dot(self, graph: pydot.Graph = None):
        node = self.make_pydot_node(label = f'ID: "{self.name}"\nType: {ObjType.inv_data_types[self.type]}')
        graph.add_node(node)
        return graph, node

    @property
    def value(self):
        return self.symbol.value

    @value.setter
    def value(self, _value):
        self.symbol.value = _value



def typed_formal(_, _type, _identifier):
    _type, _identifier
    _identifier.type = _type.type
    return _identifier


# statements
class AssignStmt(Stmt):
    def __init__(self, lhs, rhs) -> None:
        super().__init__(None, None)
        self.lhs = lhs
        self.rhs = rhs
        self.lhs.type = rhs.type

    def unparsed(self, depth: int = 0):
        return depth * '\t' + f'{self.lhs.unparsed(depth)} = {self.rhs.unparsed(depth)}'

    def bind_symbols(self, symbol_table):
        self.rhs.bind_symbols(symbol_table)
        self.lhs.type = self.rhs.type
        self.lhs.bind_symbols(symbol_table)
    
    def _to_dot(self, graph: pydot.Graph = None):
        assign_node = self.make_pydot_node(label = 'assign_stmt')
        graph.add_node(assign_node)
        lhs_node = self.lhs._to_dot(graph)[1]
        rhs_node = self.rhs._to_dot(graph)[1]
        graph.add_edge(pydot.Edge(assign_node, lhs_node))
        graph.add_edge(pydot.Edge(assign_node, rhs_node))
        return graph, assign_node

    def interpret(self, symbol_table):
        self.rhs.interpret(symbol_table)
        self.lhs.value = self.rhs.value


class Print(Stmt):
    def __init__(self, expr) -> None:
        super().__init__(None, None)
        self.expr = expr

    def unparsed(self, depth: int = 0):
        return depth * '\t' + f'print({self.expr.unparsed(depth)})'

    def bind_symbols(self, symbol_table):
        self.expr.bind_symbols(symbol_table)

    def _to_dot(self, graph: pydot.Graph = None):
        print_node = self.make_pydot_node(label = 'print_stmt')
        graph.add_node(print_node)
        expr_node = self.expr._to_dot(graph)[1]
        graph.add_edge(pydot.Edge(print_node, expr_node))
        return graph, print_node

    def interpret(self, symbol_table):
        self.expr.interpret(symbol_table)
        print(self.expr.value, flush=True)


# literals
class NumLit(Literal):
    type = float
    def __init__(self, num_token) -> None:
        super().__init__(num_token, float(num_token.value), float, None, None)

    def unparsed(self, depth: int = 0):
        return str(self.value)


class StrLit(Literal):
    def __init__(self, string_token: lark.Token) -> None:
        super().__init__(string_token, string_token.value[1:-1], str, None, None)
        self.type = str

    def unparsed(self, depth: int = 0):
        return '"' + self.value + '"'


class BoolLit(Literal):
    str_to_val = {
        'true': True,
        'false': False
    }

    def __init__(self, bool_token) -> None:
        value = BoolLit.str_to_val[bool_token.value]
        super().__init__(bool_token, value, bool, None, None)

    def unparsed(self, depth: int = 0):
        return self.token


class For(Stmt):
    def __init__(self, identifier, iterable, body) -> None:
        super().__init__(None, None)
        self.identifier = identifier
        self.iterable = iterable
        self.body = body.children if body else []

    def unparsed(self, depth: int = 0):
        indent_offset = depth * '\t'
        body_unparsed = ('\n' + indent_offset).join(stmt.unparsed(depth + 1) for stmt in self.body)
        return depth * '\t' + f'for {self.identifier.unparsed(depth)} in {self.iterable.unparsed(depth)} {{\n{body_unparsed}\n{indent_offset}}}'

    def bind_symbols(self, symbol_table: sa.SymbolTable):
        self.iterable.bind_symbols(symbol_table)
        self.identifier.type = self.iterable.type
        self.identifier.bind_symbols(symbol_table)
        for stmt in self.body:
            stmt.bind_symbols(symbol_table)

    def _to_dot(self, graph: pydot.Graph = None):
        kw_node = self.make_pydot_node(label = 'for')
        graph.add_node(kw_node)

        identifier_node = self.identifier._to_dot(graph)[1]
        graph.add_edge(pydot.Edge(kw_node, identifier_node))

        iterable_node = self.iterable._to_dot(graph)[1]
        graph.add_edge(pydot.Edge(kw_node, iterable_node))
        body_node = pydot.Node(str(hash((tuple(self.body), 'for', graph))), label = 'body')
        graph.add_node(body_node)
        graph.add_edge(pydot.Edge(kw_node, body_node))
        for stmt in self.body:
            stmt_node = stmt._to_dot(graph)[1]
            graph.add_edge(pydot.Edge(body_node, stmt_node))

        return graph, kw_node

    def interpret(self, symbol_table):
        self.identifier.value = 0
        self.iterable.interpret(symbol_table)
        for i in range(int(self.iterable.value)):
            for stmt in self.body:
                stmt.interpret(symbol_table)
            self.iterable.interpret(symbol_table)
            self.identifier.value = i + 1



class While(Stmt):
    def __init__(self, condition, body) -> None:
        self.condition = condition
        self.body = body.children if body else []
        super().__init__(None, None)

    def unparsed(self, depth: int = 0):
        body_unparsed = '\n\t'.join(stmt.unparsed(depth) for stmt in self.body)
        return f'while {self.condition.unparsed(depth)} {{\n\t{body_unparsed}\n}}'

    def bind_symbols(self, symbol_table: sa.SymbolTable):
        self.condition.bind_symbols(symbol_table)
        for stmt in self.body:
            stmt.bind_symbols(symbol_table)

    def _to_dot(self, graph: pydot.Graph = None):
        kw_node = self.make_pydot_node(label = 'while')
        graph.add_node(kw_node)

        cond_base_node = pydot.Node(str(hash((self.condition, 'while'))), label = 'condition')
        graph.add_node(cond_base_node)
        graph.add_edge(pydot.Edge(kw_node, cond_base_node))

        condition_node = self.condition._to_dot(graph)[1]
        graph.add_edge(pydot.Edge(cond_base_node, condition_node))

        body_node = pydot.Node(str(hash((tuple(self.body), 'while'))), label = 'body')
        graph.add_node(body_node)
        graph.add_edge(pydot.Edge(kw_node, body_node))
        for stmt in self.body:
            stmt_node = stmt._to_dot(graph)[1]
            graph.add_edge(pydot.Edge(body_node, stmt_node))

        return graph, kw_node

    def interpret(self, symbol_table):
        self.condition.interpret(symbol_table)

        while self.condition.value:
            for stmt in self.body:
                stmt.interpret(symbol_table)
            self.condition.interpret(symbol_table)

class ReturnInterrupt(Exception):
    def __init__(self, ret_val) -> None:
        super().__init__('Returning!!!')
        self.ret_val = ret_val

class Return(Stmt):
    def __init__(self, expr) -> None:
        super().__init__(expr.start_token, expr.end_token)
        self.expr = expr
        self.value = None
        
    def bind_symbols(self, symbol_table: sa.SymbolTable):
        self.expr.bind_symbols(symbol_table)

    def unparsed(self, depth: int = 0):
        return depth * '\t' + f'return {self.expr.unparsed(depth)}'

    def set_value(self, value): self.value = value 
    def get_value(self): return self.value

    def _to_dot(self, graph: pydot.Graph = None):
        return_node = self.make_pydot_node(label = 'return_stmt')
        graph.add_node(return_node)

        expr_node = self.expr._to_dot(graph)[1]
        graph.add_edge(pydot.Edge(return_node, expr_node))

        return graph, return_node

    def interpret(self, symbol_table):
        self.expr.interpret(symbol_table)
        self.set_value(self.expr.value)
        raise ReturnInterrupt(self.expr.value)


class Call(Expr):
    def __init__(self, identifier, actuals) -> None:
        super().__init__(identifier.start_token, actuals.children[-1].end_token if actuals.children else identifier.end_token)
        self.identifier = identifier
        self.type = None
        self.actuals = actuals.children if actuals else []
        self.values = []

    def unparsed(self, depth: int = 0):
        id_unparsed = self.identifier.unparsed(depth)
        actuals_unparsed = ", ".join(formal.unparsed(depth) for formal in self.actuals)
        return f'{id_unparsed}({actuals_unparsed})'

    def bind_symbols(self, symbol_table: sa.SymbolTable):
        for actual in self.actuals:
            actual.bind_symbols(symbol_table)

        self.type = symbol_table[self.identifier.name].ret_type

    @property
    def value(self):
        return self.values.pop()

    @value.setter
    def value(self, value):
        try:
            self.values.append(value)
        except AttributeError:
            pass

    def _to_dot(self, graph: pydot.Graph = None):
        # fn def
        call_node = self.make_pydot_node(label = f'call: "{self.identifier.name}"')
        graph.add_node(call_node)

        # actuals
        actuals_node = pydot.Node(hash(tuple(self.actuals) + (self.identifier, self.type)), label = 'actuals', fillcolor = 'plum')
        graph.add_node(actuals_node)
        graph.add_edge(pydot.Edge(call_node, actuals_node))

        for actual in self.actuals:
            actual_node = actual._to_dot(graph)[1]
            graph.add_edge(pydot.Edge(actuals_node, actual_node))
        
        return graph, call_node


    def interpret(self, symbol_table):
        for actual in self.actuals:
            actual.interpret(symbol_table)

        fn_sym = deepcopy(symbol_table['globals', self.identifier.name])
        fn_body = fn_sym.body
        formals = fn_sym.formals

        for formal, actual in zip(formals, self.actuals):
            formal.symbol.value = actual.value

        for stmt in fn_body:
            try:
                stmt.interpret(symbol_table)
            except ReturnInterrupt as RI:
                self.value = RI.ret_val
                break



class If(Stmt):
    def __init__(self, if_block, else_if_blocks, else_block) -> None:
        super().__init__(  # this is WRONG, TODO
            None,
            None
        )
        
        self.if_sequence = []

        if_cond = if_block.children[0]
        if_body_stmts = if_block.children[1].children
        
        self.if_sequence.append((if_cond, if_body_stmts, 'if'))

        if else_if_blocks:
            for else_if_block in else_if_blocks.children:
                else_if_cond = else_if_block.children[0]
                else_if_body_stmts = else_if_block.children[1].children
                self.if_sequence.append((else_if_cond, else_if_body_stmts, 'else if'))

        if else_block:
            else_body_stmts = else_block.children[0].children
            self.if_sequence.append((None, else_body_stmts, 'else'))


    def unparsed(self, depth: int = 0):
        res = ''
        for cond, body, block_type in self.if_sequence:
            res += depth * '\t' + block_type
            if cond:
                res += ' ' + cond.unparsed(depth)

            res += ' {\n' + '\n'.join([stmt.unparsed(depth + 1) for stmt in body])
            res += '\n' + (depth * '\t') + '}\n'

        return res

    def bind_symbols(self, symbol_table: sa.SymbolTable):
        for cond, body, block_type in self.if_sequence:
            if cond:
                cond.bind_symbols(symbol_table)
            for stmt in body: stmt.bind_symbols(symbol_table)       

    def _to_dot(self, graph: pydot.Graph = None):
        if_stmt_node = self.make_pydot_node(label = 'if_stmt')
        graph.add_node(if_stmt_node)

        for cond, body, block_type in self.if_sequence:
            base_node = pydot.Node(hash((cond, block_type)), label = block_type, fillcolor = 'plum')
            graph.add_node(base_node)
            graph.add_edge(pydot.Edge(if_stmt_node, base_node))

            if cond:
                cond_node = pydot.Node(hash((cond, block_type, 'condition')), label = 'condition')
                graph.add_node(cond_node)
                graph.add_edge(pydot.Edge(base_node, cond_node))

                cond_expr_node = cond._to_dot(graph)[1]
                graph.add_edge(pydot.Edge(cond_node, cond_expr_node))
            
            body_node = pydot.Node(hash((tuple(body), block_type)), label = 'body')
            graph.add_node(body_node)
            graph.add_edge(pydot.Edge(base_node, body_node))

            for stmt in body:
                stmt_node = stmt._to_dot(graph)[1]
                graph.add_edge(pydot.Edge(body_node, stmt_node))

        return graph, if_stmt_node


    def interpret(self, symbol_table):
        for cond, body, block_type in self.if_sequence:
            if cond:
                cond.interpret(symbol_table)
                if not cond.value:
                    continue
            
            for stmt in body:
                stmt.interpret(symbol_table)

            break


class ClsDef(Stmt):
    def __init__(self, decorator, _id, super_class, *methods) -> None:
        super().__init__(_id.line, _id.column)
        self.decorator = decorator
        self._id = _id
        self.super_class = super_class
        self.methods = methods

    def bind_symbols(self, symbol_table: sa.SymbolTable):
        symbol_table.add_cls(self._id.name, types.ClassType(self._id.name))
        symbol_table.enter_scope(self._id.name)

        for method in self.methods:
            method.bind_symbols(symbol_table)

        symbol_table.leave_scope()



    def unparsed(self, depth: int = 0):
        return 'NOT IMPLEMENTED'

    def _to_dot(self, graph: pydot.Graph = None):
        class_def_node = self.make_pydot_node(label = f'cls_def: "{self._id.name}"')
        graph.add_node(class_def_node)

        for method in self.methods:
            method_node = method._to_dot(graph)[1]
            graph.add_edge(pydot.Edge(class_def_node, method_node))

        return graph, class_def_node
