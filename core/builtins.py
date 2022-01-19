"""

"""

from abc import abstractmethod

import time
import subprocess
import sys
import requests
from core.runtime import InternalCallable


"""
# Inner and Outer are noops
class Inner:
    def __init__(self, val) -> None:
        self.type = val

class Outer:
    def __init__(self, val) -> None:
        self.ret_type = Inner(val)
"""

# builtins
# TODO add support for different arg types
# get a list of all subclasses and register them?
class BuiltinCallable(InternalCallable):
    registered = set()

    def __init__(self, name, ret_type, arg_type) -> None:
        super().__init__()
        self.name = name
        self.arg_types = arg_type
        self.ret_type = ret_type

    def __init_subclass__(cls):
        BuiltinCallable.registered.add(cls())

    @abstractmethod
    def __call__(self, interpreter, *args):
        raise NotImplementedError

class Clock(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('clock', float, ())

    def __call__(self, interp):
        return time.time()

class Shell(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('shell', str, (str,))

    def __call__(self, interp, cmd):
        return subprocess.run(
            cmd,
            shell=True,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT
        ).stdout.decode(encoding='utf-8').strip()

class Int(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('int', float, (float,))

    def __call__(self, interp, val):
        return float(int(val))
    
class Print(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('print', 'void', (str,))

    def __call__(self, interp, val):
        print(str(val), flush = True)

class Input(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('input', str, (str,))

    def __call__(self, interp, msg):
        return input(msg)

class Sleep(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('sleep', 'void', (float,))

    def __call__(self, interp, t):
        time.sleep(t)

class Exit(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('exit', 'void', (float,))

    def __call__(self, interp):
        sys.exit()

class Range(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('range', float, (float,))

    def __call__(self, interp, length):
        return list(range(int(length)))

class Hex(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('hex', str, (float,))

    def __call__(self, interp, val):
        int_val = int(val)
        assert int_val == val
        return hex(int_val)

class Bin(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('bin', str, (float,))

    def __call__(self, interp, val):
        int_val = int(val)
        assert int_val == val
        return bin(int_val)

class Dec(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('dec', str, (float,))

    def __call__(self, interp, val: str):
        if len(val) < 3:
            raise RuntimeError(1, f'can not convert "{val}" to decimal')
        elif val.startswith('0b'):
            return int(val, 2)
        elif val.startswith('0x'):
            return int(val, 16)
        else:
            raise RuntimeError(1, f'can not convert "{val}" to decimal')

class Ping(BuiltinCallable):
    def __init__(self) -> None:
        super().__init__('ping', str, (str,))

    def __call__(self, interp, url):
        return float(requests.get(url).status_code)