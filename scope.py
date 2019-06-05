import itertools as itl
from typetree import TypeTree

class Scope:
    def __init__(self, parent=None):
        self.locals = []
        self.parent = parent
        self.children = []
        self.index_at_parent = 0 if parent is None else len(parent.locals)
        self.types = TypeTree()

    def define_variable(self, vname):
        vinfo = VariableInfo(vname)
        self.locals.append(vinfo)
        return vinfo

    def create_child_scope(self):
        child_scope = Scope(self)
        self.children.append(child_scope)
        return child_scope

    def is_defined(self, vname):
        return self.get_variable_info(vname) is not None

    def get_variable_info(self, vname):
        current = self
        top = len(self.locals)
        while current is not None:
            vinfo = Scope.find_variable_info(vname, current, top)
            if vinfo is not None:
                return vinfo
            top = current.index_at_parent
            current = current.parent
        return None

    def is_local(self, vname):
        return self.get_local_variable_info(vname) is not None

    def get_local_variable_info(self, vname):
        return Scope.find_variable_info(vname, self)

    @staticmethod
    def find_variable_info(vname, scope, top=None):
        if top is None:
            top = len(scope.locals)
        candidates = (vinfo for vinfo in itl.islice(scope.locals, top) if vinfo.name == vname)
        return next(candidates, None)


class VariableInfo:
    def __init__(self, name):
        self.name = name
        self.type = None
        self.vmholder = None
