"""

"""


from abc import ABCMeta, abstractmethod
import pydot
from icecream import ic

# abstractions
class ASTNode(metaclass = ABCMeta):
    def __init__(self, start_token, end_token) -> None:
        self.start_token = start_token
        self.end_token = end_token

    @abstractmethod
    def accept(self, visitor, *args, **kwargs):
        raise NotImplementedError

    def make_pydot_node(self, *args, **kwargs):
        return pydot.Node(str(hash(self)), *args, **kwargs)


# root of program
class Root(ASTNode):
    def __init__(self, stmts) -> None:
        super().__init__(None, None)
        self.stmts = stmts

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitRoot(self, *args, **kwargs)

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='red', **kwargs)