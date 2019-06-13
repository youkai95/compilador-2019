import cil_hierarchy as cil
import visitor
from cool_to_cil import CILFunction
from scope import VariableInfo


class MIPSWriterVisitor(object):
    def __init__(self):
        self.output = []
        self.sp = 0
        self.gp = 0
        self.args = []
        self.types = {}

    def emit(self, msg):
        self.output.append(msg + '\n')

    def black(self):
        self.output.append('\n')

    def get_value(self, value):
        return value if isinstance(value, int) else value.vmholder

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

    def substring(self):
        self.emit(f'substring:')
        self.emit(f'    xor $t1, $t1, $t1') #cero
        self.emit(f'    add $a0, $a0, a1')
        self.emit(f'write_substring:')
        self.emit(f'    lb $t0, ($a0)')
        self.emit(f'    beq $a2, $t1, end_substring')
        self.emit(f'    sb $t0, ($a3)')
        self.emit(f'    add $a0, $a0, 1')
        self.emit(f'    add $a3, $a3, 1')
        self.emit(f'    subu $a2, $a2, 1')
        self.emit(f'    j write_substring')
        self.emit(f'end_substring:')
        self.emit(f'    sb $t1, ($a3)')
        self.emit(f'    j $ra')


    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(cil.CILProgramNode)
    def visit(self, node:cil.CILProgramNode, type_tree):
        self.emit('.data')
        for t in type_tree.type_dict:
            node.dotdata.append(cil.CILDataNode(t, '"%s"' % t))
        for x in node.dotdata:
            self.visit(x)
        self.black()

        self.emit('.text')
        length = 0
        for x in node.dottypes:
            length += 8 + len(x.methods) * 4
            self.types[x.name] = x

        self.emit(f'    li $v0, 9')
        self.emit(f'    li $a0, {length}')
        self.emit(f'    syscall')
        self.emit(f'    sw $v0, ($gp)')
        pos = 0
        self.emit(f'    lw $t0, ($gp)')
        # for x in node.dottypes:
        #     self.visit(x, type_tree)
        # self.black()

        pos = 0
        for t in node.dottypes:
            l = len(t.methods) * 4
            t.pos = pos
            self.emit(f'    la $t1, {t.name}')
            self.emit(f'    sw $t1, 4($t0)')
            i = 0
            for name, method in t.methods.items():
                method.mips_position = 8 + i
                self.emit(f'    la $t2, {method.cil_name}')
                self.emit(f'    sw $t2, {method.mips_position}($t0)')
                i += 4
            pos += 8 + l
            self.emit(f'    add $t0, $t0, {8 + l}')

        self.emit(f'    lw $t0, ($gp)')
        self.emit(f'    lw $t2, ($gp)')
        for t in node.dottypes:
            l = len(t.methods) * 4
            if type_tree.type_dict[t.name].parent is None:
                self.emit(f'    li $t1, 0')
            else:
                self.emit(f'    li $t1, {self.types[type_tree.type_dict[t.name].parent.name].pos}')
                self.emit(f'    add $t1, $t1, $t2')
            self.emit(f'    sw $t1, ($t0)')
            self.emit(f'    add $t0, $t0, {8 + l}')

        for x in node.dotcode:
            self.visit(x)


    @visitor.when(cil.CILTypeNode)
    def visit(self, node:cil.CILTypeNode, type_tree):
        pass

    @visitor.when(cil.CILDataNode)
    def visit(self, node:cil.CILDataNode):
        self.emit(f'{node.vname}: .asciiz {node.value}')

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
        self.emit(f'    jr $ra')

    @visitor.when(cil.CILParamNode)
    def visit(self, node:cil.CILParamNode, offset):
        node.param_name.vmholder = offset

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
            self.emit(f'    lw $t0, {node.source.vmholder}($sp)')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILPlusNode)
    def visit(self, node:cil.CILPlusNode):
        left = self.get_value(node.left)
        self.emit(f'    li $t1, {left}')
        right = self.get_value(node.right)
        self.emit(f'    li $t2, {right}')
        self.emit(f'    add $t0, $t1, $t2')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILMinusNode)
    def visit(self, node:cil.CILMinusNode):
        left = self.get_value(node.left)
        self.emit(f'    li $t1, {left}')
        right = self.get_value(node.right)
        self.emit(f'    li $t2, {right}')
        self.emit(f'    sub $t0, $1, $2')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILStarNode)
    def visit(self, node:cil.CILStarNode):
        left = self.get_value(node.left)
        self.emit(f'    li $t1, {left}')
        right = self.get_value(node.right)
        self.emit(f'    li $t2, {right}')
        self.emit(f'    mulo $t0, $1, $2')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILDivNode)
    def visit(self, node:cil.CILDivNode):
        left = self.get_value(node.left)
        self.emit(f'    li $t1, {left}')
        right = self.get_value(node.right)
        self.emit(f'    li $t2, {right}')
        self.emit(f'    div $t1, $t2')
        self.visit(f'   mflo $t0')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')

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
        size = len(node.alloc_type.attributes) * 4 + 4
        self.emit(f'    li $a0, {size}')
        self.emit('    li $v0, 9')
        self.emit('    syscall')
        self.emit(f'    sw $v0, {node.dst.vmholder}($sp)')
        self.emit(f'    lw $t0, ($gp)')
        self.emit(f'    la $t1, {self.types[node.alloc_type.name].pos}($t0)')
        self.emit(f'    sw $t1, ($v0)')
        node.dst.type = node.alloc_type

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
        dest = self.get_value(node.dest_address)
        l = len(self.args) * 4
        p = 0
        self.emit(f'    lw $t1, {self.args[0].vmholder}($sp)')
        self.emit(f'    subu $sp, $sp, {l + 4}')
        self.emit(f'    sw $ra, {l}($sp)')
        for arg in self.args:
            if type(arg) != int:
                self.emit(f'    lw $t0, {l + 4 + arg.vmholder}($sp)')
                self.emit(f'    sw $t0, {p}($sp)')
            else:
                self.emit(f'    lw $t0, {arg}')
                self.emit(f'    sw $t0, {p}($sp)')
            p += 4
        self.emit(f'    jal {node.type_name}_{node.func_name}')
        self.emit(f'    lw $ra, {l}($sp)')
        self.emit(f'    addu $sp, $sp, {l + 4}')
        self.emit(f'    sw $v0, {node.dest_address.vmholder}($sp)')
        self.args.clear()

    @visitor.when(cil.CILDinamicCallNode)
    def visit(self, node:cil.CILDinamicCallNode):
        dest = self.get_value(node.dest_address)
        l = len(self.args) * 4
        p = 0
        self.emit(f'    lw $t1, {self.args[0].vmholder}($sp)')
        self.emit(f'    subu $sp, $sp, {l + 4}')
        self.emit(f'    sw $ra, {l}($sp)')
        for arg in self.args:
            if type(arg) != int:
                self.emit(f'    lw $t0, {l + 4 + arg.vmholder}($sp)')
                self.emit(f'    sw $t0, {p}($sp)')
            else:
                self.emit(f'    lw $t0, {arg}')
                self.emit(f'    sw $t0, {p}($sp)')
            p += 4
        self.emit(f'    lw $t1, ($t1)')
        self.emit(f'    lw $t0, {self.types[node.type_name].methods[node.func_name].mips_position}($t1)')
        self.emit(f'    jr $t0')
        self.emit(f'    lw $ra, {l}($sp)')
        self.emit(f'    addu $sp, $sp, {l + 4}')
        self.emit(f'    sw $v0, {node.dest_address.vmholder}($sp)')
        self.args.clear()

    @visitor.when(cil.CILArgNode)
    def visit(self, node:cil.CILArgNode):
        self.args.append(node.arg_name)

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

    # @visitor.when(cil.CILPrefixNode)
    # def visit(self, node:cil.CILPrefixNode):
    #     pass

    @visitor.when(cil.CILSubstringNode)
    def visit(self, node:cil.CILSubstringNode):
        self.emit(f'    la $a0, {node.src.vmholder}($sp)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal lenght')
        self.lenght()
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    li $t0, {node.i}')
        self.emit(f'    blt $t0, 0, error')
        self.emit(f'    li $t1, {node.l}')
        self.emit(f'    blt $t1, 0, error')
        self.emit(f'    add $t0, $t0, $t1')
        self.emit(f'    blt $v0, $t0, error')
        self.emit(f'    li $v0, 9')
        self.emit(f'    li $a0, {node.l}')
        self.emit(f'    syscall')
        self.emit(f'    la $a3, $v0')
        self.emit(f'    la $a0, {node.src.vmholder}($sp)')
        self.emit(f'    li $a1, {node.i}')
        self.emit(f'    li $a2, {node.l}')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal substring')
        self.substring()
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    sw  $v0, {node.dest.vinfo.vmholder}($sp)')

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
        self.emit(f'    error:')
        self.emit(f'    break 0')

    @visitor.when(cil.CILNotNode)
    def visit(self, node: cil.CILNotNode):
        var = self.get_value(node.expr)
        self.emit(f'    li $t0, {var}')
        self.emit(f'    not $t0, $t0')
        self.emit(f'    sw $t0, {node.dest.vinfo.vmholder}($sp)')
