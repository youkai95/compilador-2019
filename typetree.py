class ClassType:
    def __init__(self, name, parent=None, methods=None, attrb=None):
        self.name = name
        self.parent = parent
        self.methods = methods if methods else {}
        self.attributes = attrb if attrb else {}

class MethodType:
    def __init__(self, name, rettype, param_types):
        self.name = name
        self.ret_type = rettype
        self.param_types = param_types
        self.cil_name = ""

# TODO Built-in methods for types. Boxing/Unboxing for Object type
class TypeTree:
    def __init__(self):
        obj_type = ClassType("Object", None, {})
        void = ClassType("Void", None)
        int_type = ClassType("Int", obj_type)
        string_type = ClassType("String", obj_type)
        bool_type = ClassType("Bool", obj_type)
        io_type = ClassType("IO", obj_type, {})
        self.type_dict = {
            "Object": obj_type,
            "Int": int_type,
            "String": string_type,
            "Bool": bool_type,
            "IO": io_type,
            "Void": void
        }

    def check_inheritance(self, a: ClassType, b: ClassType):
        a_p = []
        if a == b:
            return a
        while a.parent != None:
            a_p.append(a.parent)
            a = a.parent

        while b.parent != None:
            if b.parent in a_p:
                return b.parent
            b = b.parent

        return self.type_dict["Object"]

    def get_type(self, name):
        if name in self.type_dict:
            return self.type_dict[name]
        return None

    def check_variance(self, a: ClassType, b: ClassType):
        while a != b:
            if not b:
                return False
            b = b.parent
        return True