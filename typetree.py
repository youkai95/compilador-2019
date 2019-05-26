class ClassType:
    def __init__(self, name, parent=None, methods=None):
        self.name = name
        self.parent = parent
        self.methods = methods

class MethodType:
    def __init__(self, name, rettype, param_types):
        self.name = name
        self.ret_type = rettype
        self.param_types = param_types

class TypeTree:
    def __init__(self):
        obj_type = ClassType("Object", None)
        int_type = ClassType("Int", obj_type)
        string_type = ClassType("String", obj_type)
        bool_type = ClassType("Bool", obj_type)
        io_type = ClassType("IO", obj_type)
        self.type_dict = {
            "Object": obj_type,
            "Int": int_type,
            "String": string_type,
            "Bool": bool_type,
            "IO": io_type
        }
