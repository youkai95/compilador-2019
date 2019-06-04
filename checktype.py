import visitor
import ast_hierarchy as ast

class CheckTypeVisitor:

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node, scope, errors):
        return self.visit(node.expr)

    @visitor.when(ast.PlusNode)
    def visit(self, node, scope, errors):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if left != int or right != int:
            errors.append("'+' binary operator only works with integers")
        return int

    @visitor.when(ast.MinusNode)
    def visit(self, node, scope, errors):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if left != int or right != int:
            errors.append("'-' binary operator only works with integers")
        return int

    @visitor.when(ast.StarNode)
    def visit(self, node, scope, errors):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if left != int or right != int:
            errors.append("'*' binary operator only works with integers")
        return int

    @visitor.when(ast.DivNode)
    def visit(self, node, scope, errors):
        left = self.visit(node.left)
        right = self.visit(node.right)
        if left != int or right != int:
            errors.append("'/' binary operator only works with integers")
        return int

    @visitor.when(ast.NotNode)
    def visit(self, node, scope, errors):
        expr = self.visit(node.expr)
        return expr == bool

    @visitor.when(ast.LetInNode)
    def visit(self, node, scope, errors):
        for declaration in node.declaration_list:
            self.visit(declaration)
        return self.visit(node.expr)

    @visitor.when(ast.BlockNode)
    def visit(self, node, scope, errors):
        result = None
        for expr in node.expr_list:
            result = self.visit(expr)
        return result

    @visitor.when(ast.AssignNode)
    def visit(self, node, scope, errors):
        expr = self.visit(node.expr)
        node.variable_info.vmholder = expr
        return expr

    @visitor.when(ast.IntegerNode)
    def visit(self, node, scope, errors):
        return int

    @visitor.when(ast.VariableNode)
    def visit(self, node, scope, errors):
        return node.variable_info.vmholder

    @visitor.when(ast.PrintIntegerNode)
    def visit(self, node, scope, errors):
        expr = self.visit(node.expr)
        print(expr)
        return expr

    @visitor.when(ast.PrintStringNode)
    def visit(self, node, scope, errors):
        print(node.string_token.text_token)
        return 0

    @visitor.when(ast.ScanNode)
    def visit(self, node, scope, errors):
        return input()

    @visitor.when(ast.DeclarationNode)
    def visit(self, node, scope, errors):
        if node.expr is not None:
            expr = self.visit(node.expr)
            node.variable_info.vmholder = expr
        else:
            node.variable_info.vmholder = 0

    @visitor.when(ast.ClassNode)
    def visit(self, node, scope, errors):
        return self.visit(node.expr)

    @visitor.when(ast.DispatchNode)
    def visit(self, node, scope, errors):
        obj = self.visit(node.idx_token, scope, errors)



    @visitor.when(ast.DispatchInstanceNode)
    def visit(self, node, scope, errors):
        var_type = self.visit(node.variable, scope, errors)
        ctype = scope.typetree.type_dict[var_type]
        r = None
        for m in ctype.methods:
            if m.name == node.method:
                r = m
                break
        if not r:
            errors.append("Class '%s' doesnt contains method '%s'" % (var_type, node.method))

    @visitor.when(ast.DispatchParentInstanceNode)
    def visit(self, node, scope, errors):
        if node.expr is not None:
            pass
        else:
            pass

    @visitor.when(ast.MethodNode)
    def visit(self, node, scope, errors):
        return self.visit(node.expr)

    # TODO
    @visitor.when(ast.CaseNode)
    def visit(self, node, scope, errors):
        if node.expr is not None:
            pass
        else:
            pass

    @visitor.when(ast.IsVoidNode)
    def visit(self, node, scope, errors):
        self.visit(node, scope, errors)
        return bool

    @visitor.when(ast.BooleanNode)
    def visit(self, node, scope, errors):
        return bool

    @visitor.when(ast.StringNode)
    def visit(self, node, scope, errors):
        return str

    @visitor.when(ast.WhileNode)
    def visit(self, node, scope, errors):
        self.visit(node.expr, scope, errors)
        if self.visit(node.conditional_token, scope, errors) != bool:
            errors.append("while condition must be boolean")
        return None

    @visitor.when(ast.IfNode)
    def visit(self, node, scope, errors):
        if self.visit(node.conditional_token, scope, errors) != bool:
            errors.append("if condition must be boolean")
        expr_type = self.visit(node.expr, scope, errors)
        else_type = self.visit(node.else_expr, scope, errors)
        return scope.typetree.check_inheritance(expr_type, else_type)

    # TODO
    @visitor.when(ast.CaseItemNode)
    def visit(self, node, scope, errors):
        return self.visit(node.expr)

    @visitor.when(ast.NegationNode)
    def visit(self, node, scope, errors):
        if self.visit(node.expr, scope, errors) != int:
            errors.append("'-' operator must be with integers")
        return int

    @visitor.when(ast.EqualNode)
    def visit(self, node, scope, errors):
        left = self.visit(node.left, scope, errors)
        right = self.visit(node.right, scope, errors)
        if left != right:
            errors.append("Both types in equality must be the same")
        return bool

    @visitor.when(ast.LessEqualNode)
    def visit(self, node, scope, errors):
        left = self.visit(node.left, scope, errors)
        right = self.visit(node.right, scope, errors)
        if left == right == int:
            return bool
        errors.append("Both types in comparison must be the Integer")
        return bool

    @visitor.when(ast.LessThanNode)
    def visit(self, node, scope, errors):
        left = self.visit(node.left, scope, errors)
        right = self.visit(node.right, scope, errors)
        if left == right == int:
            return bool
        errors.append("Both types in comparison must be the Integer")
        return bool

    @visitor.when(ast.PropertyNode)
    def visit(self, node, scope, errors):
        return self.visit(node.expr)