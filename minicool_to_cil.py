import ast_hierarchy as ast
import cil_hierarchy as cil
import visitor
from scope import VariableInfo


class MiniCOOLToCILVisitor:
    def __init__(self):
        self.dotdata = []
        self.current_function_name = ""
        self.localvars = []
        self.instructions = []
        self.internal_count = 0


    # ======================================================================
    # =[ UTILS ]============================================================
    # ======================================================================

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
    # ======================================================================


    # ======================================================================
    # =[ VISIT ]============================================================
    # ======================================================================

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node:ast.ProgramNode):
        self.current_function_name = 'main'
        self.visit(node.expr)
        main = cil.CILFunctionNode('main', [], self.localvars, self.instructions)
        return cil.CILProgramNode([], self.dotdata, [main])

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
        r = cil.MinusNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        return r.dest

    @visitor.when(ast.StarNode)
    def visit(self, node:ast.StarNode):
        left_ret = self.visit(node.left)
        right_ret = self.visit(node.right)
        r = cil.StarNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        return r.dest

    @visitor.when(ast.DivNode)
    def visit(self, node:ast.DivNode):
        left_ret = self.visit(node.left)
        right_ret = self.visit(node.right)
        r = cil.DivNode(self.define_internal_local(), left_ret, right_ret)
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
            node.variable_info = self.define_internal_local()
        self.instructions.append(cil.CILAssignNode(node.variable_info, self.visit(node.expr)))
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
        return node.variable_info

    @visitor.when(ast.PrintIntegerNode)
    def visit(self, node:ast.PrintIntegerNode):
        ret_val = self.visit(node.expr)
        strc = cil.CILToStrNode(self.define_internal_local(), ret_val)
        self.instructions.append(strc)
        self.instructions.append(cil.CILPrintNode(strc.dest))
        return strc.dest
        pass

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
        pass

    # TODO
    @visitor.when(ast.ClassNode)
    def visit(self, node: ast.ClassNode):
        pass

    # TODO
    @visitor.when(ast.IfNode)
    def visit(self, node: ast.IfNode):
        pass

    # TODO
    @visitor.when(ast.PropertyNode)
    def visit(self, node: ast.PropertyNode):
        pass

    # TODO
    @visitor.when(ast.MethodNode)
    def visit(self, node: ast.MethodNode):
        pass

    # TODO
    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode):
        pass

    # TODO
    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode):
        pass

    # TODO
    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode):
        pass

    # TODO
    @visitor.when(ast.CaseItemNode)
    def visit(self, node: ast.CaseItemNode):
        pass

    # TODO
    @visitor.when(ast.DispatchNode)
    def visit(self, node: ast.DispatchNode):
        pass

    # TODO
    @visitor.when(ast.IntegerNode)
    def visit(self, node: ast.IntegerNode):
        pass

    # TODO
    @visitor.when(ast.VariableNode)
    def visit(self, node: ast.VariableNode):
        pass

    # TODO
    @visitor.when(ast.StringNode)
    def visit(self, node: ast.StringNode):
        pass

    # TODO
    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode):
        pass

    # TODO
    @visitor.when(ast.DispatchParentInstanceNode)
    def visit(self, node: ast.DispatchParentInstanceNode):
        pass

    # TODO
    @visitor.when(ast.DispatchInstanceNode)
    def visit(self, node: ast.DispatchInstanceNode):
        pass

    # TODO
    @visitor.when(ast.LessThanNode)
    def visit(self, node: ast.LessThanNode):
        pass

    # TODO
    @visitor.when(ast.LessEqualNode)
    def visit(self, node: ast.LessEqualNode):
        pass

    # TODO
    @visitor.when(ast.EqualNode)
    def visit(self, node: ast.EqualNode):
        pass



    # ======================================================================