"""

"""

from abc import ABCMeta, abstractmethod

class InternalLiteral(metaclass = ABCMeta):
    def __init__(self) -> None:
        pass

class InternalArray(InternalLiteral):
    def __init__(self, values, type_) -> None:
        super().__init__()
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