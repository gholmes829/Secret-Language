"""

"""

from icecream import ic
from core import ast_nodes
from core.ast_nodes.exprs import ThisID

from core.ast_visitors.visitor import Visitor



class ScopeStack:
    def __init__(self) -> None:
        self.scopes = [{}]
        self.names = ['globals']
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

    def resolve(self, node: ast_nodes.ASTNode):
        node.accept(self)

    def declare(self, node: ast_nodes.ASTNode):
        assert node.name not in self.scopes.top, node.name
        self.scopes.top[node.name] = {'init': False, 'type': node.type}

    def define(self, node: ast_nodes.ASTNode):
        self.scopes.top[node.name]['init'] = True

    def get_type(self, name):
        class Dummy1:
            def __init__(self, val) -> None:
                self.type = val
        class Dummy2:
            def __init__(self, val) -> None:
                self.ret_type = Dummy1(val)
        if name == 'clock': return Dummy2(float)
        elif name == 'print': return Dummy2('void')  # hard coded for now, need to find way to add builtins to semantic analysis

        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]['type']
        raise ValueError(f'Could not retrieve type for "{name}"')

    def set_type_inst(self, name, type_):  # when this.field is used as opposed to obj.field
        for scope in reversed(self.scopes):
            if 'this' in scope:
                scope[name] = {'init': True, 'type': type_}
                return
        raise ValueError(f'Could not set type for "{name}"')

    def set_type(self, name, type_):
        for scope in reversed(self.scopes):
            if name in scope:
                scope[name]['type'] = type_
                return
        raise ValueError(f'Could not set type for "{name}"')

    def resolve_local(self, node: ast_nodes.ASTNode, node_name):
        assert hasattr(node, 'name')
        for i, (scope, name) in enumerate(list(zip(self.scopes.scopes, self.scopes.names))[::-1][:-1]):
            assert name != 'globals'  # hopefully no one names their function globals until this gets fixed
            if node_name in scope:
                self.interpreter.resolve(node, i)
                break
        else:
            pass

    def resolve_function(self, node: ast_nodes.ASTNode):
        with self.scopes.enter_new(node.name):
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
        if isinstance(ad_node.rhs, (ast_nodes.FnObj, ast_nodes.ClassObj, ast_nodes.MethodObj)):
            # have to do this since desugared fn def ...maybe not a good idea in retrospect
            # otherwise have issue with recursion and closures depending on placement of set type stmt
            try:
                self.set_type(ad_node.lhs.name, ad_node.rhs.type)
            except Exception as e:
                pass
                raise
        self.resolve(ad_node.rhs)  # can skip if enable plain decl wo assign
        self.set_type(ad_node.lhs.name, ad_node.rhs.type)
        self.define(ad_node.lhs)

    def visitID(self, id_node):
        # ic(id_node)
        # I think this is varExpr from book
        if id_node.name in self.scopes.top and not self.scopes.top[id_node.name]['init']:
            raise ValueError('Variable can not reference itself in initializer.')

        id_node.type = self.get_type(id_node.name)  # hopefully not needed after type resolution
        self.resolve_local(id_node, id_node.name)

    def visitSuperID(self, super_node):
        pass

    def visitScopedID(self, id_node):
        try:
            id_node.type = self.get_type(id_node.name)
        except: pass
        self.resolve(id_node.object)

    def visitThisID(self, this_id_node):
        self.resolve_local(this_id_node.object, 'this')

    def visitSuperID(self, super_id):
        self.resolve_local(super_id.object, 'super')

    def visitSetStmt(self, set_node):
        self.resolve(set_node.rhs)
        self.resolve(set_node.lhs.object)
        #ic(type(set_node.lhs.object))
        if isinstance(set_node.lhs.object, ThisID):
            self.set_type_inst(set_node.lhs.object.name, set_node.rhs.type)
        else:
            self.set_type(set_node.lhs.object.name, set_node.rhs.type)
        # print(f'Set type for {set_node.lhs.object} in {self.scopes.top}')


    def visitAssign(self, assign_node):
        # should add type define to scopes?
        self.resolve(assign_node.rhs)
        self.set_type(assign_node.lhs.name, assign_node.rhs.type)
        self.resolve_local(assign_node.lhs, assign_node.lhs.name)

    def visitFnObj(self, fn_obj_node):
        self.resolve_function(fn_obj_node)

    def visitClassObj(self, cls_obj_node: ast_nodes.ClassObj):
        self.declare(cls_obj_node)
        self.define(cls_obj_node)
        if cls_obj_node.inheritance:
            self.resolve(cls_obj_node.inheritance)

        if cls_obj_node.inheritance:
            self.scopes.enter_new('super')
            self.scopes.top['super'] = {'init': True, 'type': cls_obj_node.inheritance.type}

        self.set_type(cls_obj_node.name, cls_obj_node.type)

        for method in cls_obj_node.body:
            if isinstance(method, ast_nodes.MethodObj):
                try:
                    self.declare(method)  # might be bad
                    self.define(method)
                    self.set_type(method.name, method.type)
                except AssertionError: pass

        with self.scopes.enter_new(cls_obj_node.name):

            self.scopes.top['this'] = {'init': True, 'type': cls_obj_node.type}

            for method in cls_obj_node.body:
                if isinstance(method, ast_nodes.MethodObj):
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
        #ic(bin_op_node.lhs)
        #ic(bin_op_node.lhs.type)
        self.resolve(bin_op_node.lhs)
        self.resolve(bin_op_node.rhs)
        bin_op_node.lhs_cast, bin_op_node.rhs_cast, bin_op_node.res_cast = \
            bin_op_node.type_resolutions[bin_op_node.op_str, bin_op_node.lhs.type, bin_op_node.rhs.type]
        bin_op_node.type = bin_op_node.res_cast

    def visitUnaryOp(self, un_op_node):
        self.resolve(un_op_node.operand)
        # need to implement theses
        un_op_node.opd_cast, un_op_node.res_cast = \
            un_op_node.type_resolutions[un_op_node.op_str, un_op_node.lhs.type, un_op_node.rhs.type]

    def visitCall(self, call_node):
        self.resolve(call_node.name)
        self.resolve(call_node.actuals)
        type_ = self.get_type(call_node.name.name).ret_type.type
        call_node.type = type_

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