import cil_hierarchy as cil
import visitor

class MIPSWriterVisitor(object):
    def __init__(self):
        self.output = []
        self.sp = 0
        self.gp = 0
        self.args = []

    def emit(self, msg):
        self.output.append(msg + '\n')

    def black(self):
        self.output.append('\n')

    def get_value(self, value):
        return value if isinstance(value, int) else value.name

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(cil.CILProgramNode)
    def visit(self, node:cil.CILProgramNode):
        self.emit('.TYPES')
        for x in node.dottypes:
            self.visit(x)
        self.black()

        self.emit('.data')
        for x in node.dotdata:
            self.visit(x)
        self.black()

        self.emit('.text')
        for x in node.dotcode:
            self.visit(x)


    @visitor.when(cil.CILTypeNode)
    def visit(self, node:cil.CILTypeNode):
        size = (len(node.attributes) + len(node.methods)) * 4 + 4
        attributes_offset = 4
        methods_offset = size - len(node.methods) * 4

        self.emit(f'TYPE {node.name} {{')
        for attr in node.attributes:
            self.emit(f'attribute {attr};')
        for instance_name, real_name in node.methods.items():
            self.emit(f'method {instance_name} : {real_name};')
        self.emit('}')
        i = 0
        for name, method in node.methods.items():
            method.mips_position = methods_offset + i
            self.emit(f'    la $t0, {method.cil_name}')
            self.emit(f'    sw $t0, {method.mips_position}($v0)')
            i += 4

    @visitor.when(cil.CILDataNode)
    def visit(self, node:cil.CILDataNode):
        self.emit(f'{node.vname}: .asciiz "{node.value}"')

    @visitor.when(cil.CILFunctionNode)
    def visit(self, node:cil.CILFunctionNode):
        self.black()

        self.emit(f'{node.fname}:')

        offset = len(node.params) * 4
        for x in node.params:
            self.visit(x, offset)
            offset -= 4
        if node.params:
            self.black()

        self.sp = 0
        sp = len(node.localvars) * 4
        self.emit(f'    subu $sp, $sp, {sp}')

        for x in node.localvars:
            self.visit(x)
        if node.localvars:
            self.black()

        for x in node.instructions:
            self.visit(x)

        self.emit(f'    addu $sp, $sp, {sp}')
        self.emit(f'    j $ra')

    @visitor.when(cil.CILParamNode)
    def visit(self, node:cil.CILParamNode, offset):
        node.param_name.vmholder = offset
        pass

    @visitor.when(cil.CILLocalNode)
    def visit(self, node:cil.CILLocalNode):
        self.emit(f'    li $t0, 0')
        self.emit(f'    sw $t0, {self.sp}($sp)')
        node.vinfo.vmholder = self.sp
        self.sp += 4

    @visitor.when(cil.CILAssignNode)
    def visit(self, node:cil.CILAssignNode):
        if type(node.source) == int:
            self.emit(f'    li $t0, {node.source}')
        else:
            self.emit(f'    lw $t0, {node.source.vinfo.vmholder}($sp)')
        self.emit(f'    sw $t0, {node.dest.vinfo.vmholder}($sp)')

    @visitor.when(cil.CILPlusNode)
    def visit(self, node:cil.CILPlusNode):
        dest = node.dest.name
        left = self.get_value(node.left)
        right = self.get_value(node.right)
        self.emit(f'    {dest} = {left} + {right}')

    @visitor.when(cil.CILMinusNode)
    def visit(self, node:cil.CILMinusNode):
        dest = node.dest.name
        left = self.get_value(node.left)
        right = self.get_value(node.right)
        self.emit(f'    {dest} = {left} - {right}')

    @visitor.when(cil.CILStarNode)
    def visit(self, node:cil.CILStarNode):
        dest = node.dest.name
        left = self.get_value(node.left)
        right = self.get_value(node.right)
        self.emit(f'    {dest} = {left} * {right}')

    @visitor.when(cil.CILDivNode)
    def visit(self, node:cil.CILDivNode):
        dest = node.dest.name
        left = self.get_value(node.left)
        right = self.get_value(node.right)
        self.emit(f'    {dest} = {left} / {right}')

    @visitor.when(cil.CILGetAttribNode)
    def visit(self, node:cil.CILGetAttribNode):
        dst = self.get_value(node.dest)
        objname = self.get_value(node.type_scr)
        self.emit(f'    {dst} = GETATTR {objname} {node.attr_addr}')

    @visitor.when(cil.CILSetAttribNode)
    def visit(self, node:cil.CILSetAttribNode):
        val = self.get_value(node.value)
        typ = self.get_value(node.type_scr)
        self.emit(f'    SETATTR {typ} {node.attr_addr} {val}')

    @visitor.when(cil.CILGetIndexNode)
    def visit(self, node:cil.CILGetIndexNode):
        pass

    @visitor.when(cil.CILSetIndexNode)
    def visit(self, node:cil.CILSetIndexNode):
        pass

    @visitor.when(cil.CILAllocateNode)
    def visit(self, node:cil.CILAllocateNode):
        size = (len(node.alloc_type.attributes) + len(node.alloc_type.methods)) * 4 + 4
        self.emit('    li $a0, 9')
        self.emit(f'    li $v0, {size}')
        self.emit('    syscall')
        self.emit(f'    sw $v0, {node.dst.vmholder}($sp)')
        node.dst.type = node.alloc_type
        for name, method in node.alloc_type.methods.items():
            self.emit(f'    la $t0, {method.cil_name}')
            self.emit(f'    sw $t0, {method.mips_position}($v0)')

    @visitor.when(cil.CILArrayNode)
    def visit(self, node:cil.CILArrayNode):
        pass

    @visitor.when(cil.CILTypeOfNode)
    def visit(self, node:cil.CILTypeOfNode):
        val = self.get_value(node.src)
        self.emit(f'    {node.dst} = TYPEOF {val}')

    @visitor.when(cil.CILLabelNode)
    def visit(self, node:cil.CILLabelNode):
        self.emit(f'{node.lname}:')

    @visitor.when(cil.CILGotoNode)
    def visit(self, node:cil.CILGotoNode):
        self.emit(f'    GOTO {node.lname.lname}')

    @visitor.when(cil.CILGotoIfNode)
    def visit(self, node:cil.CILGotoIfNode):
        val = self.get_value(node.conditional_value)
        self.emit(f'    GOTOIF {val} {node.lname.lname}')

    @visitor.when(cil.CILStaticCallNode)
    def visit(self, node:cil.CILStaticCallNode):
        pass

    @visitor.when(cil.CILDinamicCallNode)
    def visit(self, node:cil.CILDinamicCallNode):
        dest = self.get_value(node.dest_address)
        self.emit(f'    {dest} = VCALL {node.type_name} {node.func_name}')

    @visitor.when(cil.CILArgNode)
    def visit(self, node:cil.CILArgNode):
        val = self.get_value(node.arg_name)
        self.args.append(val)
        self.emit(f'    ARG {val}')

    @visitor.when(cil.CILReturnNode)
    def visit(self, node:cil.CILReturnNode):
        if type(node.value) == int:
            self.emit(f'    li $v0, {node.value}')
        else:
            self.emit(f'    lw $v0, {node.value.vmholder}($sp)')

    @visitor.when(cil.CILLoadNode)
    def visit(self, node:cil.CILLoadNode):
        self.emit(f'    lw $t0, {node.msg.vname}')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILLengthNode)
    def visit(self, node:cil.CILLengthNode):
        pass

    @visitor.when(cil.CILConcatNode)
    def visit(self, node:cil.CILConcatNode):
        pass

    @visitor.when(cil.CILPrefixNode)
    def visit(self, node:cil.CILPrefixNode):
        pass

    @visitor.when(cil.CILSubstringNode)
    def visit(self, node:cil.CILSubstringNode):
        pass

    @visitor.when(cil.CILToStrNode)
    def visit(self, node:cil.CILToStrNode):
        dest = node.dest.name
        ivalue = self.get_value(node.ivalue)
        self.emit(f'    {dest} = STR {ivalue}')

    @visitor.when(cil.CILReadNode)
    def visit(self, node:cil.CILReadNode):
        dest = node.dest.name
        self.emit(f'    {dest} = READ')

    @visitor.when(cil.CILPrintNode)
    def visit(self, node:cil.CILPrintNode):
        self.emit(f'    PRINT {node.str_addr.name}')

    @visitor.when(cil.CILEqualNode)
    def visit(self, node: cil.CILEqualNode):
        var = self.get_value(node.dest)
        left = self.get_value(node.left)
        right = self.get_value(node.right)
        self.emit(f'    {var} = {left} == {right}')

    @visitor.when(cil.CILLessThanNode)
    def visit(self, node: cil.CILEqualNode):
        var = self.get_value(node.dest)
        left = self.get_value(node.left)
        right = self.get_value(node.right)
        self.emit(f'    {var} = {left} < {right}')

    @visitor.when(cil.CILLessEqualNode)
    def visit(self, node: cil.CILEqualNode):
        var = self.get_value(node.dest)
        left = self.get_value(node.left)
        right = self.get_value(node.right)
        self.emit(f'    {var} = {left} <= {right}')

    @visitor.when(cil.CILCheckHierarchy)
    def visit(self, node: cil.CILCheckHierarchy):
        var = self.get_value(node.dest)
        b = self.get_value(node.b)
        self.emit(f'    {var} = INHERITS {b} {node.a}')

    @visitor.when(cil.CILCheckTypeHierarchy)
    def visit(self, node: cil.CILCheckTypeHierarchy):
        var = self.get_value(node.dest)
        self.emit(f'    {var} = TYPE_INHERITS {node.b} {node.a}')

    @visitor.when(cil.CILErrorNode)
    def visit(self, node: cil.CILErrorNode):
        self.emit(f'    ERROR')