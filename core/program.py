"""

"""

# try to compose nodes as other nodes "desugar"
# add all built-ins in to global scope at start
# make FnType have type of FnSignature
# max num params be 254 (class) 255 (function)
# for fn calls, each fn call gets own env to protect recursions

# consider type literals, function str should also refer to str type literal for example
# multiple inheritance and method resolution


from core.visitors.semantics import SemanticAnalyzer as SA
from core.visitors import Unparser, GraphManager, Interpreter
from core.runtime.callables import ReturnInterrupt


class Program:
    def __init__(self, ast) -> None:
        self.ast = ast
        # print(self.unparsed())
        self.interpreter = Interpreter()
        SA(self.interpreter).resolve(self.ast)

    def unparsed(self):
        return self.ast.accept(Unparser(), 0)

    def to_dot(self):
        graph_manager = GraphManager()
        self.ast.accept(graph_manager, graph_manager.graph)
        return graph_manager.graph.to_string()

    def interpret(self):
        try:
            return self.interpreter(self.ast)
        except RuntimeError as err:
            return err.args[0]
    