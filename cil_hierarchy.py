class CILNode:
    pass

class CILProgramNode(CILNode):
    def __init__(self, dottypes, dotdata, dotcode):
        self.dottypes = dottypes
        self.dotdata = dotdata
        self.dotcode = dotcode

class CILTypeNode(CILNode):
    pass

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

class CILGetAttribNode(CILInstructionNode):
    pass

class CILSetAttribNode(CILInstructionNode):
    pass

class CILGetIndexNode(CILInstructionNode):
    pass

class CILSetIndexNode(CILInstructionNode):
    pass

class CILAllocateNode(CILInstructionNode):
    pass

class CILArrayNode(CILInstructionNode):
    pass

class CILTypeOfNode(CILInstructionNode):
    pass

class CILLabelNode(CILInstructionNode):
    pass

class CILGotoNode(CILInstructionNode):
    pass

class CILGotoIfNode(CILInstructionNode):
    pass

class CILStaticCallNode(CILInstructionNode):
    pass

class CILDinamicCallNode(CILInstructionNode):
    pass

class CILArgNode(CILInstructionNode):
    pass

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