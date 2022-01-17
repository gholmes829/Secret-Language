"""

"""

from icecream import ic
from core import ast_nodes

from core.ast_visitors.visitor import Visitor



class ScopeStack:
    def __init__(self) -> None:
        self.scopes = [{}]
        self.names = ['globals']

    @property
    def top(self):
        return self.scopes[-1]

    def enter_new(self, name: str = None):
        self.scopes.append({})
        self.names.append(name)
        return self

    def leave_scope(self):
        self.scopes.pop()
        self.names.pop()

    def __enter__(self) -> None:
        return self

    def __exit__(self, *_: list) -> None:
        self.leave_scope()

    def __iter__(self):
        return self.scopes.__iter__()

    def __reversed__(self):
        return self.scopes.__reversed__()

    def __bool__(self):
        return bool(self.scopes)

    def __len__(self):
        return len(self.scopes)



class SemanticAnalyzer(Visitor):
    def __init__(self, interpreter) -> None:
        super().__init__()
        self.scopes = ScopeStack()
        self.interpreter = interpreter

    def resolve(self, node: ast_nodes.ASTNode):
        node.accept(self)

    def declare(self, node: ast_nodes.ASTNode):
        assert node.name not in self.scopes.top, node.name
        self.scopes.top[node.name] = {'init': False, 'type': node.type}

    def define(self, node: ast_nodes.ASTNode):
        self.scopes.top[node.name]['init'] = True

    def get_type(self, node):
        if node.name == 'clock': return float
        elif node.name == 'print': return 'void'  # hard coded for now, need to find way to add builtins to semantic analysis

        for scope in reversed(self.scopes):
            if node.name in scope:
                return scope[node.name]['type']
        raise ValueError(f'Could not retrieve type for "{node.name}"')

    def set_type(self, node, type):

        if node.name in {'clock', 'print'}: return float  # hard coded for now, need to find way to add builtins to semantic analysis

        for scope in reversed(self.scopes):
            if node.name in scope:
                return scope[node.name]['type']
        raise ValueError(f'Could not retrieve type for "{node.name}"')

    def resolve_local(self, node: ast_nodes.ASTNode):
        assert hasattr(node, 'name')
        if not hasattr(node, 'name'):
            return  # move this to caller side? maybe not needed
        for i, (scope, name) in enumerate(list(zip(self.scopes.scopes, self.scopes.names))[::-1][:-1]):
            if node.name in scope:
                self.interpreter.resolve(node, i)  # whats this?
                break

    def resolve_function(self, node: ast_nodes.ASTNode):
        with self.scopes.enter_new(node.name):
            for formal in node.formals:
                self.declare(formal)
                self.define(formal)
            self.resolve(node.body)

    def visitRoot(self, root_node):
        assert self.scopes
        for glbl in root_node.globals:
            self.resolve(glbl)

    def visitAssignDecl(self, ad_node):
        # I think this is equiv to varStmt from book
        ad_node.lhs.type = ad_node.rhs.type
        self.declare(ad_node.lhs)
        self.resolve(ad_node.rhs)  # skip if init null and can just decl wo assign
        self.define(ad_node.lhs)

    def visitID(self, id_node):
        # I think this is varExpr from book
        if id_node.name in self.scopes.top and not self.scopes.top[id_node.name]['init']:
            raise ValueError('Variable can not reference itself in initializer.')
        id_node.type = self.get_type(id_node)
        self.resolve_local(id_node)

    def visitAssign(self, assign_node):
        # should add type define to scopes?
        assign_node.lhs.type = assign_node.rhs.type
        self.resolve(assign_node.rhs)
        self.resolve_local(assign_node.lhs)

    def visitFnObj(self, fn_obj_node):
        self.resolve_function(fn_obj_node)

    def visitNodeList(self, node_list_node):
        for node in node_list_node:
            self.resolve(node)

    def visitIf(self, if_node):
        for branch in if_node.branch_seq:
            self.resolve(branch.cond)
            self.resolve(branch.body)

    def visitFor(self, for_node):
        # need to desugarrrrr
        self.declare(for_node.identifier)
        self.resolve(for_node.iterable)
        self.define(for_node.identifier)
        self.resolve(for_node.body)

    def visitReturn(self, return_node):
        self.resolve(return_node.expr)

    def visitWhile(self, while_node):
        self.resolve(while_node.condition)
        self.resolve(while_node.body)

    def visitBinOp(self, bin_op_node):
        self.resolve(bin_op_node.lhs)
        self.resolve(bin_op_node.rhs)
        bin_op_node.lhs_cast, bin_op_node.rhs_cast, bin_op_node.res_cast = \
            bin_op_node.type_resolutions[bin_op_node.op_str, bin_op_node.lhs.type, bin_op_node.rhs.type]

    def visitUnaryOp(self, un_op_node):
        self.resolve(un_op_node.operand)
        # need to implement theses
        un_op_node.opd_cast, un_op_node.res_cast = \
            un_op_node.type_resolutions[un_op_node.op_str, un_op_node.lhs.type, un_op_node.rhs.type]

    def visitCall(self, call_node):
        self.resolve(call_node.callee)
        self.resolve(call_node.actuals)
        call_node.type = self.get_type(call_node.callee)

    def visitLiteral(self, literal_node):
        raise NotImplementedError

    def visitNumLit(self, num_lit_node):
        pass

    def visitStrLit(self, str_lit_node):
        pass

    def visitBoolLit(self, bool_lit_node):
        pass

    def visitNone(self, none_node):
        pass

    def visitPrimitiveType(self, obj_type_node):
        raise NotImplementedError

    def visitFnType(self, fn_sig_node):
        raise NotImplementedError