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
        return cil.CILPlusNode(self.define_internal_local(), self.visit(node.left), self.visit(node.right))

    @visitor.when(ast.MinusNode)
    def visit(self, node:ast.MinusNode):
        return cil.CILMinusNode(self.define_internal_local(), self.visit(node.left), self.visit(node.right))\

    @visitor.when(ast.StarNode)
    def visit(self, node:ast.StarNode):
        return cil.CILStarNode(self.define_internal_local(), self.visit(node.left), self.visit(node.right))

    @visitor.when(ast.DivNode)
    def visit(self, node:ast.DivNode):
        return cil.CILDivNode(self.define_internal_local(), self.visit(node.left), self.visit(node.right))

    @visitor.when(ast.NegationNode)
    def visit(self, node:ast.NegationNode):
        #TODO: no exite nada en CIL
        pass

    @visitor.when(ast.LetInNode)
    def visit(self, node:ast.LetInNode):
        # TODO: to implement!!!
        pass

    @visitor.when(ast.DeclarationNode)
    def visit(self, node:ast.DeclarationNode):
        # TODO: to implement!!!
        pass

    @visitor.when(ast.BlockNode)
    def visit(self, node:ast.BlockNode):
        # TODO: to implement!!!
        pass

    @visitor.when(ast.AssignNode)
    def visit(self, node:ast.AssignNode):
        self.define_internal_local()
        
        pass

    @visitor.when(ast.IntegerNode)
    def visit(self, node:ast.IntegerNode):
        return int(node.integer_token.text_token)

    @visitor.when(ast.VariableNode)
    def visit(self, node:ast.VariableNode):
        # TODO: to implement!!!
        pass

    @visitor.when(ast.PrintIntegerNode)
    def visit(self, node:ast.PrintIntegerNode):
        # TODO: to implement!!!
        pass

    @visitor.when(ast.PrintStringNode)
    def visit(self, node:ast.PrintStringNode):
        return cil.CILPrintNode(self.register_data(node.string_token))

    @visitor.when(ast.ScanNode)
    def visit(self, node:ast.ScanNode):
        return cil.CILReadNode(self.define_internal_local())
        # TODO: to implement!!!
        pass

    # ======================================================================