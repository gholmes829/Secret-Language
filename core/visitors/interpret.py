"""

"""

from icecream import ic
from pipe import traverse, where

from core.runtime import *
from core.visitors.visitor import Visitor
from core import nodes

# could make builtins their own special scope before globals


class Interpreter(Visitor):
    def __init__(self) -> None:
        super().__init__()
        self.prev_envs = []
        self.globals = Environment('globals')
        self.locals = {}  # book calls these locals bc they didn't analyze things in global scope, might cause bugs
        self.env = self.globals

    def interpret(self, node: nodes.ASTNode):
        return node.accept(self)
    
    def __call__(self, node):
        self.interpret(node)

    def enter_scope(self, name, env = None):
        self.prev_envs.append(self.env)
        self.env = Environment(name, env or self.env)
        return self

    def exit_scope(self):
        self.env = self.prev_envs.pop()

    def resolve(self, expr, depth):
        self.locals[expr] = depth  # should type also be added here like {depth: depth, type: type}

    def look_up_var(self, node, name):
        if node in self.locals:
            dist = self.locals[node]
            return self.env.getAt(dist, name)
        else:
            return self.globals.get(name)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.exit_scope()

    def visitLiteral(self, literal_node: nodes.Literal):
        return literal_node.value

    def visitNumLit(self, num_lit_node):
        return self.interpret(super(nodes.NumLit, num_lit_node))

    def visitStrLit(self, str_lit_node):
        return self.interpret(super(nodes.StrLit, str_lit_node))

    def visitBoolLit(self, bool_lit_node):
        return self.interpret(super(nodes.BoolLit, bool_lit_node))

    def visitNone(self, none_node):
        return self.interpret(super(nodes.None_, none_node))

    def visitUnaryOp(self, unary_node: nodes.UnaryOp):
        value = unary_node.opd_cast(self.interpret(unary_node.operand))
        return unary_node.res_cast(unary_node.op(value))

    def visitBinOp(self, bin_op_node: nodes.BinOp):
        lhs_value = bin_op_node.lhs_cast(self.interpret(bin_op_node.lhs))
        rhs_value = bin_op_node.rhs_cast(self.interpret(bin_op_node.rhs))
        return bin_op_node.res_cast(bin_op_node.op(lhs_value, rhs_value))

    def visitAssignDecl(self, ad_node):
        val = self.interpret(ad_node.rhs)
        self.env.define(ad_node.lhs.name, val)

    def visitID(self, id_node):
        return self.look_up_var(id_node, id_node.name)
        # return self.env.get(id_node.name)  # pre-bind version

    def visitThisID(self, this_id_node):
        return self.look_up_var(this_id_node.object, 'this')

    def visitScopedID(self, id_node: nodes.ScopedID):
        instance = self.interpret(id_node.object)
        if isinstance(id_node.object, nodes.SuperID):
            return instance
        return instance.get(id_node.name)

    def visitSetStmt(self, set_node):
        instance = self.interpret(set_node.lhs.object)
        val = self.interpret(set_node.rhs)
        instance.set(set_node.lhs.name, val)

    def visitSuperID(self, super_node):
        dist = self.locals[super_node.object]
        superclass = self.env.getAt(dist, 'super')

        object_ = self.env.getAt(dist - 1, 'this')
        # add support for static cls vars
        method = superclass.find_method(super_node.name)
        return method.bind(object_)

    def visitAssign(self, assign_node):
        lhs_val = self.interpret(assign_node.lhs)
        val = self.interpret(assign_node.rhs)
        assign_node.lhs.type = assign_node.rhs.type  # is this necessary?
        if assign_node.lhs in self.locals:


            if isinstance(assign_node.lhs, nodes.Index):
                array, idx = lhs_val
                array[idx] = val
                return val


            dist = self.locals[assign_node.lhs]
            self.env.assignAt(dist, assign_node.lhs.name, val)
        else:
            self.globals.assign(assign_node.lhs.name, val)
        # self.env.assign(assign_node.name, val)  # old way before resolver
        return val

    def visitNodeList(self, node_list_node):
        return [self.interpret(node) for node in node_list_node]
            

    def visitIf(self, if_node: nodes.If):
        for branch in if_node.branch_seq:  # TODO add truthiness here!
            val = self.interpret(branch.cond)
            if not val: continue
            self.interpret(branch.body)

    def visitWhile(self, while_node: nodes.While):
        while self.interpret(while_node.condition):
            self.interpret(while_node.body)

    def visitCall(self, call_node: nodes.Call):
        fn = self.interpret(call_node.name)
        args = [self.interpret(arg) for arg in call_node.actuals]
        assert isinstance(fn, InternalCallable)
        return fn(self, *args)

    def visitClassObj(self, cls_obj_node: nodes.ClassObj):
        superclass = None
        if cls_obj_node.inheritance:
            superclass = self.interpret(cls_obj_node.inheritance)
            assert isinstance(superclass, InternalClass)

        self.env.define(cls_obj_node.name, None)

        if cls_obj_node.inheritance:
            self.env = Environment('base', self.env)
            self.env.define('super', superclass)

        methods = {}
        for method in cls_obj_node.body:
            internal_method = InternalFunction(method, self.env, method.name == 'init')
            methods[method.name] = internal_method
        klass = InternalClass(cls_obj_node.name, superclass, methods)

        if superclass:
            self.env = self.env.enclosing

        self.env.assign(cls_obj_node.name, klass)
    
    def visitRoot(self, root_node):
        res = list(self.interpret(root_node.globals) | traverse | where(lambda c: c is not None))
        if not len(res):
            print('Error: did not recieve exit code from "main"')
            raise RuntimeError(1)
        if len(res) > 1:
            raise ValueError(f'somehow recieved {res} from interpreting root')
        
        return res[0]

    def visitFnObj(self, fn_def_node):
        return InternalFunction(fn_def_node, self.env, False)

    def visitReturn(self, return_node):
        raise ReturnInterrupt(self.interpret(return_node.expr))


    def visitPrimitiveType(self, obj_type_node):
        raise NotImplementedError

    def visitFnType(self, fn_sig_node):
        raise NotImplementedError

    def visitIndex(self, index_node):
        idx = int(self.interpret(index_node.idx))

        if index_node in self.locals:
            dist = self.locals[index_node]
            array = self.env.getAt(dist, index_node.name)
            return array, idx
        else:
            array = self.interpret(index_node.base)

        
        return array[idx]

    def visitArray(self, array_node):
        return InternalArray(array_node.values, array_node.type)

    def visitTryCatch(self, try_catch):
        try:
            self.interpret(try_catch.try_.body)
        except try_catch.catch.exception as err:
            self.interpret(try_catch.catch.body)