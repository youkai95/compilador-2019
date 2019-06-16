class CILNode:
    pass

class CILProgramNode(CILNode):
    def __init__(self, dottypes, dotdata, dotcode):
        self.dottypes = dottypes
        self.dotdata = dotdata
        self.dotcode = dotcode

class CILTypeNode(CILNode):
    def __init__(self, name, attributes, methods):
        self.name = name
        self.attributes = attributes
        self.methods = methods
        self.pos = 0

class CILDataNode(CILNode):
    def __init__(self, vname, value):
        self.vname = vname
        self.value = value

class CILFunctionNode(CILNode):
    def __init__(self, fname, params, localvars, instructions):
        self.fname = fname
        self.params = params
        self.localvars = localvars
        self.instructions = instructions

class CILParamNode(CILNode):
    def __init__(self, param_name):
        self.param_name = param_name

class CILLocalNode(CILNode):
    def __init__(self, vinfo):
        self.vinfo = vinfo

class CILInstructionNode(CILNode):
    pass

class CILAssignNode(CILInstructionNode):
    def __init__(self, dest, source):
        self.dest = dest
        self.source = source

class CILArithmeticNode(CILInstructionNode):
    def __init__(self, dest, left, right):
        self.dest = dest
        self.left = left
        self.right = right

class CILPlusNode(CILArithmeticNode):
    pass

class CILMinusNode(CILArithmeticNode):
    pass

class CILStarNode(CILArithmeticNode):
    pass

class CILDivNode(CILArithmeticNode):
    pass

class CILEqualNode(CILArithmeticNode):
    pass

class CILLessThanNode(CILArithmeticNode):
    pass

class CILLessEqualNode(CILArithmeticNode):
    pass

class CILCheckHierarchy(CILInstructionNode):
    def __init__(self, dest, a, b):
        self.dest = dest
        self.a = a
        self.b = b

# class CILCheckTypeHierarchy(CILInstructionNode):
#     def __init__(self, dest, a, b):
#         self.dest = dest
#         self.a = a
#         self.b = b

class CILGetAttribNode(CILInstructionNode):
    def __init__(self, dest, type_src, attr_addr):
        self.type_scr = type_src
        self.attr_addr = attr_addr
        self.dest = dest

class CILNotNode(CILInstructionNode):
    def __init__(self, expr, dst):
        self.expr = expr
        self.dst = dst

class CILComplementNode(CILInstructionNode):
    def __init__(self, expr, dst):
        self.expr = expr
        self.dst = dst

class CILErrorNode(CILInstructionNode):
    pass

class CILSetAttribNode(CILInstructionNode):
    def __init__(self, type_src, attr_addr, value):
        self.type_scr = type_src
        self.attr_addr = attr_addr
        self.value = value

class CILGetIndexNode(CILInstructionNode):
    def __init__(self, array_src, position, dst):
        self.array_src = array_src
        self.position = position
        self.dst = dst

class CILSetIndexNode(CILInstructionNode):
    def __init__(self, array_src, position, value):
        self.array_src = array_src
        self.position = position
        self.value = value

class CILAllocateNode(CILInstructionNode):
    def __init__(self, alloc_type, dst):
        self.alloc_type = alloc_type
        self.dst = dst

class CILArrayNode(CILInstructionNode):
    pass

class CILTypeOfNode(CILInstructionNode):
    def __init__(self, src, dst):
        self.src = src
        self.dst = dst

class CILLabelNode(CILInstructionNode):
    def __init__(self, lname):
        self.lname = lname

class CILGotoNode(CILInstructionNode):
    def __init__(self, lname):
        self.lname = lname

class CILGotoIfNode(CILInstructionNode):
    def __init__(self, conditional_value, lname):
        self.conditional_value = conditional_value
        self.lname = lname

class CILStaticCallNode(CILInstructionNode):
    def __init__(self, type_name, func_name, dest_addr):
        self.type_name = type_name
        self.func_name = func_name
        self.dest_address = dest_addr

class CILDinamicCallNode(CILInstructionNode):
    def __init__(self, type_name, func_name, dest_addr):
        self.type_name = type_name
        self.func_name = func_name
        self.dest_address = dest_addr

class CILArgNode(CILInstructionNode):
    def __init__(self, arg_name):
        self.arg_name = arg_name

class CILReturnNode(CILInstructionNode):
    def __init__(self, value=None):
        self.value = value

class CILLoadNode(CILInstructionNode):
    def __init__(self, dest, msg):
        self.dest = dest
        self.msg = msg

#Object
class CILAbortNode(CILInstructionNode):
    def __init__(self, selftype):
        self.selftype = selftype

#String
class CILLengthNode(CILInstructionNode):
    def __init__(self, src, dest):
        self.src = src
        self.dest = dest

class CILConcatNode(CILInstructionNode):
    def __init__(self, str, src, dest):
        self.str = str
        self.src = src
        self.dest = dest

class CILPrefixNode(CILInstructionNode):
    pass

class CILSubstringNode(CILInstructionNode):
    def __init__(self, src, i, l, dest):
        self.i = i
        self.l = l
        self.src = src
        self.dest = dest

class CILToStrNode(CILInstructionNode):
    def __init__(self, dest, ivalue):
        self.dest = dest
        self.ivalue = ivalue

class CILReadIntNode(CILInstructionNode):
    def __init__(self, dest):
        self.dest = dest

class CILReadStringNode(CILInstructionNode):
    def __init__(self, dest):
        self.dest = dest

class CILPrintIntNode(CILInstructionNode):
    def __init__(self, src, str_addr):
        self.str_addr = str_addr
        self.src = src

class CILPrintStringNode(CILInstructionNode):
    def __init__(self, src, str_addr):
        self.str_addr = str_addr
        self.src = src

class CILEndProgram(CILInstructionNode):
    def __init__(self, expr):
        self.expr = expr

class CILBoxVariable(CILInstructionNode):
    def __init__(self, variable, dest):
        self.variable = variable
        self.dest = dest

class CILUnboxVariable(CILInstructionNode):
    def __init__(self, variable, dest):
        self.variable = variable
        self.dest = dest
