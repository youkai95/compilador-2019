import ast_hierarchy as ast
import cil_hierarchy as cil
import visitor
from scope import VariableInfo
from typetree import ClassType


class COOLToCILVisitor:
    def __init__(self):
        self.types = []
        self.dotdata = []
        self.dotcode = []
        self.current_function_name = ""
        self.localvars = []
        self.instructions = []
        self.internal_count = 0
        self.current_type = None
        self.label_count = 0

    # ======================================================================
    # =[ UTILS ]============================================================
    # ======================================================================

    def gen_label(self):
        self.label_count+=1
        return "label_%d"%(self.label_count)


    def build_internal_vname(self, vname):
        vname = f'{self.internal_count}_{self.current_function_name}_{vname}'
        self.internal_count +=1
        return vname

    def define_internal_local(self):
        vinfo = VariableInfo('internal')
        return self.register_local(vinfo)

    def register_local(self, vinfo):
        vinfo.name = self.build_internal_vname(vinfo.name)
        vinfo.vmholder = len(self.localvars)
        local_node = cil.CILLocalNode(vinfo)
        self.localvars.append(local_node)
        return vinfo

    def register_instruction(self, instruction_type, *args):
        instruction = instruction_type(*args)
        self.instructions.append(instruction)
        return instruction

    def register_data(self, value):
        vname = f'data_{len(self.dotdata)}'
        data_node = cil.CILDataNode(vname, value)
        self.dotdata.append(data_node)
        return data_node

    def build_type(self, type_info: ClassType, attrib, methods):
        if not type_info:
            return
        self.build_type(type_info.parent, attrib, methods)
        if type_info.methods:
            for name in type_info.methods:
                type_info.methods[name].cil_name = f"{type_info.name}_{name}"
                methods.append(type_info.methods[name].cil_name)
        if type_info.attributes:
            for name in type_info.attributes:
                attrib.append(name)

    def build_arg_name(self, fname, pname):
        return f"{fname}_{pname}"
    # ======================================================================


    # ======================================================================
    # =[ VISIT ]============================================================
    # ======================================================================

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node:ast.ProgramNode):
        for expr in node.expr:
            self.visit(expr)
        return cil.CILProgramNode(self.types, self.dotdata, self.dotcode)

    @visitor.when(ast.PlusNode)
    def visit(self, node:ast.PlusNode):
        left_ret = self.visit(node.left)
        right_ret = self.visit(node.right)
        r = cil.CILPlusNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        return r.dest

    @visitor.when(ast.MinusNode)
    def visit(self, node:ast.MinusNode):
        left_ret = self.visit(node.left)
        right_ret = self.visit(node.right)
        r = cil.CILMinusNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        return r.dest

    @visitor.when(ast.StarNode)
    def visit(self, node:ast.StarNode):
        left_ret = self.visit(node.left)
        right_ret = self.visit(node.right)
        r = cil.CILStarNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        return r.dest

    @visitor.when(ast.DivNode)
    def visit(self, node:ast.DivNode):
        left_ret = self.visit(node.left)
        right_ret = self.visit(node.right)
        r = cil.CILDivNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        return r.dest

    @visitor.when(ast.NegationNode)
    def visit(self, node:ast.NegationNode):
        ret_val = self.visit(node.expr)
        if type(ret_val) == int:
            return -ret_val
        r = self.define_internal_local()
        self.instructions.append(cil.CILMinusNode(r, 0, ret_val))
        return r

    @visitor.when(ast.LetInNode)
    def visit(self, node:ast.LetInNode):
        for instruction in node.declaration_list:
            self.visit(instruction)
        ret_val = self.visit(node.expr)
        return ret_val

    @visitor.when(ast.DeclarationNode)
    def visit(self, node:ast.DeclarationNode):
        if node.expr:
            ret_val = self.visit(node.expr)
            node.variable_info = ret_val
            return ret_val
        var = self.define_internal_local()
        node.variable_info = var
        return var

    @visitor.when(ast.BlockNode)
    def visit(self, node:ast.BlockNode):
        result = 0
        for instruction in node.expr_list:
            result = self.visit(instruction)
        return result

    @visitor.when(ast.AssignNode)
    def visit(self, node:ast.AssignNode):
        if not node.variable_info.vmholder:
            if not node.variable_info.name in self.current_type.attributes:
                var = self.define_internal_local()
                node.variable_info.name = var.name
                node.variable_info.vmholder = var.vmholder
                self.instructions.append(cil.CILAssignNode(node.variable_info, self.visit(node.expr)))
            else:
                self.instructions.append(cil.CILSetAttribNode(self.current_type.name, node.idx_token, self.visit(node.expr)))

        return node.variable_info

    @visitor.when(ast.IntegerNode)
    def visit(self, node:ast.IntegerNode):
        return int(node.integer_token)

    @visitor.when(ast.StringNode)
    def visit(self, node:ast.StringNode):
        data = self.register_data(node.string)
        return data

    @visitor.when(ast.VariableNode)
    def visit(self, node:ast.VariableNode):
        if node.variable_info.vmholder is not None:
            return node.variable_info
        else:
            result = self.define_internal_local()
            node.variable_info.name = result.name
            node.variable_info.vmholder = result.vmholder
            self.instructions.append(cil.CILGetAttribNode(result, self.current_type.name, node.idx_token))
            return result

    @visitor.when(ast.PrintIntegerNode)
    def visit(self, node:ast.PrintIntegerNode):
        ret_val = self.visit(node.expr)
        strc = cil.CILToStrNode(self.define_internal_local(), ret_val)
        self.instructions.append(strc)
        self.instructions.append(cil.CILPrintNode(strc.dest))
        return strc.dest

    @visitor.when(ast.PrintStringNode)
    def visit(self, node:ast.PrintStringNode):
        self.instructions.append(cil.CILPrintNode(self.register_data(node.string_token)))
        return 0

    @visitor.when(ast.ScanNode)
    def visit(self, node:ast.ScanNode):
        n = cil.CILReadNode(self.define_internal_local())
        self.instructions.append(n)
        return n.dest

    #TODO
    @visitor.when(ast.NewNode)
    def visit(self, node: ast.NewNode):
        cil.CILAllocateNode()
        pass

    # TODO
    @visitor.when(ast.ClassNode)
    def visit(self, node: ast.ClassNode):
        vt: ClassType = node.vtable
        methods = []
        attrib = []
        self.current_type = vt
        self.build_type(vt, attrib, methods)
        for expr in node.cexpresion:
            self.visit(expr)
        self.types.append(cil.CILTypeNode(node.idx_token, attrib, methods))

    # TODO
    @visitor.when(ast.IfNode)
    def visit(self, node: ast.IfNode):
        v = self.visit(node.conditional_token)
        v1 = self.define_internal_local()
        doIf = cil.CILLabelNode(self.gen_label())
        end = cil.CILLabelNode(self.gen_label())
        self.instructions.append(cil.CILGotoIfNode(v, doIf))
        self.instructions.append(cil.CILAssignNode(v1, self.visit(node.else_expr)))
        self.instructions.append(cil.CILGotoNode(end))
        self.instructions.append(doIf)
        self.instructions.append(cil.CILAssignNode(v1, self.visit(node.expr)))
        self.instructions.append(end)
        return v1

    # TODO
    @visitor.when(ast.PropertyNode)
    def visit(self, node: ast.PropertyNode):
        pass

    # TODO
    @visitor.when(ast.MethodNode)
    def visit(self, node: ast.MethodNode):
        self.instructions = []
        self.localvars = []
        args = []
        for param in node.params:
            name = self.build_arg_name(node.name, param.idx_token)
            args.append(cil.CILArgNode(name))
            param.variable_info.name = name

        self.current_function_name = node.vinfo.cil_name
        self.instructions.append(cil.CILReturnNode(self.visit(node.body)))
        self.dotcode.append(cil.CILFunctionNode(self.current_function_name, args, self.localvars, self.instructions))

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode):
        result = cil.CILEqualNode(self.define_internal_local(), self.visit(node.expr), 0)
        self.instructions.append(result)
        return result.dest

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode):
        v = self.visit(node.conditional_token)
        start = cil.CILLabelNode(self.gen_label())
        dowhile = cil.CILLabelNode(self.gen_label())
        end = cil.CILLabelNode(self.gen_label())
        self.instructions.append(start)
        self.instructions.append(cil.CILGotoIfNode(v, dowhile))
        self.instructions.append(cil.CILGotoNode(end))
        self.instructions.append(dowhile)
        self.visit(node.expr)
        self.instructions.append(cil.CILGotoNode(start))
        self.instructions.append(end)
        return 0

    # TODO
    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode):
        pass

    @visitor.when(ast.CaseItemNode)
    def visit(self, node: ast.CaseItemNode):
        self.visit(node.variable)
        return self.visit(node.expr)

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode):
        return bool(node.value)

    # TODO
    @visitor.when(ast.DispatchNode)
    def visit(self, node: ast.DispatchNode):
        pass

    # TODO
    @visitor.when(ast.DispatchParentInstanceNode)
    def visit(self, node: ast.DispatchParentInstanceNode):
        pass

    # TODO
    @visitor.when(ast.DispatchInstanceNode)
    def visit(self, node: ast.DispatchInstanceNode):
        pass

    @visitor.when(ast.LessThanNode)
    def visit(self, node: ast.LessThanNode):
        left_ret = self.visit(node.left)
        rigth_ret = self.visit(node.right)
        ret_type = cil.CILLessThanNode(self.define_internal_local(), left_ret, rigth_ret)
        self.instructions.append(ret_type)
        return ret_type.dest

    @visitor.when(ast.LessEqualNode)
    def visit(self, node: ast.LessEqualNode):
        left_ret = self.visit(node.left)
        rigth_ret = self.visit(node.right)
        ret_type = cil.CILLessEqualNode(self.define_internal_local(), left_ret, rigth_ret)
        self.instructions.append(ret_type)
        return ret_type.dest

    @visitor.when(ast.EqualNode)
    def visit(self, node: ast.EqualNode):
        left_ret = self.visit(node.left)
        rigth_ret = self.visit(node.right)
        ret_type = cil.CILEqualNode(self.define_internal_local(), left_ret, rigth_ret)
        self.instructions.append(ret_type)
        return ret_type.dest

    # ======================================================================