# ===============================================================
# =======================AST=HIERARCHY===========================
# ===============================================================

ERROR = 0
INTEGER = 1


class Node:
    pass


class ProgramNode(Node):
    def __init__(self, expr):
        self.expr = expr

class ExpressionNode(Node):
    pass

class UtilNode(Node):
    pass

class BinaryOperatorNode(ExpressionNode):
    def __init__(self, left, right):
        self.left = left
        self.right = right

class UnaryOperator(ExpressionNode):
    def __init__(self, expr):
        self.expr = expr

class AtomicNode(ExpressionNode):
    pass


class PlusNode(BinaryOperatorNode):
    pass

class MinusNode(BinaryOperatorNode):
    pass


class StarNode(BinaryOperatorNode):
    pass

class DivNode(BinaryOperatorNode):
    pass

class NegationNode(UnaryOperator):
    pass

class NotNode(UnaryOperator):
    pass

class ComplementNode(UnaryOperator):
    pass

class LetInNode(AtomicNode):
    def __init__(self, declaration_list, expr):
        self.declaration_list = declaration_list
        self.expr = expr

class BlockNode(AtomicNode):
    def __init__(self, expr_list):
        self.expr_list = expr_list

class AssignNode(AtomicNode):
    def __init__(self, idx_token, expr):
        self.idx_token = idx_token
        self.expr = expr
        self.variable_info = None


class NewNode(AtomicNode):
    def __init__(self, type_token):
        self.type_token = type_token

class ClassNode(AtomicNode):
    def __init__(self, idx_token, inherit_token, cexpresion):
        self.idx_token = idx_token
        self.inherit_token = inherit_token
        self.cexpresion = cexpresion

class IfNode(AtomicNode):
    def __init__(self, conditional_token, expr, else_expr):
        self.conditional_token = conditional_token
        self.expr = expr
        self.else_expr = else_expr

class PropertyNode(AtomicNode):
    def __init__(self, decl):
        self.decl = decl

class MethodNode(AtomicNode):
    def __init__(self, name, params, ret_type, body):
        self.name = name
        self.params = params
        self.ret_type = ret_type
        self.body = body

class IsVoidNode(AtomicNode):
    def __init__(self, expr):
        self.expr = expr


class WhileNode(AtomicNode):
    def __init__(self, conditional_token, expr):
        self.conditional_token = conditional_token
        self.expr = expr


class CaseNode(AtomicNode):
    def __init__(self, expr, expresion_list):
        self.expr = expr
        self.expresion_list = expresion_list

class CaseItemNode(AtomicNode):
    def __init__(self, variable, expr):
        self.variable = variable
        self.expr = expr

class DispatchNode(AtomicNode):
    def __init__(self, idx_token, expresion_list):
        self.idx_token = idx_token
        self.expresion_list = expresion_list

class IntegerNode(AtomicNode):
    def __init__(self, integer_token):
        self.integer_token = int(integer_token)


class VariableNode(AtomicNode):
    def __init__(self, idx_token):
        self.idx_token = idx_token
        self.variable_info = None

class StringNode(AtomicNode):
    def __init__(self, string):
        self.string = str(string)

class PrintIntegerNode(AtomicNode):
    def __init__(self, expr):
        self.expr = expr


class PrintStringNode(AtomicNode):
    def __init__(self, string_token):
        self.string_token = string_token


class ScanNode(AtomicNode):
    pass

class DeclarationNode(UtilNode):
    def __init__(self, idx_token, type_token = None , expr = None):
        self.idx_token = idx_token
        self.expr = expr
        self.type_token = type_token
        self.variable_info = None

# ===============================================================
class BooleanNode():
    def __init__(self, val):
        self.value = val


class DispatchParentInstanceNode():
    def __init__(self, variable, parent, method, params):
        self.variable = variable
        self.parent = parent
        self.method = method
        self.params = params

class DispatchInstanceNode():
    def __init__(self, variable, method, params):
        self.variable = variable
        self.method = method
        self.params = params

class LessThanNode(BinaryOperatorNode):
    pass

class LessEqualNode(BinaryOperatorNode):
    pass

class EqualNode(BinaryOperatorNode):
    pass