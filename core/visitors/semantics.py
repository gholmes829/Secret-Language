"""

"""

from icecream import ic
from core import nodes
from core.visitors.visitor import Visitor

# multiple inheritance, either disallow ambiguous calls or MRO from left to right of inheritance call
class ScopeStack:
    def __init__(self) -> None:
        self.scopes = [{}]
        self.names = ['globals']

        from core.runtime.builtins import BuiltinCallable
        for builtin in BuiltinCallable.registered:
            self.top[builtin.name] = True
        # add builtins to global here

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

    def resolve(self, node: nodes.ASTNode):
        node.accept(self)

    def declare(self, name):
        assert isinstance(name, str)
        assert name not in self.scopes.top, ic(name)
        self.scopes.top[name] = False

    def define(self, name: nodes.ASTNode):
        assert isinstance(name, str)
        self.scopes.top[name] = True

    def resolve_local(self, node: nodes.ASTNode, node_name):
        # ic(node, node_name)
        for i, (scope, name) in enumerate(list(zip(self.scopes.scopes, self.scopes.names))[::-1][:-1]):
            assert name != 'globals'  # hopefully no one names their function globals until this gets fixed
            if node_name in scope:
                self.interpreter.resolve(node, i)
                break
        else:
            pass

    def resolve_function(self, node: nodes.ASTNode):
        with self.scopes.enter_new(node.ident):
            for formal in node.formals:
                self.declare(formal)
                self.define(formal)
            self.resolve(node.body)

    def visitRoot(self, root_node):
        assert self.scopes
        self.resolve(root_node.globals)

    def visitAssignDecl(self, ad_node):
        # I think this is equiv to varStmt from book
        self.declare(ad_node.lhs)
        self.resolve(ad_node.rhs)  # can skip if enable plain decl wo assign
        self.define(ad_node.lhs)

    def visitVar(self, id_node):
        # I think this is varExpr from book
        if id_node.ident_token in self.scopes.top and not self.scopes.top[id_node.ident_token]:
            raise ValueError('Variable can not reference itself in initializer.')
        self.resolve_local(id_node, id_node.ident_token)

    def visitSuperID(self, super_node):
        pass

    def visitScopedID(self, id_node):
        self.resolve(id_node.object)

    def visitThisID(self, this_id_node):
        self.resolve_local(this_id_node.object, 'this')

    def visitSuperID(self, super_id):
        self.resolve_local(super_id.object, 'super')

    def visitSetStmt(self, set_node):
        self.resolve(set_node.rhs)
        self.resolve(set_node.lhs.object)
        # print(f'Set type for {set_node.lhs.object} in {self.scopes.top}')


    def visitAssign(self, assign_node):
        # should add type define to scopes?
        self.resolve(assign_node.rhs)
        self.resolve_local(assign_node.lhs, assign_node.lhs.name)
        # self.resolve(assign_node.lhs)

    def visitFuncObj(self, fn_obj_node):
        if fn_obj_node.ident:
            self.declare(fn_obj_node.ident.ident_token)
            self.define(fn_obj_node.ident.ident_token)
        self.resolve_function(fn_obj_node)

    def visitClassObj(self, cls_obj_node: nodes.ClassObj):
        self.declare(cls_obj_node)
        self.define(cls_obj_node)
        if cls_obj_node.inheritance:
            self.resolve(cls_obj_node.inheritance)

        if cls_obj_node.inheritance:
            self.scopes.enter_new('super')
            self.scopes.top['super'] = True


        for method in cls_obj_node.body:
            if isinstance(method, nodes.MethodObj):
                try:
                    self.declare(method)  # might be bad
                    self.define(method)
                except AssertionError: pass

        with self.scopes.enter_new(cls_obj_node.name):

            self.scopes.top['this'] = True

            for method in cls_obj_node.body:
                if isinstance(method, nodes.MethodObj):
                    # self.declare(method)  # might be bad
                    # self.define(method)
                    # self.set_type(method, method.type)
                    self.resolve_function(method)
        
        if cls_obj_node.inheritance:
            self.scopes.leave_scope()

            

    def visitNodeList(self, node_list_node):
        for node in node_list_node:
            self.resolve(node)

    def visitIf(self, if_node):
        for branch in if_node.branch_seq:
            self.resolve(branch.cond)
            self.resolve(branch.body)

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
        bin_op_node.type = bin_op_node.res_cast

    def visitUnaryOp(self, un_op_node):
        self.resolve(un_op_node.operand)
        # need to implement theses
        un_op_node.opd_cast, un_op_node.res_cast = \
            un_op_node.type_resolutions[un_op_node.op_str, un_op_node.operand.type]

    def visitCall(self, call_node):
        ic(call_node, call_node.ident, call_node.actuals)
        self.resolve(call_node.ident)  # Var
        self.resolve(call_node.actuals)

    def visitLiteral(self, literal_node):
        raise NotImplementedError

    def visitInt(self, int_node):
        pass

    def visitFloat(self, float_node):
        pass

    def visitStrLit(self, str_lit_node):
        pass

    def visitBoolLit(self, bool_lit_node):
        pass

    def visitNone(self, none_node):
        pass

    def visitPrimitiveType(self, obj_type_node):
        raise NotImplementedError

    def visitFuncType(self, fn_sig_node):
        raise NotImplementedError

    def visitArray(self, array_node):
        pass

    def visitIndex(self, index_node):
        self.resolve(index_node.idx)
        self.resolve(index_node.base)
        index_node.type = self.get_type(index_node.name)
        self.resolve_local(index_node.base, index_node.name)
    
    def visitTryCatch(self, tc_node):
        self.resolve(tc_node.try_)
        self.resolve(tc_node.catch)

    def visitTry(self, try_node):
        self.resolve(try_node.body)

    def visitCatch(self, catch_node):
        # will need to resolve exception(s) in future
        self.resolve(catch_node.body)

    def visitThrow(self, throw_node):
        # will need to resolve exception in future
        pass