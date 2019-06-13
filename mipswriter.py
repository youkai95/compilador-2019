import cil_hierarchy as cil
import visitor
from scope import VariableInfo


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

    def check_hierarchy(self):
        self.emit(f'    check_hierarchy:')
        self.emit(f'    la $t0, $a0')
        self.emit(f'    la $t1, $a1')
        self.emit(f'    xor $t2, $t2, $t2')
        self.emit(f'    beq $t0, $t1, goodend_check_hierarchy')

        self.emit(f'    loop_check_hierarchy:')
        self.emit(f'    lw $t1, 4($t1)')
        self.emit(f'    beq $t1, $t2, badend_check_hierarchy')
        self.emit(f'    beq $t0, $t1, goodend_check_hierarchy')
        self.emit(f'    j loop_check_hierarchy_check_hierarchy')
        self.emit(f'    badend_check_hierarchy:')
        self.emit(f'    li $v0, 0')
        self.emit(f'    j $ra')
        self.emit(f'    goodend_check_hierarchy:')
        self.emit(f'    li $v0, 1')
        self.emit(f'    jr $ra')

    def lenght(self):
        self.emit(f'    lenght:')
        self.emit(f'    xor $t0, $t0, $t0') #letras
        self.emit(f'    xor $t1, $t1, $t1') #cero
        self.emit(f'    xor $v0, $v0, $v0') #result
        self.emit(f'    loop_lenght:')
        self.emit(f'    lb $t0, ($a0)')
        self.emit(f'    beq $t0, $t1, end_lenght')
        self.emit(f'    addu $v0, $v0, 1')
        self.emit(f'    addu $a0, $a0, 1')
        self.emit(f'    j loop_lenght')
        self.emit(f'    end_lenght:')
        self.emit(f'    j $ra')

    def concat(self):
        self.emit(f'    concat:')
        self.emit(f'    xor $t0, $t0, $t0')  # letras
        self.emit(f'    xor $t1, $t1, $t1')  # cero
        #self.emit(f'    xor $v0, $v0, $v0')  # result
        #self.emit(f'    la $v0, ($a2)')
        self.emit(f'    loop_concat1:')
        self.emit(f'    lb $t0, ($a0)')
        self.emit(f'    beq $t0, $t1, concat2')
        self.emit(f'    sb $t0, ($a2)')
        self.emit(f'    add $a0, $a0, 1')
        self.emit(f'    add $a2, $a2, 1')
        self.emit(f'    j loop_concat1')
        self.emit(f'    concat2:')
        #self.emit(f'    xor $t0, $t0, $t0')
        self.emit(f'    loop_concat2:')
        self.emit(f'    lb $t0, ($a1)')
        self.emit(f'    beq $t0, $t1, end_concat')
        self.emit(f'    sb $t0, ($a2)')
        self.emit(f'    add $a1, $a1, 1')
        self.emit(f'    add $a2, $a2, 1')
        self.emit(f'    j loop_concat2')
        self.emit(f'    end_concat:')
        self.emit(f'    sb $t1, ($a2)')
        self.emit(f'    j $ra')

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(cil.CILProgramNode)
    def visit(self, node:cil.CILProgramNode, type_tree):
        self.emit('.TYPES')
        for x in node.dottypes:
            self.visit(x)
        self.black()

        self.emit('.data')
        for t in type_tree.type_dict:
            node.dotdata.append(cil.CILDataNode(VariableInfo(t), t))
        for x in node.dotdata:
            self.visit(x)
        self.black()

        self.emit('.text')
        lenght = 8*len(type_tree.type_dict)
        self.emit(f'    li $t0, {lenght}')
        self.emit(f'    $v0, li')
        self.emit(f'    $a0, 9')
        self.emit(f'    syscall')
        self.emit(f'    li $gp, v0')
        i = 0
        for t in type_tree.type_dict:
            type_tree.type_dict[t].pos = i*8
            pos = i*8
            self.emit(f'    li $t0, $gp')
            self.emit(f'    add $t0, $t0, {pos}')
            self.emit(f'    la $t1, {t}')
            self.emit(f'    sw $t1, $t0')
            i += 1

        i = 0
        for t in type_tree.type_dict:
            pos = i*8 + 4
            self.emit(f'    li $t0, $gp')
            self.emit(f'    add $t0, $t0, {pos}')
            self.emit(f'    li $t1, {type_tree.type_dict[t].parent.pos}')
            self.emit(f'    sw $t1, $t0')

        for x in node.dotcode:
            self.visit(x)


    @visitor.when(cil.CILTypeNode)
    def visit(self, node:cil.CILTypeNode):
        self.emit(f'TYPE {node.name} {{')
        for attr in node.attributes:
            self.emit(f'attribute {attr};')
        for instance_name, real_name in node.methods.items():
            self.emit(f'method {instance_name} : {real_name};')
        self.emit('}')

    @visitor.when(cil.CILDataNode)
    def visit(self, node:cil.CILDataNode):
        self.emit(f'{node.vname} = {node.value}')

    @visitor.when(cil.CILFunctionNode)
    def visit(self, node:cil.CILFunctionNode):
        self.black()
        self.emit(f'{node.fname}:')

        for x in node.params:
            self.visit(x)
        if node.params:
            self.black()

        sp = len(node.localvars) * 4
        self.emit(f'    subu $sp, $sp, {sp}')

        for x in node.localvars:
            self.visit(x)
        if node.localvars:
            self.black()

        for x in node.instructions:
            self.visit(x)

        self.emit(f'    addu $sp, $sp, {sp}')

    @visitor.when(cil.CILParamNode)
    def visit(self, node:cil.CILParamNode):
        pass

    @visitor.when(cil.CILLocalNode)
    def visit(self, node:cil.CILLocalNode):
        self.emit(f'    li $t1, 0')
        self.emit(f'    sw $t1, {self.sp}($sp)')
        node.vinfo.vmholder = self.sp
        self.sp += 4

    @visitor.when(cil.CILAssignNode)
    def visit(self, node:cil.CILAssignNode):
        self.emit(f'    lw $t1 {node.source.vinfo.vmholder}($sp)')
        self.emit(f'    sw $t1 {node.dest.vinfo.vmholder}($sp)')

    @visitor.when(cil.CILPlusNode)
    def visit(self, node:cil.CILPlusNode):
        left = self.get_value(node.left)
        self.emit(f'    li $t1, {left}')
        right = self.get_value(node.right)
        self.emit(f'    li $t2, {right}')
        self.emit(f'    add $t0, {left}, {right}')
        self.emit(f'    sw $t0, {node.dest.vinfo.vmholder}($sp)')

    @visitor.when(cil.CILMinusNode)
    def visit(self, node:cil.CILMinusNode):
        left = self.get_value(node.left)
        self.emit(f'    li $t1, {left}')
        right = self.get_value(node.right)
        self.emit(f'    li $t2, {right}')
        self.emit(f'    sub $t0, {left}, {right}')
        self.emit(f'    sw $t0, {node.dest.vinfo.vmholder}($sp)')

    @visitor.when(cil.CILStarNode)
    def visit(self, node:cil.CILStarNode):
        left = self.get_value(node.left)
        self.emit(f'    li $t1, {left}')
        right = self.get_value(node.right)
        self.emit(f'    li $t2, {right}')
        self.emit(f'    mulo $t0, {left}, {right}')
        self.emit(f'    sw $t0, {node.dest.vinfo.vmholder}($sp)')

    @visitor.when(cil.CILDivNode)
    def visit(self, node:cil.CILDivNode):
        left = self.get_value(node.left)
        self.emit(f'    li $t1, {left}')
        right = self.get_value(node.right)
        self.emit(f'    li $t2, {right}')
        self.emit(f'    div {left}, {right}')
        self.visit(f'   mflo $t0')
        self.emit(f'    sw $t0, {node.dest.vinfo.vmholder}($sp)')

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
        dst = self.get_value(node.dst)
        self.emit(f"    {dst} = ALLOCATE {node.alloc_type}")

    @visitor.when(cil.CILArrayNode)
    def visit(self, node:cil.CILArrayNode):
        pass

    @visitor.when(cil.CILTypeOfNode)
    def visit(self, node:cil.CILTypeOfNode):
        val = self.get_value(node.src)
        self.emit(f'    {node.dst} = TYPEOF {val}')

    @visitor.when(cil.CILLabelNode)
    def visit(self, node:cil.CILLabelNode):
        self.emit(f'    LABEL {node.lname}')

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
        value = self.get_value(node.value)
        value = "" if value is None else str(value)
        self.emit(f'    RETURN {value}')

    @visitor.when(cil.CILLoadNode)
    def visit(self, node:cil.CILLoadNode):
        dest = node.dest.name
        self.emit(f'    {dest} = LOAD {node.msg.vname}')

    @visitor.when(cil.CILLengthNode)
    def visit(self, node:cil.CILLengthNode):
        self.emit(f'    lw $a0, {node.src.vmholder}($sp)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal lenght')
        self.lenght()
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    sw  $v0, {node.dest.vinfo.vmholder}($sp)')

    @visitor.when(cil.CILConcatNode)
    def visit(self, node:cil.CILConcatNode):
        self.emit(f'    lw $a0, {node.str.vmholder}($sp)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal lenght')
        self.lenght()
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    la $t0, $v0')
        self.emit(f'    lw $a0, {node.src.vmholder}($sp)')
        self.emit(f'    subu $sp, $sp, 8')
        self.emit(f'    sw $ra, 4($sp)')
        self.emit(f'    sw $t0, ($sp)')
        self.emit(f'    jal lenght')
        self.lenght()
        self.emit(f'    lw $t0, ($sp)')
        self.emit(f'    lw $ra, 4($sp)')
        self.emit(f'    addu $sp, $sp, 8')
        self.emit(f'    addu $v0, $v0, $t0')
        self.emit(f'    addu $v0, $v0, 1')
        self.emit(f'    li $a0, 9')
        self.emit(f'    syscall')
        self.emit(f'    la $a2, $v0')
        self.emit(f'    lb $a0, {node.str.vmholder}($sp)')
        self.emit(f'    lb $a0, ($a0)')
        self.emit(f'    lb $a1, {node.src.vmholder}($sp)')
        self.emit(f'    lb $a1, ($a1)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal concat')
        self.concat()
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    sw  $v0, {node.dest.vinfo.vmholder}($sp)')

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
        def visit(self, node: cil.CILLessEqualNode):
            left = self.get_value(node.left)
            self.emit(f'    li $t1, {left}')
            right = self.get_value(node.right)
            self.emit(f'    li $t2, {right}')
            self.emit(f'    seq $t0, $t1, $t2')
            self.emit(f'    sw $t0, {node.dest.vinfo.vmholder}($sp)')

    @visitor.when(cil.CILLessThanNode)
    def visit(self, node: cil.CILLessThanNode):
        left = self.get_value(node.left)
        self.emit(f'    li $t1, {left}')
        right = self.get_value(node.right)
        self.emit(f'    li $t2, {right}')
        self.emit(f'    stl $t0, $t1, $t2')
        self.emit(f'    sw $t0, {node.dest.vinfo.vmholder}($sp)')

    @visitor.when(cil.CILLessEqualNode)
    def visit(self, node: cil.CILLessEqualNode):
        left = self.get_value(node.left)
        self.emit(f'    li $t1, {left}')
        right = self.get_value(node.right)
        self.emit(f'    li $t2, {right}')
        self.emit(f'    sle $t0, $t1, $t2')
        self.emit(f'    sw $t0, {node.dest.vinfo.vmholder}($sp)')

    @visitor.when(cil.CILCheckHierarchy)
    def visit(self, node: cil.CILCheckHierarchy):
        self.emit(f'    lw $a0, {node.a.vmholder}($sp)')
        self.emit(f'    lw $a0, ($a0)')
        self.emit(f'    lw $a1, ($gp)')
        self.emit(f'    add $a1, $a1, {node.b.pos}')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal check_hierarchy')
        self.check_hierarchy()
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    sw $v0, {node.dest.vinfo.vmholder}($sp)')

    # @visitor.when(cil.CILCheckTypeHierarchy)
    # def visit(self, node: cil.CILCheckTypeHierarchy):
    #     var = self.get_value(node.dest)
    #     self.emit(f'    {var} = TYPE_INHERITS {node.b} {node.a}')

    @visitor.when(cil.CILErrorNode)
    def visit(self, node: cil.CILErrorNode):
        self.emit(f'    break 0')

    @visitor.when(cil.CILNotNode)
    def visit(self, node: cil.CILNotNode):
        var = self.get_value(node.expr)
        self.emit(f'    li $t0, {var}')
        self.emit(f'    not $t0, $t0')
        self.emit(f'    sw $t0, {node.dest.vinfo.vmholder}($sp)')
