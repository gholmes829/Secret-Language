"""

"""


from abc import ABCMeta, abstractmethod
import pydot
from icecream import ic

# abstractions
class ASTNode(metaclass = ABCMeta):
    dot_node_kwargs = dict()
    def __init__(self, meta) -> None:
        self.meta = meta
        self.id = hex(id(self))
        # ic(meta.type, meta.value)
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
    def __init__(self, meta, globals) -> None:
        super().__init__(meta)
        self.globals = globals

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitRoot(self, *args, **kwargs)

    def make_pydot_node(self, *args, **kwargs):
        return super().make_pydot_node(*args, fillcolor='red', **kwargs)


class NodeList(ASTNode):
    def __init__(self, meta, nodes, list_name) -> None:
        super().__init__(meta)
        self.nodes = nodes
        self.list_name = list_name

    def accept(self, visitor, *args, **kwargs):
        return visitor.visitNodeList(self, *args, **kwargs)

    def __len__(self):
        return len(self.nodes)

    def __getitem__(self, idx):
        return self.nodes[idx]

    def __iter__(self):
        return self.nodes.__iter__()

    def __repr__(self):
        return f'<NodeList "{self.list_name}" at {self.id}>'