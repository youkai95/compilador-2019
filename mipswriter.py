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
        self.selftype = None
        self.in_buffer = 0

    def emit(self, msg):
        self.output.append(msg + '\n')

    def black(self):
        self.output.append('\n')

    def get_value(self, value):
        return value if isinstance(value, int) else value.vmholder

    def check_hierarchy(self):
        self.emit(f'    check_hierarchy:')
        self.emit(f'    la $t0, ($a0)')
        self.emit(f'    la $t1, ($a1)')
        self.emit(f'    xor $t2, $t2, $t2')
        self.emit(f'    beq $t0, $t1, goodend_check_hierarchy')

        self.emit(f'    loop_check_hierarchy:')
        self.emit(f'    lw $t1, ($t1)')
        self.emit(f'    beq $t1, $t2, badend_check_hierarchy')
        self.emit(f'    beq $t0, $t1, goodend_check_hierarchy')
        self.emit(f'    j loop_check_hierarchy')
        self.emit(f'    badend_check_hierarchy:')
        self.emit(f'    li $v0, 0')
        self.emit(f'    jr $ra')
        self.emit(f'    goodend_check_hierarchy:')
        self.emit(f'    li $v0, 1')
        self.emit(f'    jr $ra')

    def length(self):
        self.emit(f'    length:')
        self.emit(f'    xor $t0, $t0, $t0') #letras
        self.emit(f'    xor $t1, $t1, $t1') #cero
        self.emit(f'    xor $v0, $v0, $v0') #result
        self.emit(f'    loop_length:')
        self.emit(f'    lb $t0, ($a0)')
        self.emit(f'    beq $t0, $t1, end_length')
        self.emit(f'    addu $v0, $v0, 1')
        self.emit(f'    addu $a0, $a0, 1')
        self.emit(f'    j loop_length')
        self.emit(f'    end_length:')
        self.emit(f'    jr $ra')

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
        self.emit(f'    jr $ra')

    def substring(self):
        self.emit(f'substring:')
        self.emit(f'    xor $t1, $t1, $t1') #cero
        self.emit(f'    add $a0, $a0, $a1')
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
        self.emit(f'    jr $ra')

    def unboxing(self):
        self.emit('unbox_variable:')
        self.emit(f'    lw $t0, 4($a0)')
        #self.emit(f'    lw $t0, ($t0)')
        self.emit(f'    beq $t0, 0, not_boxed')
        self.emit(f'    ld $v0, ($t0)')
        self.emit(f'    j end_unbox')
        self.emit(f'not_boxed:')
        self.emit(f'    ld $v0, ($a0)')
        self.emit(f'end_unbox:')
        self.emit(f'    jr $ra')



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
        for x in node.dottypes:
            self.in_buffer += 8 + len(x.methods) * 4
            self.types[x.name] = x

        pos = 0
        self.emit(f'    la $t0, ($gp)')
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

        self.emit(f'    la $t0, ($gp)')
        self.emit(f'    la $t2, ($gp)')
        for t in node.dottypes:
            l = len(t.methods) * 4
            if type_tree.type_dict[t.name].parent is None:
                self.emit(f'    li $t1, 0')
            else:
                self.emit(f'    li $t1, {self.types[type_tree.type_dict[t.name].parent.name].pos}')
                self.emit(f'    add $t1, $t1, $t2')
            self.emit(f'    sw $t1, ($t0)')
            self.emit(f'    add $t0, $t0, {8 + l}')

        self.emit(f'    li $a0, 128')
        self.emit(f'    li $v0, 9')
        self.emit(f'    syscall')
        self.emit(f'    sw $v0, {self.in_buffer}($gp)')

        for x in node.dotcode:
            self.visit(x)

        self.length()
        self.concat()
        self.substring()
        self.check_hierarchy()
        self.unboxing()

        self.emit(f'    error:')
        self.emit(f'    break 0')

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

        sp = len(node.localvars) * 8
        offset = sp + (len(node.params) - 1) * 8
        for x in node.params:
            self.visit(x, offset)
            offset -= 8
        if node.params:
            self.black()

        self.sp = 0
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
        self.emit(f'    sw $t0, {self.sp + 4}($sp)')
        node.vinfo.vmholder = self.sp
        self.sp += 8

    @visitor.when(cil.CILAssignNode)
    def visit(self, node:cil.CILAssignNode):
        #self.emit(f'    lw $t0, {node.dest.vmholder}($sp)')
        #self.emit(f'    lw $t1, {node.source.vmholder}($sp)')
        #self.emit(f'    la $t2, {self.types["Object"].pos}($gp)')
        #self.emit(f'    beq $t0, $t2, labb')

        if type(node.source) == int:
            self.emit(f'    la $t0, {self.types["Int"].pos}($gp)')
            self.emit(f'    li $t1, {node.source}')
        elif isinstance(node.source, bool):
            v = 1 if node.source else 0
            self.emit(f'    la $t0, {self.types["Bool"].pos}($gp)')
            self.emit(f'    li $t1, {v}')
        else:
            self.emit(f'    ld $t0, {node.source.vmholder}($sp)')
        self.emit(f'    sd $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILPlusNode)
    def visit(self, node:cil.CILPlusNode):
        if isinstance(node.right, int):
            self.emit(f'    li $t2, {node.right}')
        else:
            self.emit(f'    lw $t2, {node.right.vmholder + 4}($sp)')
        if isinstance(node.left, int):
            self.emit(f'    li $t1, {node.left}')
        else:
            self.emit(f'    lw $t1, {node.left.vmholder + 4}($sp)')

        self.emit(f'    add $t1, $t1, $t2')
        self.emit(f'    la $t0, {self.types["Int"].pos}($gp)')
        self.emit(f'    sd $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILMinusNode)
    def visit(self, node:cil.CILMinusNode):
        if isinstance(node.right, int):
            self.emit(f'    li $t2, {node.right}')
        else:
            self.emit(f'    lw $t2, {node.right.vmholder + 4}($sp)')
        if isinstance(node.left, int):
            self.emit(f'    li $t1, {node.left}')
        else:
            self.emit(f'    lw $t1, {node.left.vmholder + 4}($sp)')

        self.emit(f'    sub $t1, $t1, $t2')
        self.emit(f'    la $t0, {self.types["Int"].pos}($gp)')
        self.emit(f'    sd $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILStarNode)
    def visit(self, node:cil.CILStarNode):
        if isinstance(node.right, int):
            self.emit(f'    li $t2, {node.right}')
        else:
            self.emit(f'    lw $t2, {node.right.vmholder + 4}($sp)')
        if isinstance(node.left, int):
            self.emit(f'    li $t1, {node.left}')
        else:
            self.emit(f'    lw $t1, {node.left.vmholder + 4}($sp)')

        self.emit(f'    mulo $t1, $t1, $t2')
        self.emit(f'    la $t0, {self.types["Int"].pos}($gp)')
        self.emit(f'    sd $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILDivNode)
    def visit(self, node:cil.CILDivNode):
        if isinstance(node.right, int):
            self.emit(f'    li $t2, {node.right}')
        else:
            self.emit(f'    lw $t2, {node.right.vmholder + 4}($sp)')
        if isinstance(node.left, int):
            self.emit(f'    li $t1, {node.left}')
        else:
            self.emit(f'    lw $t1, {node.left.vmholder + 4}($sp)')

        self.emit(f'    div $t1, $t2')
        self.emit(f'    mflo $t1')
        self.emit(f'    la $t0, {self.types["Int"].pos}($gp)')
        self.emit(f'    sd $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILGetAttribNode)
    def visit(self, node:cil.CILGetAttribNode):
        attr_offset = self.types[node.type_scr.type.name].attributes.index(node.attr_addr) * 8
        self.emit(f'    lw $t0, {node.type_scr.vmholder + 4}($sp)')
        self.emit(f'    ld $t1, {attr_offset}($t0)')
        self.emit(f'    sd $t1, {node.dest.vmholder}($sp)')


    @visitor.when(cil.CILSetAttribNode)
    def visit(self, node:cil.CILSetAttribNode):
        value = self.get_value(node.value)
        attr_offset = self.types[node.type_scr.type.name].attributes.index(node.attr_addr) * 8
        self.emit(f'    lw $t0, {node.type_scr.vmholder + 4}($sp)')
        if type(node.value) == int:
            self.emit(f'    la $t1, {self.types["Int"].pos}($gp)')
            self.emit(f'    li $t2, {value}')
        elif isinstance(node.value, bool):
            v = 1 if node.value else 0
            self.emit(f'    la $t1, {self.types["Bool"].pos}($gp)')
            self.emit(f'    li $t2, {v}')
        else:
            self.emit(f'    ld $t1, {value}($sp)')
        self.emit(f'    sd $t1, {attr_offset}($t0)')

    @visitor.when(cil.CILGetIndexNode)
    def visit(self, node:cil.CILGetIndexNode):
        pass

    @visitor.when(cil.CILSetIndexNode)
    def visit(self, node:cil.CILSetIndexNode):
        pass

    @visitor.when(cil.CILAllocateNode)
    def visit(self, node:cil.CILAllocateNode):
        size = len(self.types[node.alloc_type.name].attributes) * 8
        self.emit(f'    li $a0, {size}')
        self.emit('    li $v0, 9')
        self.emit('    syscall')
        self.emit(f'    sw $v0, {node.dst.vmholder + 4}($sp)')
        self.emit(f'    la $t1, {self.types[node.alloc_type.name].pos}($gp)')
        self.emit(f'    sw $t1, {node.dst.vmholder}($sp)')
        node.dst.type = node.alloc_type

    @visitor.when(cil.CILArrayNode)
    def visit(self, node:cil.CILArrayNode):
        pass

    @visitor.when(cil.CILTypeOfNode)
    def visit(self, node:cil.CILTypeOfNode):
        self.emit(f'    lw $t1, {node.src.vmholder}($sp)')
        self.emit(f'    lw $t1, 4($t1)')
        self.emit(f'    la $t0, {self.types["String"].pos}($gp)')
        self.emit(f'    sd $t0, {node.dst.vmholder}($sp)')

    @visitor.when(cil.CILLabelNode)
    def visit(self, node:cil.CILLabelNode):
        self.emit(f'{node.lname}:')

    @visitor.when(cil.CILGotoNode)
    def visit(self, node:cil.CILGotoNode):
        self.emit(f'    j {node.lname.lname}')

    @visitor.when(cil.CILGotoIfNode)
    def visit(self, node:cil.CILGotoIfNode):
        if type(node.conditional_value) == int:
            self.emit(f'    li $t0 {node.conditional_value}')
        elif isinstance(node.conditional_value, bool):
            v = 1 if node.conditional_value else 0
            self.emit(f'    li $t0, {v}')
        else:
            self.emit(f'    lw $t0 {node.conditional_value.vmholder + 4}($sp)')

        self.emit(f'    beq $t0, 1, {node.lname.lname}')

    @visitor.when(cil.CILStaticCallNode)
    def visit(self, node:cil.CILStaticCallNode):
        dest = self.get_value(node.dest_address)
        l = len(self.args) * 8
        p = 8
        #self.emit(f'    lw $t1, {self.args[0].vmholder}($sp)')
        self.emit(f'    subu $sp, $sp, {l + 4}')
        self.emit(f'    sw $ra, {l}($sp)')
        for arg in self.args:
            if type(arg) != int:
                self.emit(f'    ld $t0, {l + 4 + arg.vmholder}($sp)')
                self.emit(f'    sd $t0, {l - p}($sp)')
            elif isinstance(arg, bool):
                v = 1 if arg else 0
                self.emit(f'    li $t0, {v}')
                self.emit(f'    la $t1, {self.types["Bool"].pos}($gp)')
                self.emit(f'    sd $t0, {l - p + 4}($sp)')
            else:
                self.emit(f'    li $t0, {arg}')
                self.emit(f'    la $t1, {self.types["Int"].pos}($gp)')
                self.emit(f'    sd $t0, {l - p + 4}($sp)')
            p += 8
        self.emit(f'    jal {node.type_name}_{node.func_name}')
        self.emit(f'    lw $ra, {l}($sp)')
        self.emit(f'    addu $sp, $sp, {l + 4}')
        self.emit(f'    sd $v0, {node.dest_address.vmholder}($sp)')
        self.args.clear()

    @visitor.when(cil.CILDinamicCallNode)
    def visit(self, node:cil.CILDinamicCallNode):
        dest = self.get_value(node.dest_address)
        l = len(self.args) * 8
        p = 8
        self.emit(f'    lw $t2, {self.args[0].vmholder}($sp)')
        self.emit(f'    subu $sp, $sp, {l + 4}')
        self.emit(f'    sw $ra, {l}($sp)')
        for arg in self.args:
            if type(arg) != int:
                self.emit(f'    ld $t0, {l + 4 + arg.vmholder}($sp)')
                self.emit(f'    sd $t0, {l - p}($sp)')
            else:
                self.emit(f'    li $t1, {arg}')
                self.emit(f'    la $t0, {self.types["Int"].pos}($gp)')
                self.emit(f'    sd $t0, {l - p}($sp)')
            p += 8
        self.emit(f'    lw $t0, {self.types[node.type_name].methods[node.func_name].mips_position}($t2)')
        self.emit(f'    jalr $t0')
        self.emit(f'    lw $ra, {l}($sp)')
        self.emit(f'    addu $sp, $sp, {l + 4}')
        self.emit(f'    sd $v0, {dest}($sp)')
        self.args.clear()

    @visitor.when(cil.CILArgNode)
    def visit(self, node:cil.CILArgNode):
        self.args.append(node.arg_name)

    @visitor.when(cil.CILReturnNode)
    def visit(self, node:cil.CILReturnNode):
        if type(node.value) == int:
            self.emit(f'    la $v0, {self.types["Int"].pos}($gp)')
            self.emit(f'    li $v1, {node.value}')
        elif isinstance(node.value, bool):
            v = 1 if node.value else 0
            self.emit(f'    la $v0, {self.types["Bool"].pos}($gp)')
            self.emit(f'    li $v1, {v}')
        else:
            self.emit(f'    ld $v0, {node.value.vmholder}($sp)')

    @visitor.when(cil.CILLoadNode)
    def visit(self, node:cil.CILLoadNode):
        self.emit(f'    la $t0, {node.msg.vname}')
        self.emit(f'    la $t1, {self.types["String"].pos}($gp)')
        self.emit(f'    sw $t1, {node.dest.vmholder}($sp)')
        self.emit(f'    sw $t0, {node.dest.vmholder + 4}($sp)')

    @visitor.when(cil.CILLengthNode)
    def visit(self, node:cil.CILLengthNode):
        self.emit(f'    lw $a0, {node.src.vmholder + 4}($sp)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal length')
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    la $t0, {self.types["Int"].pos}($gp)')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')
        self.emit(f'    sw $v0, {node.dest.vmholder + 4}($sp)')

    @visitor.when(cil.CILConcatNode)
    def visit(self, node:cil.CILConcatNode):
        self.emit(f'    lw $a0, {node.str.vmholder + 4}($sp)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal length')
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    la $t0, ($v0)')
        self.emit(f'    lw $a0, {node.src.vmholder + 4}($sp)')
        self.emit(f'    subu $sp, $sp, 8')
        self.emit(f'    sw $ra, 4($sp)')
        self.emit(f'    sw $t0, ($sp)')
        self.emit(f'    jal length')
        self.emit(f'    lw $t0, ($sp)')
        self.emit(f'    lw $ra, 4($sp)')
        self.emit(f'    addu $sp, $sp, 8')
        self.emit(f'    la $a0, ($v0)')
        self.emit(f'    addu $a0, $a0, $t0')
        self.emit(f'    addu $a0, $a0, 1')
        self.emit(f'    li $v0, 9')
        self.emit(f'    syscall')
        self.emit(f'    la $a2, ($v0)')
        self.emit(f'    lw $a0, {node.str.vmholder + 4}($sp)')
        #self.emit(f'    lb $a0, ($a0)')
        self.emit(f'    lw $a1, {node.src.vmholder + 4}($sp)')
        #self.emit(f'    lb $a1, ($a1)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal concat')
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')

        self.emit(f'    la $t0, {self.types["String"].pos}($gp)')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')
        self.emit(f'    sw  $v0, {node.dest.vmholder + 4}($sp)')

    # @visitor.when(cil.CILPrefixNode)
    # def visit(self, node:cil.CILPrefixNode):
    #     pass

    @visitor.when(cil.CILSubstringNode)
    def visit(self, node:cil.CILSubstringNode):
        self.emit(f'    lw $a0, {node.src.vmholder + 4}($sp)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal length')
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    lw $t0, {node.i.vmholder + 4}($sp)')
        self.emit(f'    blt $t0, 0, error')
        self.emit(f'    lw $t1, {node.l.vmholder + 4}($sp)')
        self.emit(f'    blt $t1, 0, error')
        self.emit(f'    add $t0, $t0, $t1')
        self.emit(f'    blt $v0, $t0, error')
        self.emit(f'    li $v0, 9')
        self.emit(f'    lw $a0, {node.l.vmholder + 4}($sp)')
        self.emit(f'    add $a0, $a0, 1')
        self.emit(f'    syscall')
        self.emit(f'    la $a3, ($v0)')
        self.emit(f'    lw $a0, {node.src.vmholder + 4}($sp)')
        self.emit(f'    lw $a1, {node.i.vmholder + 4}($sp)')
        self.emit(f'    lw $a2, {node.l.vmholder + 4}($sp)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal substring')
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    la $t1, {self.types["String"].pos}($gp)')
        self.emit(f'    sw $t1, {node.dest.vmholder}($sp)')
        self.emit(f'    sw  $v0, {node.dest.vmholder + 4}($sp)')

    @visitor.when(cil.CILToStrNode)
    def visit(self, node:cil.CILToStrNode):
        dest = node.dest.name
        ivalue = self.get_value(node.ivalue)
        self.emit(f'    {dest} = STR {ivalue}')

    @visitor.when(cil.CILReadStringNode)
    def visit(self, node:cil.CILReadStringNode):
        dest = node.dest.name
        self.emit(f'    lw $a0, {self.in_buffer}($gp)')
        self.emit(f'    li $a1, 128')
        self.emit(f'    li $v0, 8')
        self.emit(f'    syscall')
        self.emit(f'    subu $sp, $sp, 8')
        self.emit(f'    sw $ra, 4($sp)')
        self.emit(f'    sw $a0, ($sp)')
        self.emit(f'    jal length')
        self.emit(f'    lw $a0, ($sp)')
        self.emit(f'    lw $ra, 4($sp)')
        self.emit(f'    addu $sp, $sp, 8')

        self.emit(f'    la $t0, ($a0)')
        self.emit(f'    la $t1, ($v0)')

        self.emit(f'    la $a0, ($v0)')
        self.emit(f'    li $v0, 9')
        self.emit(f'    syscall')
        self.emit(f'    la $a0, ($t0)')
        self.emit(f'    li $a1, 0')
        self.emit(f'    la $a2, ($t1)')
        self.emit(f'    la $a3, ($v0)')

        self.emit(f'    subu $sp, $sp, 8')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal substring')
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 8')

        self.emit(f'    la $t0, {self.types["String"].pos}($gp)')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')
        self.emit(f'    sw $v0, {node.dest.vmholder + 4}($sp)')

    @visitor.when(cil.CILReadIntNode)
    def visit(self, node: cil.CILReadIntNode):
        self.emit('    li $v0, 5')
        self.emit('    syscall')
        self.emit(f'    sw $v0, {node.dest.vmholder + 4}($sp)')
        self.emit(f'    la $t0, {self.types["Int"].pos}($gp)')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')

    @visitor.when(cil.CILPrintStringNode)
    def visit(self, node:cil.CILPrintStringNode):
        self.emit(f'    li $v0, 4')
        self.emit(f'    lw $a0, {node.src.vmholder + 4}($sp)')
        self.emit('syscall')
        self.emit(f'    ld $v0, {node.str_addr.vmholder}($sp)')

    @visitor.when(cil.CILPrintIntNode)
    def visit(self, node: cil.CILPrintIntNode):
        self.emit(f'    li $v0, 1')
        if isinstance(node.src, int):
            self.emit(f'    li $a0, {node.src}')
        else:
            self.emit(f'    lw $a0, {node.src.vmholder + 4}($sp)')
        self.emit('syscall')
        self.emit(f'    ld $v0, {node.str_addr.vmholder}($sp)')

    @visitor.when(cil.CILEqualNode)
    def visit(self, node: cil.CILEqualNode):
        if type(node.left) == int:
            self.emit(f'    li $t1, {node.left}')
        elif isinstance(node.left, bool):
            v = 1 if node.left else 0
            self.emit(f'    li $t1, {v}')
        else:
            self.emit(f'    lw $t1, {node.left.vmholder + 4}($sp)')

        if type(node.right) == int:
            self.emit(f'    li $t2, {node.right}')
        elif isinstance(node.right, bool):
            v = 1 if node.right else 0
            self.emit(f'    li $t1, {v}')
        else:
            self.emit(f'    lw $t2, {node.right.vmholder + 4}($sp)')

        self.emit(f'    seq $t0, $t1, $t2')
        self.emit(f'    la $t1, {self.types["Bool"].pos}($gp)')
        self.emit(f'    sw $t1, {node.dest.vmholder}($sp)')
        self.emit(f'    sw $t0, {node.dest.vmholder + 4}($sp)')

    @visitor.when(cil.CILLessThanNode)
    def visit(self, node: cil.CILLessThanNode):
        if isinstance(node.left, int):
            self.emit(f'    li $t1, {node.left}')
        else:
            self.emit(f'    lw $t1, {node.left.vmholder + 4}($sp)')

        if isinstance(node.right, int):
            self.emit(f'    li $t2, {node.right}')
        else:
            self.emit(f'    lw $t2, {node.right.vmholder + 4}($sp)')

        self.emit(f'    slt $t0, $t1, $t2')
        self.emit(f'    la $t1, {self.types["Bool"].pos}($gp)')
        self.emit(f'    sw $t1, {node.dest.vmholder}($sp)')
        self.emit(f'    sw $t0, {node.dest.vmholder + 4}($sp)')

    @visitor.when(cil.CILLessEqualNode)
    def visit(self, node: cil.CILLessEqualNode):
        if isinstance(node.left, int):
            self.emit(f'    li $t1, {node.left}')
        else:
            self.emit(f'    lw $t1, {node.left.vmholder + 4}($sp)')

        if isinstance(node.right, int):
            self.emit(f'    li $t2, {node.right}')
        else:
            self.emit(f'    lw $t2, {node.right.vmholder + 4}($sp)')
        self.emit(f'    sle $t0, $t1, $t2')
        self.emit(f'    la $t1, {self.types["Bool"].pos}($gp)')
        self.emit(f'    sw $t1, {node.dest.vmholder}($sp)')
        self.emit(f'    sw $t0, {node.dest.vmholder + 4}($sp)')

    @visitor.when(cil.CILCheckHierarchy)
    def visit(self, node: cil.CILCheckHierarchy):
        self.emit(f'    la $a0, {self.types[node.a].pos}($gp)')
        if type(node.b) == int:
            self.emit(f'    la $a1, {self.types["Int"].pos}($gp)')
        elif type(node.b) == bool:
            self.emit(f'    la $a1, {self.types["Bool"].pos}($gp)')
        else:
            self.emit(f'    lw $a1, {node.b.vmholder}($sp)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal check_hierarchy')
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    la $t1, {self.types["Bool"].pos}($gp)')
        self.emit(f'    sw $t1, {node.dest.vmholder}($sp)')
        self.emit(f'    sw $v0, {node.dest.vmholder + 4}($sp)')

    @visitor.when(cil.CILErrorNode)
    def visit(self, node: cil.CILErrorNode):
        self.emit(f'    j error')

    @visitor.when(cil.CILNotNode)
    def visit(self, node: cil.CILNotNode):
        var = self.get_value(node.expr)
        if isinstance(node.expr, bool):
            v = 1 if node.expr else 0
            self.emit(f'    li $t0, {v}')
        else:
            self.emit(f'    li $t0, {var}')
        self.emit(f'    not $t0, $t0')
        self.emit(f'    la $t1, {self.types["Bool"].pos}($gp)')
        self.emit(f'    sw $t1, {node.dst.vmholder}($sp)')
        self.emit(f'    sw $t0, {node.dst.vmholder + 4}($sp)')

    @visitor.when(cil.CILEndProgram)
    def visit(self, node):
        self.emit(f"    li $v0, 10")
        self.emit("    xor $a0, $a0, $a0")
        self.emit("    syscall")

    @visitor.when(cil.CILComplementNode)
    def visit(self, node: cil.CILComplementNode):
        if isinstance(node.expr, int):
            self.emit(f'    li $t0, {node.expr}')
        else:
            self.emit(f'    lw $t0, {node.expr.vmholder + 4}($sp)')
            # TODO Ver bien cual es el resultado esperado del complemento
        self.emit(f'    not $t0, $t0')
        #self.emit(f'    li $t1, 0x7FFFFFFF')
        #self.emit(f'    and $t0, $t0, $t1'
        self.emit(f'    la $t1, {self.types["Int"].pos}($gp)')
        self.emit(f'    sw $t1, {node.dst.vmholder}($sp)')
        self.emit(f'    sw $t0, {node.dst.vmholder + 4}($sp)')

    @visitor.when(cil.CILAbortNode)
    def visit(self, node: cil.CILAbortNode):
        self.emit(f"    li $v0, 10")
        self.emit("    xor $a0, $a0, $a0")
        self.emit("    syscall")

    @visitor.when(cil.CILBoxVariable)
    def visit(self, node: cil.CILBoxVariable):
        self.emit(f'    li $v0, 9')
        self.emit(f'    li $a0, 8')
        self.emit(f'    syscall')
        self.emit(f'    la $t0, {self.types["Object"].pos}($gp)')
        self.emit(f'    sw $v0, {node.dest.vmholder + 4}($sp)')
        self.emit(f'    sw $t0, {node.dest.vmholder}($sp)')

        if type(node.variable) == int:
            self.emit(f'    la $t0, {self.types["Int"].pos}($gp)')
            self.emit(f'    li $t1, {node.variable}')
        elif isinstance(node.variable, bool):
            v = 1 if node.variable else 0
            self.emit(f'    la $t0, {self.types["Bool"].pos}($gp)')
            self.emit(f'    li $t1, {v}')
        else:
            self.emit(f'    ld $t0, {node.variable.vmholder}($sp)')

        self.emit(f'    sd $t0, ($v0)')

    @visitor.when(cil.CILUnboxVariable)
    def visit(self, node:cil.CILUnboxVariable):
        self.emit(f'    la $a0, {node.variable.vmholder}($sp)')
        self.emit(f'    subu $sp, $sp, 4')
        self.emit(f'    sw $ra, ($sp)')
        self.emit(f'    jal unbox_variable')
        self.emit(f'    lw $ra, ($sp)')
        self.emit(f'    addu $sp, $sp, 4')
        self.emit(f'    sd $v0, {node.dest.vmholder}($sp)')