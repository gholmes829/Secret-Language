"""

"""

# try to compose nodes as other nodes "desugar"
# add all built-ins in to global scope at start
# make FnType have type of FnSignature
# max num params be 254 (class) 255 (function)
# for fn calls, each fn call gets own env to protect recursions


from core.ast_visitors import SemanticAnalyzer as SA, Unparser, GraphManager, Interpreter
from core import ReturnInterrupt


class AST:
    def __init__(self, root) -> None:
        self.root = root
        self.bind_and_resolve()

    def bind_and_resolve(self):
        SA().resolve(self.root)

    def unparsed(self):
        return self.root.accept(Unparser(), 0)

    def to_dot(self):
        graph_manager = GraphManager()
        self.root.accept(graph_manager, graph_manager.graph)
        return graph_manager.graph.to_string()

    def interpret(self):
        interpreter = Interpreter()
        exit_code = None
        try:
            interpreter.interpret(self.root)
        except ReturnInterrupt as RI:
            exit_code = int(RI.ret_val)
        else:
            pass
            # raise ValueError('Did not recieve any exit code...')
        
        return exit_code
    