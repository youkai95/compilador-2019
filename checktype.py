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
        return left == int and right == int

    @visitor.when(ast.MinusNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        return left == int and right == int

    @visitor.when(ast.StarNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        return left == int and right == int

    @visitor.when(ast.DivNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        return left == int and right == int

    @visitor.when(ast.NegationNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        return expr == int

    @visitor.when(ast.NotNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        return expr == bool

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
        node.variable_info.vmholder = expr
        return expr

    @visitor.when(ast.IntegerNode)
    def visit(self, node, tree, errors):
        return int

    @visitor.when(ast.VariableNode)
    def visit(self, node, tree, errors):
        return node.variable_info.vmholder

    @visitor.when(ast.PrintIntegerNode)
    def visit(self, node, tree, errors):
        expr = self.visit(node.expr, tree, errors)
        print(expr)
        return expr

    @visitor.when(ast.PrintStringNode)
    def visit(self, node, tree, errors):
        print(node.string_token.text_token)
        return 0

    @visitor.when(ast.ScanNode)
    def visit(self, node, tree, errors):
        return input()

    @visitor.when(ast.DeclarationNode)
    def visit(self, node, tree, errors):
        if node.expr is not None:
            expr = self.visit(node.expr, tree, errors)
            node.variable_info.vmholder = expr
        else:
            node.variable_info.vmholder = 0

    @visitor.when(ast.ClassNode)
    def visit(self, node, tree, errors):
        for expr in node.cexpresion:
            self.visit(expr, tree, errors)
        self.classType = tree.type_dict[node.idx_token]

    @visitor.when(ast.DispatchNode)
    def visit(self, node, tree, errors):
        temp = None
        clss = self.classType
        while temp and not clss.methods:
            for method in clss.methods:
                if method.name == node.idx_token:
                    temp = method
                    break
                clss = clss.parent

        if len(temp.param_types) == len(node.expresion_list):
            for i in range(len(node.expresion_list)):
                if self.visit(node.expresion_list[i], tree, errors).name != temp.param_types[i]:
                    errors.append("TODO")
        else:
            errors.append("TODO")
        return temp.ret_type


    @visitor.when(ast.DispatchInstanceNode)
    def visit(self, node, tree, errors):
        if node.expr is not None:
            pass
        else:
            pass

    @visitor.when(ast.DispatchParentInstanceNode)
    def visit(self, node, tree, errors):
        if node.expr is not None:
            pass
        else:
            pass

    @visitor.when(ast.MethodNode)
    def visit(self, node, tree, errors):
        self.visit(node.body, tree, errors)
        return self.visit(node.ret_type, tree, errors)

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
            pass

    @visitor.when(ast.IsVoidNode)
    def visit(self, node, tree, errors):
        return bool

    @visitor.when(ast.BooleanNode)
    def visit(self, node, tree, errors):
        return bool

    @visitor.when(ast.StringNode)
    def visit(self, node, tree, errors):
        return str

    @visitor.when(ast.WhileNode)
    def visit(self, node, tree, errors):
        self.visit(node.expr, tree, errors)
        if self.visit(node.conditional_token, tree, errors) != bool:
            errors.append("while condition must be boolean")
        return None

    @visitor.when(ast.IfNode)
    def visit(self, node, tree, errors):
        if self.visit(node.conditional_token, tree, errors) != bool:
            errors.append("if condition must be boolean")
        return self.visit(node.expr, tree, errors)

    @visitor.when(ast.EqualNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left != right:
            errors.append("Both types in equality must be the same")
        return bool

    @visitor.when(ast.LessEqualNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left == right == int:
            return bool
        errors.append("Both types in comparison must be Integer")
        return bool

    @visitor.when(ast.LessThanNode)
    def visit(self, node, tree, errors):
        left = self.visit(node.left, tree, errors)
        right = self.visit(node.right, tree, errors)
        if left == right == int:
            return bool
        errors.append("Both types in comparison must be Integer")
        return bool

    @visitor.when(ast.PropertyNode)
    def visit(self, node, tree, errors):
        return self.visit(node.decl, tree, errors)