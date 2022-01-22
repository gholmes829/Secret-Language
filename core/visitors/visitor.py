"""

"""

from abc import ABCMeta, abstractmethod


class Visitor(metaclass = ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def visitRoot(self, root_node, *args, **kwargs):
        raise NotImplementedError