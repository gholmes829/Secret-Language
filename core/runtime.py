"""
Contains:
 - internals
 - builtins
 - environment
"""

from abc import ABCMeta, abstractmethod
from icecream import ic

# internals
class InternalArray:
    def __init__(self, values, type_) -> None:
        self.values = values
        self.type = type_

    def __getitem__(self, idx):
        return self.values[idx]

    def __setitem__(self, idx, val):
        self.values[idx] = val

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return repr(self.values)


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
        
        method = self.klass.find_method(name)
        return method.bind(self)
    
    def set(self, name, val):
        self.fields[name] = val

    def __repr__(self):
        return f'<Internal Instance of "{self.klass.name}">'

class InternalClass(InternalCallable):
    def __init__(self, name, superclass, methods) -> None:
        super().__init__()
        self.name = name
        self.superclass = superclass
        self.methods = methods

    def find_method(self, name):
        if name in self.methods:
            return self.methods[name]
        elif self.superclass:
            return self.superclass.find_method(name)

    def __call__(self, interpreter, *args):
        instance = InternalInstance(self)
        initializer = self.find_method('init')
        if initializer:
            initializer.bind(instance)(interpreter, *args)
        return instance

    def __repr__(self):
        return f'<Internal Class, "{self.name}">'

class InternalFunction(InternalCallable):
    def __init__(self, fn_obj, closure, is_initializer) -> None:
        super().__init__()
        self.fn_obj = fn_obj
        self.closure = closure
        self.is_initializer = is_initializer

    def bind(self, instance):
        env = Environment('binding', self.closure)
        env.define('this', instance)
        return InternalFunction(self.fn_obj, env, self.is_initializer)

    def __call__(self, interpreter, *args):
        assert len(args) == len(self.fn_obj.formals)

        with interpreter.enter_scope(self.fn_obj.name, self.closure):
            for arg, formal in zip(args, self.fn_obj.formals):
                interpreter.env.define(formal.name, arg)
            try:
                interpreter.interpret(self.fn_obj.body)
            except ReturnInterrupt as RI:
                    return RI.val
            else:
                if self.is_initializer:
                    return self.closure.getAt(0, 'this')
                return None

    def __repr__(self):
        return f'<Internal Function, "{self.fn_obj.name}">'



# environment
class Environment:
    from core.builtins import BuiltinCallable
    def __init__(self, name, enclosing = None) -> None:
        self.scope = {}
        self.name = name
        self.enclosing = enclosing
        if not enclosing:
            for builtin in Environment.BuiltinCallable.registered:
                self.define(builtin.name, builtin)

    def print(self):
        print(f'Env "{self.name}" -> {self.enclosing}:')
        for k, v in self.scope:
            print(f'\t{k}: {v}')

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