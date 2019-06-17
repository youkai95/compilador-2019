from ast_hierarchy import PropertyNode, DeclarationNode


class ClassType:
    def __init__(self, name, parent=None, methods=None, attrb=None):
        self.name = name
        self.parent = parent
        self.methods = methods if methods else {}
        self.attributes = attrb if attrb else {}
        self.generate_cil_names()
        self.pos = None

    def generate_cil_names(self):
        for name, method in self.methods.items():
            method.cil_name = f'{self.name}_{name}'

class MethodType:
    def __init__(self, name, rettype, param_types):
        self.name = name
        self.ret_type = rettype
        self.param_types = param_types
        self.cil_name = ""
        self.mips_position = 0

# TODO Built-in methods for types. Boxing/Unboxing for Object type
class TypeTree:
    def __init__(self):
        #MethodType("copy", "Self_Type", [])
        obj_methods = {"abort" : MethodType("abort", "Object", []),
                       "type_name" : MethodType("type_name", "String", [])}
        h = DeclarationNode("holder")
        h.type = None
        obj_type = ClassType("Object", None, obj_methods, {"holder": PropertyNode(h)})

        void = ClassType("Void", None)

        int_type = ClassType("Int", obj_type)

        string_methods = {"substring" : MethodType("substr", "String", ["Int", "Int"]),
                          "length" : MethodType("length", "Int", []),
                          "concat" : MethodType("concat", "String", ["String"])}
        string_type = ClassType("String", obj_type, string_methods)

        bool_type = ClassType("Bool", obj_type)

        io_methods = {"in_string" : MethodType("in_string", "String", []),
                      "in_int" : MethodType("in_int", "Int", []),
                      "out_string": MethodType("out_string", "IO", ["String"]),
                      "out_int": MethodType("out_int", "IO", ["Int"])
                      }
        io_type = ClassType("IO", obj_type, io_methods)
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