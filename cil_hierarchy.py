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
    pass

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

class CILGetAttribNode(CILInstructionNode):
    def __init__(self, dest, type_src, attr_addr):
        self.type_scr = type_src
        self.attr_addr = attr_addr
        self.dest = dest

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
    pass

class CILDinamicCallNode(CILInstructionNode):
    pass

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

class CILLengthNode(CILInstructionNode):
    pass

class CILConcatNode(CILInstructionNode):
    pass

class CILPrefixNode(CILInstructionNode):
    pass

class CILSubstringNode(CILInstructionNode):
    pass

class CILToStrNode(CILInstructionNode):
    def __init__(self, dest, ivalue):
        self.dest = dest
        self.ivalue = ivalue

class CILReadNode(CILInstructionNode):
    def __init__(self, dest):
        self.dest = dest

class CILPrintNode(CILInstructionNode):
    def __init__(self, str_addr):
        self.str_addr = str_addr