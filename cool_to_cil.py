import ast_hierarchy as ast
import cil_hierarchy as cil
import visitor
from scope import VariableInfo
from typetree import ClassType, TypeTree


class COOLToCILVisitor:
    def __init__(self):
        self.types = []
        self.dotdata = []
        self.dotcode = []
        self.current_function_name = ""
        self.localvars = []
        self.instructions = []
        self.internal_count = 0
        self.selftype = None
        self.current_typename = None
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

    def define_selftype(self):
        vname = "self"
        vinfo = VariableInfo(vname)
        self.selftype = vinfo
        self.instructions.append(cil.CILArgNode(vinfo.name))
        return vinfo


    def build_type(self, type_info: ClassType, attrib, methods):
        if not type_info:
            return
        self.build_type(type_info.parent, attrib, methods)
        if type_info.methods:
            for name in type_info.methods:
                type_info.methods[name].cil_name = f"{type_info.name}_{name}"
                methods[name] = type_info.methods[name].cil_name
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
    def visit(self, node:ast.ProgramNode, type_tree):
        for expr in node.expr:
            self.visit(expr, type_tree)
        return cil.CILProgramNode(self.types, self.dotdata, self.dotcode)

    @visitor.when(ast.PlusNode)
    def visit(self, node:ast.PlusNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        right_ret = self.visit(node.right, type_tree)
        r = cil.CILPlusNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        return r.dest

    @visitor.when(ast.MinusNode)
    def visit(self, node:ast.MinusNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        right_ret = self.visit(node.right, type_tree)
        r = cil.CILMinusNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        return r.dest

    @visitor.when(ast.StarNode)
    def visit(self, node:ast.StarNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        right_ret = self.visit(node.right, type_tree)
        r = cil.CILStarNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        return r.dest

    @visitor.when(ast.DivNode)
    def visit(self, node:ast.DivNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        right_ret = self.visit(node.right, type_tree)
        r = cil.CILDivNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        return r.dest

    @visitor.when(ast.NegationNode)
    def visit(self, node:ast.NegationNode, type_tree):
        ret_val = self.visit(node.expr, type_tree)
        if type(ret_val) == int:
            return -ret_val
        r = self.define_internal_local()
        self.instructions.append(cil.CILMinusNode(r, 0, ret_val))
        return r

    @visitor.when(ast.LetInNode)
    def visit(self, node:ast.LetInNode, type_tree):
        for instruction in node.declaration_list:
            self.visit(instruction, type_tree)
        ret_val = self.visit(node.expr, type_tree)
        return ret_val

    @visitor.when(ast.DeclarationNode)
    def visit(self, node:ast.DeclarationNode, type_tree):
        if node.expr:
            ret_val = self.visit(node.expr, type_tree)
            node.variable_info = ret_val
            return ret_val
        var = self.define_internal_local()
        node.variable_info = var
        return var

    @visitor.when(ast.BlockNode)
    def visit(self, node:ast.BlockNode, type_tree):
        result = 0
        for instruction in node.expr_list:
            result = self.visit(instruction, type_tree)
        return result

    @visitor.when(ast.AssignNode)
    def visit(self, node:ast.AssignNode, type_tree):
        if not node.variable_info.vmholder:
            if not node.variable_info.name in self.current_typename.attributes:
                var = self.define_internal_local()
                node.variable_info.name = var.name
                node.variable_info.vmholder = var.vmholder
                self.instructions.append(cil.CILAssignNode(node.variable_info, self.visit(node.expr, type_tree)))
            else:
                self.instructions.append(cil.CILSetAttribNode(self.current_typename.name, node.idx_token, self.visit(node.expr, type_tree)))

        return node.variable_info

    @visitor.when(ast.IntegerNode)
    def visit(self, node:ast.IntegerNode, type_tree):
        return int(node.integer_token)

    @visitor.when(ast.StringNode)
    def visit(self, node:ast.StringNode, type_tree):
        data = self.register_data(node.string)
        var = self.define_internal_local()
        self.instructions.append(cil.CILLoadNode(var, data))
        return var

    @visitor.when(ast.VariableNode)
    def visit(self, node:ast.VariableNode, type_tree):
        if node.variable_info.vmholder is not None:
            return node.variable_info
        else:
            result = self.define_internal_local()
            node.variable_info.name = result.name
            node.variable_info.vmholder = result.vmholder
            self.instructions.append(cil.CILGetAttribNode(result, self.current_typename.name, node.idx_token))
            return result

    @visitor.when(ast.PrintIntegerNode)
    def visit(self, node:ast.PrintIntegerNode, type_tree):
        ret_val = self.visit(node.expr, type_tree)
        strc = cil.CILToStrNode(self.define_internal_local(), ret_val)
        self.instructions.append(strc)
        self.instructions.append(cil.CILPrintNode(strc.dest))
        return strc.dest

    @visitor.when(ast.PrintStringNode)
    def visit(self, node:ast.PrintStringNode, type_tree):
        data = self.register_data(node.string_token)
        var = self.define_internal_local()
        self.instructions.append(cil.CILLoadNode(var, data))
        self.instructions.append(cil.CILPrintNode(var))
        return 0

    @visitor.when(ast.ScanNode)
    def visit(self, node:ast.ScanNode, type_tree):
        n = cil.CILReadNode(self.define_internal_local())
        self.instructions.append(n)
        return n.dest

    @visitor.when(ast.NewNode)
    def visit(self, node: ast.NewNode, type_tree: TypeTree):
        var = self.define_internal_local()
        self.instructions.append(cil.CILAllocateNode(node.type_token, var))
        # TODO Carry with type tree to get type parameters
        t = type_tree.get_type(node.type_token)
        for name, attr in t.attributes.items():
            self.instructions.append(cil.CILSetAttribNode(var, name, self.visit(attr, type_tree)))
        return var

    @visitor.when(ast.ClassNode)
    def visit(self, node: ast.ClassNode, type_tree):
        vt: ClassType = node.vtable
        methods = {}
        attrib = []
        self.current_typename = vt
        self.build_type(vt, attrib, methods)
        for expr in node.cexpresion:
            self.visit(expr, type_tree)
        self.types.append(cil.CILTypeNode(node.idx_token, attrib, methods))

    @visitor.when(ast.IfNode)
    def visit(self, node: ast.IfNode, type_tree):
        v = self.visit(node.conditional_token, type_tree)
        v1 = self.define_internal_local()
        doIf = cil.CILLabelNode(self.gen_label())
        end = cil.CILLabelNode(self.gen_label())
        self.instructions.append(cil.CILGotoIfNode(v, doIf))
        self.instructions.append(cil.CILAssignNode(v1, self.visit(node.else_expr, type_tree)))
        self.instructions.append(cil.CILGotoNode(end))
        self.instructions.append(doIf)
        self.instructions.append(cil.CILAssignNode(v1, self.visit(node.expr, type_tree)))
        self.instructions.append(end)
        return v1


    @visitor.when(ast.PropertyNode)
    def visit(self, node: ast.PropertyNode, type_tree):
        return self.visit(node.decl, type_tree)


    @visitor.when(ast.MethodNode)
    def visit(self, node: ast.MethodNode, type_tree):
        self.instructions = []
        self.localvars = []
        args = []
        self.define_selftype()
        for param in node.params:
            name = self.build_arg_name(node.name, param.idx_token)
            args.append(cil.CILArgNode(name))
            param.variable_info.name = name

        self.current_function_name = node.vinfo.cil_name
        self.instructions.append(cil.CILReturnNode(self.visit(node.body, type_tree)))
        self.dotcode.append(cil.CILFunctionNode(self.current_function_name, args, self.localvars, self.instructions))

    @visitor.when(ast.IsVoidNode)
    def visit(self, node: ast.IsVoidNode, type_tree):
        # t = self.define_internal_local()
        # expr = self.visit(node.expr)
        # endC = cil.CILLabelNode(self.gen_label())
        # end = cil.CILLabelNode(self.gen_label())
        # v = cil.CILEqualNode(expr.type.name, "Bool")
        # self.instructions.append(v)
        # self.instructions.append(cil.CILGotoIfNode(v, endC))
        # v = cil.CILEqualNode(expr.type.name, "Int")
        # self.instructions.append(v)
        # self.instructions.append(cil.CILGotoIfNode(v, endC))
        # v = cil.CILEqualNode(expr.type.name, "String")
        # self.instructions.append(v)
        # self.instructions.append(cil.CILGotoIfNode(v, endC))
        # result = cil.CILEqualNode(self.define_internal_local(), expr, 0)
        # self.instructions.append(result)
        # r = cil.CILAssignNode(t, result.dest)
        # self.instructions.append(cil.CILGotoNode(end))
        # self.instructions.append(endC)
        # r = cil.CILAssignNode(t, 0)
        # self.instructions.append(end)
        # return r.dest

        expr = self.visit(node.expr, type_tree)
        if expr.type.name == "Bool" or expr.type.name == "Int" or expr.type.name == "String":
            return 0
        result = cil.CILEqualNode(self.define_internal_local(), expr, 0)
        self.instructions.append(result)
        return result.dest

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, type_tree):
        v = self.visit(node.conditional_token, type_tree)
        start = cil.CILLabelNode(self.gen_label())
        dowhile = cil.CILLabelNode(self.gen_label())
        end = cil.CILLabelNode(self.gen_label())
        self.instructions.append(start)
        self.instructions.append(cil.CILGotoIfNode(v, dowhile))
        self.instructions.append(cil.CILGotoNode(end))
        self.instructions.append(dowhile)
        self.visit(node.expr, type_tree)
        self.instructions.append(cil.CILGotoNode(start))
        self.instructions.append(end)
        return 0

    @visitor.when(ast.CaseNode)
    def visit(self, node: ast.CaseNode, type_tree):
        expr = self.visit(node.expr, type_tree)
        labels = []
        end = cil.CILLabelNode(self.gen_label())
        ends = []
        checkr = self.define_internal_local()

        for i in range(len(node.expresion_list)):
            temp = cil.CILLabelNode(self.gen_label())
            labels.append(temp)
            check = cil.CILCHeckHierarchy(checkr, node.expresion_list[i].type_token, expr.type)
            self.instructions.append(check)
            self.instructions.append(cil.CILGotoIfNode(check, temp))
        self.instructions.append(cil.CILErrorNode)
        self.instructions.append(cil.CILGotoNode(end))

        for i in range(0, len(node.expresion_list)):
            self.instructions.append(labels[i])
            for j in range(i + 1, len(node.expresion_list)):
                e1 = node.expresion_list[j].type_token
                e2 = node.expresion_list[i].type_token
                check = cil.CILCHeckHierarchy(checkr, e1, e2)
                self.instructions.append(check)
                self.instructions.append(cil.CILGotoIfNode(check, labels[j]))
            t = cil.CILLabelNode(self.gen_label())
            ends.append(t)
            self.instructions.append(cil.CILGotoNode(t))

        r = self.define_internal_local()
        for i in ends:
            self.instructions.append(i)
            e = self.visit(node.expresion_list[i], type_tree)
            self.instructions.append(cil.CILAssignNode(r, e))
            self.instructions.append(cil.CILGotoNode(end))

        self.instructions.append(end)
        return r

    @visitor.when(ast.CaseItemNode)
    def visit(self, node: ast.CaseItemNode, type_tree):
        self.visit(node.variable, type_tree)
        return self.visit(node.expr, type_tree)

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, type_tree):
        return 1 if node.value == "true" else 0

    @visitor.when(ast.DispatchNode)
    def visit(self, node: ast.DispatchNode, type_tree):
        args = []
        r = self.define_internal_local()
        args.append(cil.CILArgNode(self.selftype.name))
        for param in node.expresion_list:
            args.append(cil.CILArgNode(self.visit(param.name, type_tree)))
        self.instructions += args
        self.instructions.append(cil.CILDinamicCallNode(self.current_typename.name, node.idx_token, r))
        return r

    # TODO
    @visitor.when(ast.DispatchParentInstanceNode)
    def visit(self, node: ast.DispatchParentInstanceNode, type_tree):
        pass

    # TODO
    @visitor.when(ast.DispatchInstanceNode)
    def visit(self, node: ast.DispatchInstanceNode, type_tree):
        pass

    @visitor.when(ast.LessThanNode)
    def visit(self, node: ast.LessThanNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        rigth_ret = self.visit(node.right, type_tree)
        ret_type = cil.CILLessThanNode(self.define_internal_local(), left_ret, rigth_ret)
        self.instructions.append(ret_type)
        return ret_type.dest

    @visitor.when(ast.LessEqualNode)
    def visit(self, node: ast.LessEqualNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        rigth_ret = self.visit(node.right, type_tree)
        ret_type = cil.CILLessEqualNode(self.define_internal_local(), left_ret, rigth_ret)
        self.instructions.append(ret_type)
        return ret_type.dest

    @visitor.when(ast.EqualNode)
    def visit(self, node: ast.EqualNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        rigth_ret = self.visit(node.right, type_tree)
        ret_type = cil.CILEqualNode(self.define_internal_local(), left_ret, rigth_ret)
        self.instructions.append(ret_type)
        return ret_type.dest

    # ======================================================================