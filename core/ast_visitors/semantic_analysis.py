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
    def __init__(self) -> None:
        super().__init__()
        self.scopes = ScopeStack()

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

    def resolve_local(self, node: ast_nodes.ASTNode):
        if not hasattr(node, 'name'):
            return
        for i, scope in enumerate(reversed(self.scopes)):
            if node.name in scope:
                # interpreter.resolve(node, i)
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
        ad_node.lhs.type = ad_node.rhs.type
        self.declare(ad_node.lhs)
        self.resolve(ad_node.rhs)
        self.define(ad_node.lhs)

    def visitID(self, id_node):
        if id_node.name in self.scopes.top and not self.scopes.top[id_node.name]:
            raise ValueError('Variable can not reference itself in initializer.')
        id_node.type = self.get_type(id_node)
        self.resolve_local(id_node)

    def visitAssign(self, assign_node):
        #print()
        #ic(assign_node.rhs, assign_node.rhs.type)
        #ic(assign_node.lhs, assign_node.lhs.type)
        # should add type define to scopes?
        assign_node.lhs.type = assign_node.rhs.type
        self.resolve(assign_node.rhs)
        self.resolve_local(assign_node.rhs)

    def visitFnObj(self, fn_obj_node):
        #ic(self.scopes.top)
        #self.declare(fn_obj_node)
        #self.define(fn_obj_node)
        self.resolve_function(fn_obj_node)

    def visitNodeList(self, node_list_node):
        for node in node_list_node:
            self.resolve(node)











    def visitPrint(self, print_node):
        print_node.expr.accept(self)

    def visitBinOp(self, bin_op_node):
        self.resolve(bin_op_node.lhs)
        self.resolve(bin_op_node.rhs)
        #ic(bin_op_node.lhs, bin_op_node.lhs.type)
        #ic(bin_op_node.rhs, bin_op_node.rhs.type)
        bin_op_node.lhs_cast, bin_op_node.rhs_cast, bin_op_node.res_cast = \
            bin_op_node.type_resolutions[bin_op_node.op_str, bin_op_node.lhs.type, bin_op_node.rhs.type]
        

    def visitCall(self, call_node):
        for arg in call_node.actuals:
            self.resolve(arg)
        call_node.type = self.get_type(call_node.callee)
        # self.resolve(call_node.callee)

    def visitReturn(self, return_node):
        return_node.expr.accept(self)

    def visitIf(self, if_node):
        for branch in if_node.branch_seq:
            self.resolve(branch.cond)

            for stmt in branch.body:
                self.resolve(stmt)

    def visitFor(self, for_node):
        for_node.iterable.accept(self)
        for_node.identifier.type = for_node.iterable.type
        for_node.identifier.accept(self)
        for stmt in for_node.body:
            stmt.accept(self)


    def visitWhile(self, while_node):
        while_node.condition.accept(self)
        for stmt in while_node.body:
            stmt.accept(self)

    def visitPrimitiveType(self, obj_type_node):
        raise NotImplementedError


    def visitFnType(self, fn_sig_node):
        pass

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