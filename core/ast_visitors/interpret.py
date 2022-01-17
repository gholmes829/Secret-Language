"""

"""

from abc import ABCMeta, abstractmethod
from icecream import ic
from core.ast_nodes.node import ASTNode
import time

from core.ast_visitors.visitor import Visitor
from core import ast_nodes

# could make builtins their own special scope before globals


class ReturnInterrupt(Exception):
    def __init__(self, val) -> None:
        super().__init__()
        self.val = val

class InternalCallable(metaclass = ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def __call__(self, interpreter, *args):
        raise NotImplementedError

class InternalInstance:
    def __init__(self, klass) -> None:
        self.klass = klass
        self.fields = {}

    def get(self, name):
        if name in self.fields:
            return self.fields[name]
        
        return self.klass.find_method(name)
    
    def set(self, name, val):
        self.fields[name] = val

    def __repr__(self):
        return f'<Internal Instance of "{self.klass.name}" at {id(self)}>'

class InternalClass(InternalCallable):
    def __init__(self, name, methods) -> None:
        super().__init__()
        self.name = name
        self.methods = methods

    def find_method(self, name):
        return self.methods[name]

    def __call__(self, interpreter, *args):
        return InternalInstance(self)

    def __repr__(self):
        return f'<Internal Class, "{self.name}", at {id(self)}>'

class InternalFunction(InternalCallable):
    def __init__(self, fn_obj, closure) -> None:
        super().__init__()
        self.fn_obj = fn_obj
        self.closure = closure

    def __call__(self, interpreter: 'Interpreter', *args):
        assert len(args) == len(self.fn_obj.formals)

        with interpreter.enter_scope(self.fn_obj.name, self.closure):
            for arg, formal in zip(args, self.fn_obj.formals):
                interpreter.env.define(formal.name, arg)
            try:
                interpreter.interpret(self.fn_obj.body)
            except ReturnInterrupt as RI:
                    return RI.val
            else:
                return None


# built ins
class Clock(InternalCallable):
    def __init__(self) -> None:
        super().__init__()
        self.ret_type = 'void'

    def __call__(self, interpreter):
        return time.time()
    
class Print(InternalCallable):
    def __init__(self) -> None:
        super().__init__()
        self.ret_type = 'void'

    def __call__(self, interpreter, val):
        print(str(val), flush = True)
        # return val  # wont work yet bc need to template (?)

# end built ins


class Environment:
    _builtins = builtin_globals = {
        ('clock', Clock()),
        ('print', Print())
    } 
    def __init__(self, name, enclosing = None) -> None:
        self.scope = {}
        self.name = name
        self.enclosing = enclosing
        if not enclosing:
            for name, builtin in Environment._builtins:
                self.define(name, builtin)


    def define(self, name, val):
        #if name in self.scope:
        #    raise ValueError(f'"{name}" is already defined with value "{val}".')  # might want to enable this but wld break mult for loop
        self.scope[name] = val

    def get(self, name):
        try:
            return self.scope[name]
        except KeyError:
            if self.enclosing:
                return self.enclosing.get(name)
            raise AttributeError(f'Undefined variable "{name}".')
        
    def getAt(self, dist, name):
        curr_env = self
        for _ in range(dist):
            curr_env = curr_env.enclosing

        return curr_env.scope[name]

    def assignAt(self, dist, name, val):
        curr_env = self
        for _ in range(dist):
            curr_env = curr_env.enclosing

        curr_env.scope[name] = val

    def assign(self, name, val):
        if name in self.scope:
            self.scope[name] = val
        elif self.enclosing:
            return self.enclosing.assign(name, val)
        else:
            raise AttributeError(f'Undefined variable "{name}".')

    def __repr__(self) -> str:
        return f'<env object "{self.name}" at {id(self)}>'


class Interpreter(Visitor):
    def __init__(self) -> None:
        super().__init__()
        self.prev_envs = []
        self.globals = Environment('globals')
        self.locals = {}  # book calls these locals bc they didn't analyze things in global scope, might cause bugs
        self.env = self.globals

    def interpret(self, node: ast_nodes.ASTNode):
        return node.accept(self)

    def enter_scope(self, name, env = None):
        self.prev_envs.append(self.env)
        self.env = Environment(name, env or self.env)
        return self

    def exit_scope(self):
        self.env = self.prev_envs.pop()

    def resolve(self, expr, depth):
        self.locals[expr] = depth  # should type also be added here like {depth: depth, type: type}

    def look_up_var(self, node):
        if node in self.locals:
            dist = self.locals[node]
            return self.env.getAt(dist, node.name)
        else:
            return self.globals.get(node.name)

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.exit_scope()

    def visitLiteral(self, literal_node: ast_nodes.Literal):
        return literal_node.value

    def visitNumLit(self, num_lit_node):
        return self.interpret(super(ast_nodes.NumLit, num_lit_node))

    def visitStrLit(self, str_lit_node):
        return self.interpret(super(ast_nodes.StrLit, str_lit_node))

    def visitBoolLit(self, bool_lit_node):
        return self.interpret(super(ast_nodes.BoolLit, bool_lit_node))

    def visitNone(self, none_node):
        return self.interpret(super(ast_nodes.None_, none_node))

    def visitUnary(self, unary_node: ast_nodes.UnaryOp):
        value = self.interpret(unary_node.operand)
        return unary_node.op(value)

    def visitBinOp(self, bin_op_node: ast_nodes.BinOp):
        lhs_value = bin_op_node.lhs_cast(self.interpret(bin_op_node.lhs))
        rhs_value = bin_op_node.rhs_cast(self.interpret(bin_op_node.rhs))
        return bin_op_node.res_cast(bin_op_node.op(lhs_value, rhs_value))

    def visitAssignDecl(self, ad_node):
        val = self.interpret(ad_node.rhs)
        self.env.define(ad_node.lhs.name, val)

    def visitID(self, id_node):
        return self.look_up_var(id_node)
        # return self.env.get(id_node.name)  # pre-bind version

    def visitScopedID(self, id_node: ast_nodes.ScopedID):
        instance = self.interpret(id_node.object)
        assert isinstance(instance, InternalInstance)
        return instance.get(id_node.name)

    def visitSetStmt(self, set_node):
        instance = self.interpret(set_node.lhs.object)
        val = self.interpret(set_node.rhs)
        instance.set(set_node.lhs.name, val)

    def visitAssign(self, assign_node):
        self.interpret(assign_node.lhs)
        val = self.interpret(assign_node.rhs)
        assign_node.lhs.type = assign_node.rhs.type  # is this necessary?
        if assign_node.lhs in self.locals:
            dist = self.locals[assign_node.lhs]
            self.env.assignAt(dist, assign_node.lhs.name, val)
        else:
            self.globals.assign(assign_node.lhs.name, val)
        # self.env.assign(assign_node.name, val)  # old way before resolver
        return val

    def visitNodeList(self, node_list_node):
        for node in node_list_node:
            self.interpret(node)

    def visitIf(self, if_node: ast_nodes.If):
        for branch in if_node.branch_seq:  # TODO add truthiness here!
            val = self.interpret(branch.cond)
            if not val: continue
            self.interpret(branch.body)

    def visitWhile(self, while_node: ast_nodes.While):
        while self.interpret(while_node.condition):
            self.interpret(while_node.body)

    def visitCall(self, call_node: ast_nodes.Call):
        name = self.interpret(call_node.name)
        args = [self.interpret(arg) for arg in call_node.actuals]
        assert isinstance(name, InternalCallable)
        return name(self, *args)

    def visitClassObj(self, cls_obj_node: ast_nodes.ClassObj):
        self.env.define(cls_obj_node.name, None)
        methods = {}
        for method in cls_obj_node.body:
            internal_method = InternalFunction(method, self.env)
            methods[method.name] = internal_method
        klass = InternalClass(cls_obj_node.name, methods)
        self.env.assign(cls_obj_node.name, klass)
    
    def visitRoot(self, root_node):
        # with self.enter_scope('globals'):  # before initializing globals in __init__
        self.interpret(root_node.globals)

    def visitFnObj(self, fn_def_node):
        new_fn = InternalFunction(fn_def_node, self.env)
        #self.env.define(fn_def_node.name, new_fn)
        return new_fn

    def visitReturn(self, return_node):
        raise ReturnInterrupt(self.interpret(return_node.expr))


    def visitPrimitiveType(self, obj_type_node, symbol_table):
        raise NotImplementedError

    def visitFnType(self, fn_sig_node, *args, **kwargs):
        pass