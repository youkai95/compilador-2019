import itertools as itl

import ast_hierarchy as ast
import visitor
from scope import Scope
from typetree import ClassType, MethodType

ERROR = 0
INTEGER = 1

class CheckSemanticsVisitor:
    @visitor.on('node')
    def visit(self, node, scope, errors):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node, scope, errors):
        rtype = INTEGER
        for c in node.expr:
            rtype &= self.visit(c, scope, errors)
        return rtype

    @visitor.when(ast.BinaryOperatorNode)
    def visit(self, node, scope, errors):
        rleft = self.visit(node.left, scope, errors)
        rright = self.visit(node.right, scope, errors)
        return rleft and rright

    @visitor.when(ast.UnaryOperator)
    def visit(self, node, scope, errors):
        return self.visit(node.expr, scope, errors)

    @visitor.when(ast.LetInNode)
    def visit(self, node, scope, errors):
        child_scope = scope.create_child_scope()
        rtype = INTEGER
        for declaration in node.declaration_list:
            rtype &= self.visit(declaration, child_scope, errors)
        rtype &= self.visit(node.expr, child_scope, errors)
        return rtype

    @visitor.when(ast.BlockNode)
    def visit(self, node, scope, errors):
        rtype = INTEGER
        for expr in node.expr_list:
            rtype = self.visit(expr, scope, errors)
        return rtype

    @visitor.when(ast.AssignNode)
    def visit(self, node, scope, errors):
        rtype = self.visit(node.expr, scope, errors)
        vname = node.idx_token
        # if not scope.is_defined(vname):
        #     errors.append('Variable \'%s\' not defined.' % (vname))
        #     return ERROR
        node.variable_info = scope.get_variable_info(vname)
        if node.variable_info is None:
            node.variable_info = scope.define_variable(vname)

        return rtype

    @visitor.when(ast.NotNode)
    def visit(self, node, scope, errors):
        return self.visit(node.expr, scope, errors)

    @visitor.when(ast.NegationNode)
    def visit(self, node, scope, errors):
        return self.visit(node.expr, scope, errors)

    @visitor.when(ast.ComplementNode)
    def visit(self, node, scope, errors):
        return self.visit(node.expr, scope, errors)

    @visitor.when(ast.IntegerNode)
    def visit(self, node, scope, errors):
        return INTEGER

    @visitor.when(ast.StringNode)
    def visit(self, node, scope, errors):
        return INTEGER

    @visitor.when(ast.BooleanNode)
    def visit(self, node, scope, errors):
        return INTEGER

    @visitor.when(ast.VariableNode)
    def visit(self, node, scope, errors):
        vname = node.idx_token
        if not scope.is_defined(vname):
            errors.append('Variable \'%s\' not defined.' % (vname))
            return ERROR
        node.variable_info = scope.get_variable_info(vname)
        return INTEGER

    @visitor.when(ast.PrintIntegerNode)
    def visit(self, node, scope, errors):
        return self.visit(node.expr, scope, errors)

    @visitor.when(ast.PrintStringNode)
    def visit(self, node, scope, errors):
        return INTEGER

    @visitor.when(ast.ScanNode)
    def visit(self, node, scope, errors):
        return INTEGER

    @visitor.when(ast.DeclarationNode)
    def visit(self, node, scope, errors):
        rtype = INTEGER if node.expr is None else self.visit(node.expr, scope, errors)
        vname = node.idx_token
        if scope.is_local(vname):
            errors.append('Variable \'%s\' already defined.' % (vname))
            return ERROR
        node.variable_info = scope.define_variable(vname)
        return rtype

    @visitor.when(ast.CaseNode)
    def visit(self, node, scope, errors):
        rtype = self.visit(node.expr, scope, errors)
        for exp in node.expresion_list:
            rtype &= self.visit(exp, scope, errors)
        return rtype

    @visitor.when(ast.CaseItemNode)
    def visit(self, node, scope, errors):
        s = scope.create_child_scope()
        self.visit(node.variable, s, errors)
        return self.visit(node.expr, s, errors)

    @visitor.when(ast.IfNode)
    def visit(self, node, scope, errors):
        s = scope.create_child_scope()
        return self.visit(node.conditional_token, scope, errors) and self.visit(node.expr, s, errors) \
               and self.visit(node.else_expr, s, errors)

    @visitor.when(ast.WhileNode)
    def visit(self, node, scope, errors):
        s = scope.create_child_scope()
        return self.visit(node.conditional_token, scope, errors) and self.visit(node.expr, s, errors)

    @visitor.when(ast.NewNode)
    def visit(self, node, scope, errors):
        return INTEGER

    @visitor.when(ast.IsVoidNode)
    def visit(self, node, scope, errors):
        return self.visit(node.expr, scope, errors)

    @visitor.when(ast.DispatchInstanceNode)
    def visit(self, node, scope, errors):
        rtype = self.visit(node.variable, scope, errors)
        for p in node.params:
            rtype &= self.visit(p, scope, errors)
        return rtype

    @visitor.when(ast.DispatchNode)
    def visit(self, node, scope, errors):
        rtype = INTEGER
        for p in node.expresion_list:
            rtype &= self.visit(p, scope, errors)
        return rtype

    @visitor.when(ast.DispatchParentInstanceNode)
    def visit(self, node, scope, errors):
        #if not scope.is_defined(node.variable.idx_token):
        #    return ERROR
        rtype = self.visit(node.variable, scope, errors) #INTEGER
        for p in node.params:
            rtype &= self.visit(p, scope, errors)
        return rtype

    @visitor.when(ast.ClassNode)
    def visit(self, node, scope, errors):
        rtype = INTEGER
        s = scope.create_child_scope()
        # methods = []
        for p in node.cexpresion:
            # if type(p) is ast.MethodNode:
            #     params = []
            #     for d in p.params:
            #         params.append(d.type_token)
            #     methods.append(MethodType(p.name, p.ret_type, params))
            rtype &= self.visit(p, s, errors)
        # if rtype:
        #     if node.idx_token in scope.types.type_dict:
        #         errors.append("Error: Type %s already defined" % node.idx_token)
        #         return ERROR
        #     parent = scope.types.type_dict["Object"]
        #     if node.inherit_token:
        #         if not node.inherit_token in scope.types.type_dict:
        #             errors.append("Error: Parent %s not defined" % node.inherit_token)
        #             return ERROR
        #         parent = scope.types.type_dict[node.inherit_token]
        #     scope.types.type_dict[node.idx_token] = ClassType(node.idx_token, parent, methods)
        return rtype

    @visitor.when(ast.MethodNode)
    def visit(self, node, scope, errors):
        s = scope.create_child_scope()
        names = set()
        for p in node.params:
            length = len(names)
            names.add(p.idx_token)
            if length == len(names):
                errors.append("ERROR: parameter name '%s' at method '%s' already defined" % (p.idx_token, node.name))
                return ERROR
            self.visit(p, s, errors)
        return self.visit(node.body, s, errors)

    @visitor.when(ast.PropertyNode)
    def visit(self, node, scope, errors):
        return self.visit(node.decl, scope, errors)

