"""

"""

# try to compose nodes as other nodes "desugar"
# add all built-ins in to global scope at start
# make FnType have type of FnSignature
# max num params be 254 (class) 255 (function)
# for fn calls, each fn call gets own env to protect recursions

# consider type literals, function str should also refer to str type literal for example


from core.ast_visitors import SemanticAnalyzer as SA, Unparser, GraphManager, Interpreter
from core import ReturnInterrupt


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
        exit_code = None
        try:
            self.interpreter.interpret(self.ast)
        except ReturnInterrupt as RI:
            exit_code = int(RI.ret_val)
        else:
            pass
            # raise ValueError('Did not recieve any exit code...')
        
        return exit_code
    