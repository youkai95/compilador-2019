import visitor
import ast_hierarchy as ast
import typetree

class CheckTypeVisitor_1st:
    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node, errors):
        t = typetree.TypeTree()
        for expr in node.expr:
            self.visit(expr, t, errors)
        return t

    @visitor.when(ast.ClassNode)
    def visit(self, node: ast.ClassNode, types, errors):
        methods = {}
        attrb = {}
        for p in node.cexpresion:
            if type(p) is ast.MethodNode:
                params = []
                for d in p.params:
                    params.append(d.type_token)
                if p.name in methods:
                    errors.append("Method '%s' already defined in type '%s'" % (p.name, node.idx_token))
                    return 0
                m = typetree.MethodType(p.name, p.ret_type, params)
                methods[p.name] = m
                p.vinfo = m
            else:
                if p.decl.idx_token in attrb:
                    errors.append("Property '%s' already defined in type '%s'" % (p.decl.idx_token, node.idx_token))
                attrb[p.decl.idx_token] = p
        if node.idx_token in types.type_dict:
            errors.append("Error: Type %s already defined" % node.idx_token)
            return 0
        if node.idx_token == "String" or node.idx_token == "Int" or node.idx_token == "Bool":
            errors.append("Type %s cannot be redefined" % node.idx_token)
            return 0
        if node.inherit_token == "String" or node.inherit_token == "Int" or node.inherit_token == "Bool":
            errors.append("Cannot inherit from type %s" % node.inherit_token)
            return 0
        parent = types.type_dict["Object"]
        types.type_dict[node.idx_token] = typetree.ClassType(node.idx_token, parent, methods, attrb)
        node.vtable = types.type_dict[node.idx_token]
        return types

class CheckTypeVisitor_2nd:
    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node, type, errors):
        main = type.get_type("Main")
        if not main or not "main" in main.methods:
            errors.append("There is no entry point. Couldnt find Main.main().")
        for expr in node.expr:
            self.visit(expr, type, errors)
        return type

    @visitor.when(ast.ClassNode)
    def visit(self, node, types, errors):
        if node.inherit_token:
            if not node.inherit_token in types.type_dict:
                errors.append("Error: Parent '%s' not defined" % node.inherit_token)
                return 0
            parent = types.type_dict[node.inherit_token]
            # INHERITANCE CYCLES & METHOD OVERLOADS
            p = parent
            while p != None:
                # Cycles
                if p.name == node.idx_token:
                    errors.append("Error: Inherintance cycles")
                    return 0
                # Overloads
                for m in types.type_dict[node.idx_token].methods.values():
                    if m.name in parent.methods and (parent.methods[m.name].param_types != m.param_types or parent.methods[m.name].ret_type != m.ret_type):
                        errors.append("Method overload error")
                p = p.parent

            types.type_dict[node.idx_token].parent = parent
        return types