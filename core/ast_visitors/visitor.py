"""

"""

from abc import ABCMeta, abstractmethod


class Visitor(metaclass = ABCMeta):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def visitRoot(self, root_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitPrint(self, print_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitID(self, id_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitAssignDecl(self, assign_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitAssign(self, assign_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitBinOp(self, bin_op_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitCall(self, call_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitIf(self, if_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitReturn(self, return_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitFor(self, for_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitWhile(self, while_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitPrimitiveType(self, obj_type_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitFnObj(self, fn_def_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitFnType(self, fn_sig_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitLiteral(self, literal_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitNumLit(self, num_lit_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitStrLit(self, str_lit_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitBoolLit(self, bool_lit_node, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def visitNone(self, bool_lit_node, *args, **kwargs):
        raise NotImplementedError