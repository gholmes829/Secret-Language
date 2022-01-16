"""

"""


from abc import ABCMeta, abstractmethod
import pydot
from icecream import ic

# abstractions
class ASTNode(metaclass = ABCMeta):
    dot_node_kwargs = dict()
    def __init__(self, token) -> None:
        self.token = token
        # ic(token.type, token.value)
        # input('\n\n\n')

    @abstractmethod
    def accept(self, visitor, *args, **kwargs):
        raise NotImplementedError

    def make_pydot_node(self, *args, **kwargs):
        print(__class__)
        print(self.dot_node_kwargs)
        return pydot.Node(str(hash(self)), *args, **(self.dot_node_kwargs | kwargs))


# root of program
class Root(ASTNode):
    def __init__(self, token, globals) -> None:
        super().__init__(token)
        self.globals = globals

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitRoot(self, *args, **kwargs)

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='red', **kwargs)


class NodeList(ASTNode):
    def __init__(self, token, nodes, nodes_type) -> None:
        super().__init__(token)
        self.nodes = nodes
        self.nodes_type = nodes_type

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitNodeList(self, *args, **kwargs)

    def __repr__(self):
        return f'<"{self.nodes_type}" list obj at {id(self)}>'