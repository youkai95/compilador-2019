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
    def visit(self, node, types, errors):
        methods = {}
        for p in node.cexpresion:
            if type(p) is ast.MethodNode:
                params = []
                for d in p.params:
                    params.append(d.type_token)
                methods[p.name] = typetree.MethodType(p.name, p.ret_type, params)
        if node.idx_token in types.type_dict:
            errors.append("Error: Type %s already defined" % node.idx_token)
            return 0
        parent = types.type_dict["Object"]
        types.type_dict[node.idx_token] = typetree.ClassType(node.idx_token, parent, methods)
        return types

class CheckTypeVisitor_2nd:
    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node, type, errors):
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
                        errors.append("Method error")
                p = p.parent

            types.type_dict[node.idx_token].parent = parent
        return types