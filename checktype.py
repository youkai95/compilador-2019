import visitor
import ast_hierarchy as ast

class CheckTypeVisitor:

    @visitor.on('node')
    def visit(self, node):
        pass

    def __init__(self):
        self.classType = None

    @visitor.when(ast.ProgramNode)
    def visit(self, node, tree, errors):
        for expr in node.expr:
            self.visit(expr, tree, errors)

    @visitor.when(ast.PlusNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left != tree.type_dict["Int"] or right != tree.type_dict["Int"]:
            errors.append("'+' binary operator only works with integers")
        return tree.type_dict["Int"]

    @visitor.when(ast.MinusNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left != tree.type_dict["Int"] or right != tree.type_dict["Int"]:
            errors.append("'-' binary operator only works with integers")
        return tree.type_dict["Int"]

    @visitor.when(ast.StarNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left != tree.type_dict["Int"] or right != tree.type_dict["Int"]:
            errors.append("'*' binary operator only works with integers")
        return tree.type_dict["Int"]

    @visitor.when(ast.DivNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left != tree.type_dict["Int"] or right != tree.type_dict["Int"]:
            errors.append("'/' binary operator only works with integers")
        return tree.type_dict["Int"]

    @visitor.when(ast.NegationNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        if expr != tree.type_dict["Int"]:
            # TODO
            errors.append("TODO")
        return tree.type_dict["Int"]

    @visitor.when(ast.NotNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        if expr != tree.type_dict["Bool"]:
            # TODO
            errors.append("TODO")
        return tree.type_dict["Bool"]

    @visitor.when(ast.LetInNode)
    def visit(self, node, tree, errors):
        for declaration in node.declaration_list:
            self.visit(declaration, tree, errors)
        return self.visit(node.expr, tree, errors)

    @visitor.when(ast.BlockNode)
    def visit(self, node, tree, errors):
        result = None
        for expr in node.expr_list:
            result = self.visit(expr, tree, errors)
        return result

    @visitor.when(ast.AssignNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        if node.variable_info.type:
            # TODO Check for polimorphism
            if node.variable_info.type != expr:
                errors.append("Type mistmatch with variable '%s'" % node.variable_info.name)
            node.variable_info.vmholder = expr
        else:
            node.variable_info.type = expr
        # TODO Check if is correct to return variable declaration type or new assign type
        return node.variable_info.type

    @visitor.when(ast.IntegerNode)
    def visit(self, node, tree, errors):
        return tree.type_dict["Int"]

    @visitor.when(ast.VariableNode)
    def visit(self, node, tree, errors):
        return node.variable_info.type

    # TODO
    @visitor.when(ast.PrintIntegerNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        print(expr)
        return expr

    # TODO
    @visitor.when(ast.PrintStringNode)
    def visit(self, node, tree, errors):
        print(node.string_token.text_token)
        return tree.type_dict["IO"]

    # TODO
    @visitor.when(ast.ScanNode)
    def visit(self, node, tree, errors):
        return input()

    @visitor.when(ast.DeclarationNode)
    def visit(self, node, tree, errors):
        if node.expr is not None:
            expr = self.visit(node.expr, tree, errors)
            # TODO Check for polimorphism
            if expr != tree.type_dict[node.type_token]:
                errors.append("Type mistmatch with variable '%s'" % node.variable_info.name)
            node.variable_info.type = tree.type_dict[node.type_token]
            node.variable_info.vmholder = expr
        else:
            node.variable_info.type = tree.type_dict[node.type_token]
            node.variable_info.vmholder = 0
        return node.variable_info.type

    @visitor.when(ast.ClassNode)
    def visit(self, node, tree, errors):
        for expr in node.cexpresion:
            self.visit(expr, tree, errors)
        t = tree.get_type(node.idx_token)
        if not t:
            errors.append("The type is not defined")
        return t

    @visitor.when(ast.DispatchNode)
    def visit(self, node, tree, errors):
        temp = None
        clss = self.classType
        while not temp and clss:
            for name, method in clss.methods.items():
                if name == node.idx_token:
                    temp = method
                    break
                clss = clss.parent
        if not temp:
            errors.append("TODO")
            return
        if len(temp.param_types) == len(node.expresion_list):
            for i in range(len(node.expresion_list)):
                if self.visit(node.expresion_list[i], tree, errors).name != temp.param_types[i]:
                    errors.append("TODO")
        else:
            errors.append("TODO")
        return temp.ret_type


    @visitor.when(ast.DispatchInstanceNode)
    def visit(self, node, tree, errors):
        var_type = self.visit(node.variable, tree, errors)
        r = None
        ctype = var_type
        while not r and ctype:
            for n, m in ctype.methods.items():
                if n == node.method:
                    r = m
                    break
            ctype = ctype.parent
        if not r:
            errors.append("Class '%s' doesnt contains method '%s'" % (var_type.name, node.method))
        if len(r.param_types) == len(node.params):
            for i in range(0, len(node.params)):
                # TODO Check for specific types at parameters (varianza)
                if self.visit(node.params[i], tree, errors).name != r.param_types[i]:
                    errors.append("Incorrect parameter type")
        else:
            errors.append("Incorrect number of parameters")
        return tree.type_dict[r.ret_type]

    @visitor.when(ast.NewNode)
    def visit(self, node, tree, errors):
        return tree.type_dict[node.type_token]

    @visitor.when(ast.DispatchParentInstanceNode)
    def visit(self, node, tree, errors):
        var_type = self.visit(node.variable, tree, errors)
        ctype = var_type
        parent_type = tree.type_dict[node.parent]
        while ctype:
            if ctype == parent_type:
                break
            ctype = ctype.parent
        if not ctype:
            errors.append("Class '%s' isnt a '%s' parent" % (node.parent, var_type.name))
        if len(r.param_types) == len(node.params):
            for i in range(0, len(node.params)):
                # TODO Check for specific types at parameters (varianza)
                if self.visit(node.params[i], tree, errors).name != r.param_types[i]:
                    errors.append("Incorrect parameter type")
        else:
            errors.append("Incorrect number of parameters")
        return tree.type_dict[r.ret_type]

    @visitor.when(ast.MethodNode)
    def visit(self, node, tree, errors):
        v = self.visit(node.body, tree, errors)
        if v.name != node.ret_type:
            errors.append("Method return type mistmatch")
        return v

    # TODO
    @visitor.when(ast.CaseNode)
    def visit(self, node, tree,  errors):
        self.visit(node.expr, tree, errors)
        result = self.visit(node.expr_list[0])
        for expr in node.expr_list:
            result = tree.check_inheritance(self.visit(expr, tree, errors), result)
        return result

    @visitor.when(ast.CaseItemNode)
    def visit(self, node, tree, errors):
        if self.visit(node.expr, tree, errors) is not None:
            return self.visit(node.expr, tree, errors)
        else:
            errors.append("The expresion is None")

    @visitor.when(ast.IsVoidNode)
    def visit(self, node, tree, errors):
        return tree.type_dict["Bool"]

    @visitor.when(ast.BooleanNode)
    def visit(self, node, tree, errors):
        return tree.type_dict["Bool"]

    @visitor.when(ast.StringNode)
    def visit(self, node, tree, errors):
        return tree.type_dict["String"]

    @visitor.when(ast.WhileNode)
    def visit(self, node, tree, errors):
        self.visit(node.expr, tree, errors)
        if self.visit(node.conditional_token, tree, errors) != tree.type_dict["Bool"]:
            errors.append("while condition must be boolean")
        return None

    @visitor.when(ast.IfNode)
    def visit(self, node, tree, errors):
        if self.visit(node.conditional_token, tree, errors) != tree.type_dict["Bool"]:
            errors.append("if condition must be boolean")
        expr_type = self.visit(node.expr, tree, errors)
        else_type = self.visit(node.else_expr, tree, errors)
        return tree.check_inheritance(expr_type, else_type)

    @visitor.when(ast.EqualNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left != right:
            errors.append("Both types in equality must be the same")
        return tree.type_dict["Bool"]

    @visitor.when(ast.LessEqualNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left == right == tree.type_dict["Int"]:
            return tree.type_dict["Bool"]
        errors.append("Both types in comparison must be Integer")
        return tree.type_dict["Bool"]

    @visitor.when(ast.LessThanNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left == right == tree.type_dict["Int"]:
            return tree.type_dict["Bool"]
        errors.append("Both types in comparison must be Integer")
        return tree.type_dict["Bool"]

    @visitor.when(ast.PropertyNode)
    def visit(self, node, tree, errors):
        return self.visit(node.decl, tree, errors)