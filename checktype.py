import visitor
import ast_hierarchy as ast
from typetree import TypeTree


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
        t = tree.type_dict["Int"]
        node.type = t
        return t

    @visitor.when(ast.MinusNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left != tree.type_dict["Int"] or right != tree.type_dict["Int"]:
            errors.append("'-' binary operator only works with integers")
        t = tree.type_dict["Int"]
        node.type = t
        return t

    @visitor.when(ast.StarNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left != tree.type_dict["Int"] or right != tree.type_dict["Int"]:
            errors.append("'*' binary operator only works with integers")
        t = tree.type_dict["Int"]
        node.type = t
        return t

    @visitor.when(ast.DivNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left != tree.type_dict["Int"] or right != tree.type_dict["Int"]:
            errors.append("'/' binary operator only works with integers")
        t = tree.type_dict["Int"]
        node.type = t
        return t

    @visitor.when(ast.NegationNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        if expr != tree.get_type("Int"):
            errors.append("Negation operator is only valid with Integers")
        node.type = tree.get_type("Int")
        return tree.get_type("Int")

    @visitor.when(ast.NotNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        if expr != tree.get_type("Bool"):
            errors.append("Not operator is only valid with booleans")
        t = tree.get_type("Bool")
        node.type = t
        return t

    @visitor.when(ast.ComplementNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        if expr != tree.get_type("Int"):
            errors.append("Complement operator is only valid with Integers")
        t = tree.get_type("Int")
        node.type = t
        return t

    @visitor.when(ast.LetInNode)
    def visit(self, node, tree, errors):
        for declaration in node.declaration_list:
            self.visit(declaration, tree, errors)
        t = self.visit(node.expr, tree, errors)
        node.type = t
        return t

    @visitor.when(ast.BlockNode)
    def visit(self, node, tree, errors):
        result = None
        for expr in node.expr_list:
            result = self.visit(expr, tree, errors)
        node.type = result
        return result

    @visitor.when(ast.AssignNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        if node.variable_info.type:
            if not tree.check_variance(node.variable_info.type, expr):
                errors.append("Type mistmatch with variable '%s'" % node.variable_info.name)
            #node.variable_info.vmholder = expr
        else:
            node.variable_info.type = expr
        node.type = node.variable_info.type
        return node.variable_info.type

    @visitor.when(ast.IntegerNode)
    def visit(self, node, tree, errors):
        t = tree.get_type("Int")
        node.type = t
        return t

    @visitor.when(ast.VariableNode)
    def visit(self, node, tree, errors):
        node.type = node.variable_info.type
        return node.variable_info.type

    # TODO
    @visitor.when(ast.PrintIntegerNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        #print(expr)
        node.type = expr
        return expr

    # TODO
    @visitor.when(ast.PrintStringNode)
    def visit(self, node, tree, errors):
        #print(node.string_token.text_token)
        t = tree.get_type("IO")
        node.type = t
        return t

    # TODO
    @visitor.when(ast.ScanNode)
    def visit(self, node, tree, errors):
        t = tree.get_type("IO")
        node.type = t
        return t
        #return input()

    @visitor.when(ast.DeclarationNode)
    def visit(self, node, tree, errors):
        t = tree.get_type(node.type_token)
        if node.expr is not None:
            expr = self.visit(node.expr, tree, errors)
            # TODO Check for polimorphism
            if not t:
                errors.append("type '%s' is not defined" % node.type_token)
            else:
                if not tree.check_variance(t, expr):
                    errors.append("Type mistmatch with variable '%s'" % node.variable_info.name)
                node.variable_info.type = t
                #node.variable_info.vmholder = expr
        else:
            node.variable_info.type = t
            #node.variable_info.vmholder = 0

        node.type =  node.variable_info.type
        return node.variable_info.type

    @visitor.when(ast.ClassNode)
    def visit(self, node, tree, errors):
        t = tree.get_type(node.idx_token)
        if not t:
            errors.append("type '%s' is not defined" % node.idx_token)
        self.classType = t
        for expr in node.cexpresion:
            self.visit(expr, tree, errors)
        node.type =t
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
            errors.append("Class '%s' doesnt contains method '%s'" % (self.classType.name, node.idx_token))
            return tree.get_type("Void")
        if len(temp.param_types) == len(node.expresion_list):
            for i in range(len(node.expresion_list)):
                if not tree.check_variance(tree.get_type(temp.param_types[i]), self.visit(node.expresion_list[i], tree, errors)):
                    errors.append("Incorrect parameter type")
        else:
            errors.append("Incorrect number of parameters")
        t = tree.get_type(temp.ret_type)
        node.type = t
        node.method_type = temp
        return t

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
        node.method_type = r
        if not r:
            errors.append("Class '%s' doesnt contains method '%s'" % (var_type.name, node.method))
            return tree.get_type("Void")
        if len(r.param_types) == len(node.params):
            for i in range(0, len(node.params)):
                # TODO Check for specific types at parameters (varianza)
                if not tree.check_variance(tree.get_type(r.param_types[i]), self.visit(node.params[i], tree, errors)):
                    errors.append("Incorrect parameter type")
        else:
            errors.append("Incorrect number of parameters")

        t = tree.get_type(r.ret_type)
        if not t:
            errors.append("type is '%s' not defined" % r.ret_type)
        node.type = t
        return t

    @visitor.when(ast.NewNode)
    def visit(self, node, tree, errors):
        t = tree.get_type(node.type_token)
        if not t:
            errors.append("type is '%s' not defined" % node.type_token)
        node.type = t
        return t

    @visitor.when(ast.DispatchParentInstanceNode)
    def visit(self, node, tree, errors):
        var_type = self.visit(node.variable, tree, errors)
        ctype = var_type
        r = None
        parent_type = tree.get_type(node.parent)
        if not parent_type:
            errors.append("Type '%s' is not defined" % node.parent)
        while not r and ctype:
            if ctype == parent_type:
                for n, m in ctype.methods.items():
                    if n == node.method:
                        r = m
                        break
                if not r:
                    errors.append("Parent class '%s' doesnt have a definition for method '%s'" % (node.parent, node.method))
                    return tree.get_type(r.ret_type)
                break
            ctype = ctype.parent

        if not ctype:
            errors.append("Class '%s' isnt a '%s' parent" % (node.parent, var_type.name))
            return tree.get_type("Void")
        if len(r.param_types) == len(node.params):
            for i in range(0, len(node.params)):
                # TODO Check for specific types at parameters (varianza)
                if not tree.check_variance(tree.get_type(r.param_types[i]), self.visit(node.params[i], tree, errors)):
                    errors.append("Incorrect parameter type")
        else:
            errors.append("Incorrect number of parameters")
        t = tree.get_type(r.ret_type)
        node.type = t
        return t

    @visitor.when(ast.MethodNode)
    def visit(self, node, tree: TypeTree, errors):
        for param in node.params:
            self.visit(param, tree, errors)
        v = self.visit(node.body, tree, errors)
        if not v or not tree.check_variance(tree.get_type(node.ret_type), v): # v.name != node.ret_type
            errors.append("Method return type mistmatch")
        node.type = v
        return v

    @visitor.when(ast.CaseNode)
    def visit(self, node, tree,  errors):
        self.visit(node.expr, tree, errors)
        result = self.visit(node.expresion_list[0], tree, errors)
        for expr in range(1, len(node.expresion_list)):
            result = tree.check_inheritance(self.visit(node.expresion_list[expr], tree, errors), result)
        node.type = result
        return result

    @visitor.when(ast.CaseItemNode)
    def visit(self, node, tree, errors):
        self.visit(node.variable, tree, errors)
        r = self.visit(node.expr, tree, errors)
        if r is not None:
            node.type = r
            return r
        else:
            errors.append("The expresion is None")

    @visitor.when(ast.IsVoidNode)
    def visit(self, node, tree, errors):
        t = tree.type_dict["Bool"]
        node.type = t
        return t

    @visitor.when(ast.BooleanNode)
    def visit(self, node, tree, errors):
        t = tree.type_dict["Bool"]
        node.type = t
        return t

    @visitor.when(ast.StringNode)
    def visit(self, node, tree, errors):
        t = tree.type_dict["String"]
        node.type = t
        return t

    @visitor.when(ast.WhileNode)
    def visit(self, node, tree, errors):
        self.visit(node.expr, tree, errors)
        if self.visit(node.conditional_token, tree, errors) != tree.type_dict["Bool"]:
            errors.append("while condition must be boolean")
        node.type = None
        return None

    @visitor.when(ast.IfNode)
    def visit(self, node, tree, errors):
        if self.visit(node.conditional_token, tree, errors) != tree.type_dict["Bool"]:
            errors.append("if condition must be boolean")
        expr_type = self.visit(node.expr, tree, errors)
        else_type = self.visit(node.else_expr, tree, errors)
        t = tree.check_inheritance(expr_type, else_type)
        node.type = t
        return t

    @visitor.when(ast.EqualNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left != right:
            errors.append("Both types in equality must be the same")
        t = tree.type_dict["Bool"]
        node.type = t
        return t

    @visitor.when(ast.LessEqualNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        t = tree.type_dict["Bool"]
        node.type = t
        if left == right == tree.type_dict["Int"]:
            return t
        errors.append("Both types in comparison must be Integer")
        return t

    @visitor.when(ast.LessThanNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        t = tree.type_dict["Bool"]
        node.type = t
        if left == right == tree.type_dict["Int"]:
            return t
        errors.append("Both types in comparison must be Integer")
        return t

    @visitor.when(ast.PropertyNode)
    def visit(self, node, tree, errors):
        t = self.visit(node.decl, tree, errors)
        node.type = t
        return t