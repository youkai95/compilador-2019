import ast_hierarchy as ast
import cil_hierarchy as cil
import visitor
from scope import VariableInfo
from typetree import ClassType, TypeTree, MethodType

class CILFunction:
    def __init__(self, name):
        self.cil_name = name
        self.mips_position = 0

class COOLToCILVisitor:
    def __init__(self):
        self.types = []
        self.dotdata = []
        self.dotcode = []
        self.current_function_name = ""
        self.localvars = []
        self.arguments = []
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

    def subscribe_internal_local(self, vinfo):
        return self.register_local(vinfo)

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
        vinfo.type = self.current_typename
        self.selftype = vinfo
        return vinfo

    def build_type(self, type_info: ClassType, attrib, methods):
        if not type_info:
            return
        self.build_type(type_info.parent, attrib, methods)
        if type_info.methods:
            for name in type_info.methods:
                #type_info.methods[name].cil_name = f"{type_info.name}_{name}"
                methods[name] = CILFunction(type_info.methods[name].cil_name)
        if type_info.attributes:
            for name in type_info.attributes:
                attrib.append(name)

    def build_arg_name(self, fname, pname):
        return f"{fname}_{pname}"

    def build_in_methods(self, a, node, m):
        #m.cil_name = name
        instructions = []
        self.localvars = []
        l = self.define_internal_local()

        args = []
        variables = []
        for i in a:
            vinfo = VariableInfo(i)
            variables.append(vinfo)
            args.append(cil.CILParamNode(vinfo))

        l = self.define_internal_local()
        variables.append(l)
        cargs = tuple(variables)
        instructions.append(node(*cargs))
        instructions.append(cil.CILReturnNode(l))
        self.dotcode.append(cil.CILFunctionNode(m.cil_name, args, self.localvars, instructions))

    # ======================================================================


    # ======================================================================
    # =[ VISIT ]============================================================
    # ======================================================================

    @visitor.on('node')
    def visit(self, node):
        pass

    @visitor.when(ast.ProgramNode)
    def visit(self, node:ast.ProgramNode, type_tree:TypeTree):
        n = ast.NewNode("Main")
        n.type = type_tree.get_type("Main")
        m = ast.MethodNode("entry",[], type_tree.get_type("Int"), ast.DispatchInstanceNode(n, "main", []))
        m.vinfo = MethodType("entry", m.type, [])
        m.vinfo.cil_name = "entry"
        self.visit(m, type_tree)
        for expr in node.expr:
            self.visit(expr, type_tree)

        self.build_in_methods(["self", "i", "l"], cil.CILSubstringNode, type_tree.get_type("String").methods["substring"])
        self.build_in_methods(["self"], cil.CILLengthNode, type_tree.get_type("String").methods["length"])
        self.build_in_methods(["self", "str"], cil.CILConcatNode, type_tree.get_type("String").methods["concat"])
        self.build_in_methods(["self"], cil.CILTypeOfNode, type_tree.get_type("Object").methods["type_name"])
        self.build_in_methods([], cil.CILReadStringNode, type_tree.get_type("IO").methods["in_string"])
        self.build_in_methods([], cil.CILReadIntNode, type_tree.get_type("IO").methods["in_int"])
        self.build_in_methods(["self"], cil.CILPrintStringNode, type_tree.get_type("IO").methods["out_string"])
        self.build_in_methods(["self"], cil.CILPrintIntNode, type_tree.get_type("IO").methods["out_int"])
        #type_tree.get_type("Object").methods["abort"].cil_name = "abort"
        selfvar = VariableInfo("self")
        self.dotcode.append(cil.CILFunctionNode(type_tree.get_type("Object").methods["abort"].cil_name, [cil.CILParamNode(selfvar)], [], [cil.CILAbortNode(selfvar)]))

        attrib = []
        methods = {}
        self.build_type(type_tree.get_type("Object"), attrib, methods)
        self.types.append(cil.CILTypeNode("Object", attrib, methods))
        attrib = []
        methods = {}
        self.build_type(type_tree.get_type("Int"), attrib, methods)
        self.types.append(cil.CILTypeNode("Int", attrib, methods))
        attrib = []
        methods = {}
        self.build_type(type_tree.get_type("String"), attrib, methods)
        self.types.append(cil.CILTypeNode("String", attrib, methods))
        attrib = []
        methods = {}
        self.build_type(type_tree.get_type("Bool"), attrib, methods)
        self.types.append(cil.CILTypeNode("Bool", attrib, methods))
        attrib = []
        methods = {}
        self.build_type(type_tree.get_type("IO"), attrib, methods)
        self.types.append(cil.CILTypeNode("IO", attrib, methods))
        return cil.CILProgramNode(self.types, self.dotdata, self.dotcode)

    @visitor.when(ast.PlusNode)
    def visit(self, node:ast.PlusNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        right_ret = self.visit(node.right, type_tree)
        r = cil.CILPlusNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        r.dest.type = node.type
        return r.dest

    @visitor.when(ast.MinusNode)
    def visit(self, node:ast.MinusNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        right_ret = self.visit(node.right, type_tree)
        r = cil.CILMinusNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        r.dest.type = node.type
        return r.dest

    @visitor.when(ast.StarNode)
    def visit(self, node:ast.StarNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        right_ret = self.visit(node.right, type_tree)
        r = cil.CILStarNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        r.dest.type = node.type
        return r.dest

    @visitor.when(ast.DivNode)
    def visit(self, node:ast.DivNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        right_ret = self.visit(node.right, type_tree)
        r = cil.CILDivNode(self.define_internal_local(), left_ret, right_ret)
        self.instructions.append(r)
        r.dest.type = node.type
        return r.dest

    @visitor.when(ast.NegationNode)
    def visit(self, node:ast.NegationNode, type_tree):
        ret_val = self.visit(node.expr, type_tree)
        if type(ret_val) == int:
            return -ret_val
        r = self.define_internal_local()
        r.type = node.type
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
            if type(ret_val) is VariableInfo:
                node.variable_info.name = ret_val.name
                node.variable_info.vmholder = ret_val.vmholder
            else:
                node.variable_info.vmholder = ret_val
            self.subscribe_internal_local(node.variable_info)
            self.instructions.append(cil.CILAssignNode(node.variable_info, ret_val))
            return ret_val
        var = self.subscribe_internal_local(node.variable_info)
        return var

    @visitor.when(ast.BlockNode)
    def visit(self, node:ast.BlockNode, type_tree):
        result = 0
        for instruction in node.expr_list:
            result = self.visit(instruction, type_tree)
        if isinstance(result, VariableInfo):
            result.type = node.type
        return result

    @visitor.when(ast.AssignNode)
    def visit(self, node:ast.AssignNode, type_tree):
        r = self.visit(node.expr, type_tree)
        if node.variable_info.name in self.current_typename.attributes:
            if (not type(r) == VariableInfo and node.type.name == "Object") or (node.type.name == "Object" and r.type.name in ["Int", "Bool"]):
                box = self.define_internal_local()
                self.instructions.append(cil.CILBoxVariable(r, box))
                self.instructions.append(cil.CILSetAttribNode(self.selftype, node.idx_token, box))
            else:
                self.instructions.append(cil.CILSetAttribNode(self.selftype, node.idx_token, r))
            return r
        elif node.variable_info in self.arguments:
            if (not type(r) == VariableInfo and node.type.name == "Object") or (node.type.name == "Object" and r.type.name in ["Int", "Bool"]):
                self.instructions.append(cil.CILBoxVariable(r, node.variable_info))
            else:
                self.instructions.append(cil.CILAssignNode(node.variable_info, r))
        else:
            if node.variable_info.vmholder is None:
                self.subscribe_internal_local(node.variable_info)
                self.instructions.append(cil.CILAssignNode(node.variable_info, r))
            else:
                if (not type(r) == VariableInfo and node.type.name == "Object") or (node.type.name == "Object" and r.type.name in ["Int", "Bool"]):
                    self.instructions.append(cil.CILBoxVariable(r, node.variable_info))
                else:
                    self.instructions.append(cil.CILAssignNode(node.variable_info, r))

        return node.variable_info

    @visitor.when(ast.IntegerNode)
    def visit(self, node:ast.IntegerNode, type_tree):
        return int(node.integer_token)

    @visitor.when(ast.StringNode)
    def visit(self, node:ast.StringNode, type_tree):
        data = self.register_data(node.string)
        var = self.define_internal_local()
        self.instructions.append(cil.CILLoadNode(var, data))
        var.type = node.type
        return var

    @visitor.when(ast.VariableNode)
    def visit(self, node:ast.VariableNode, type_tree):
        r = self.define_internal_local()
        r.type = node.variable_info.type
        if node.variable_info.name in self.current_typename.attributes:
            self.instructions.append(cil.CILGetAttribNode(r, self.selftype, node.idx_token))
            return r
        elif node.variable_info in self.arguments:
            return node.variable_info
            #self.instructions.append(cil.CILAssignNode(r, node.variable_info))
        else:
            #if node.variable_info.vmholder is not None:
            return node.variable_info
            #else:
                # result = self.define_internal_local()
                # #node.variable_info.name = result.name
                # #node.variable_info.vmholder = result.vmholder
                # self.instructions.append(cil.CILGetAttribNode(result, self.selftype.name, node.idx_token))
                # return result

    @visitor.when(ast.PrintIntegerNode)
    def visit(self, node:ast.PrintIntegerNode, type_tree):
        ret_val = self.visit(node.expr, type_tree)
        strc = cil.CILToStrNode(self.define_internal_local(), ret_val)
        self.instructions.append(strc)
        self.instructions.append(cil.CILPrintIntNode(strc.dest))
        return strc.dest

    @visitor.when(ast.PrintStringNode)
    def visit(self, node:ast.PrintStringNode, type_tree):
        data = self.register_data(node.string_token)
        var = self.define_internal_local()
        self.instructions.append(cil.CILLoadNode(var, data))
        self.instructions.append(cil.CILPrintStringNode(var))
        return 0

    @visitor.when(ast.ScanNode)
    def visit(self, node:ast.ScanNode, type_tree):
        n = cil.CILReadNode(self.define_internal_local())
        self.instructions.append(n)
        return n.dest

    @visitor.when(ast.NewNode)
    def visit(self, node: ast.NewNode, type_tree: TypeTree):
        var = self.define_internal_local()
        var.type = node.type
        self.instructions.append(cil.CILAllocateNode(type_tree.get_type(node.type_token), var))
        t = type_tree.get_type(node.type_token)
        temp = self.current_typename
        selftemp = self.selftype
        self.selftype = var
        while t:
            self.current_typename = t
            for name, attr in t.attributes.items():
                decl = attr.decl
                if decl.expr:
                    self.instructions.append(cil.CILSetAttribNode(var, name, self.visit(decl.expr, type_tree)))
                else:
                    lvar = self.define_internal_local()
                    lvar.type = decl.type
                    self.instructions.append(cil.CILSetAttribNode(var, name, lvar))

            t = t.parent
        self.selftype = selftemp
        self.current_typename = temp
        return var

    @visitor.when(ast.ClassNode)
    def visit(self, node: ast.ClassNode, type_tree):
        vt: ClassType = node.vtable
        methods = {}
        attrib = []
        self.current_typename = vt
        self.build_type(vt, attrib, methods)
        for expr in filter(lambda x: type(x) == ast.MethodNode, node.cexpresion):
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
        v1.type = node.type
        return v1


    @visitor.when(ast.PropertyNode)
    def visit(self, node: ast.PropertyNode, type_tree):
        return self.visit(node.decl, type_tree)


    @visitor.when(ast.MethodNode)
    def visit(self, node: ast.MethodNode, type_tree):
        self.instructions = []
        self.localvars = []
        self.arguments.clear()
        args = [cil.CILParamNode(self.define_selftype())]
        for param in node.params:
            name = self.build_arg_name(node.name, param.idx_token)
            args.append(cil.CILParamNode(param.variable_info))
            param.variable_info.name = name
            self.arguments.append(param.variable_info)

        self.current_function_name = node.vinfo.cil_name
        if node.name != "entry":
            self.instructions.append(cil.CILReturnNode(self.visit(node.body, type_tree)))
        else:
            self.instructions.append(cil.CILEndProgram(self.visit(node.body, type_tree)))
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
        if not isinstance(expr, VariableInfo) or expr.type.name == "Bool" or expr.type.name == "Int" or expr.type.name == "String":
            return 0
        result = cil.CILEqualNode(self.define_internal_local(), expr, 0)
        self.instructions.append(result)
        return result.dest

    @visitor.when(ast.WhileNode)
    def visit(self, node: ast.WhileNode, type_tree):
        start = cil.CILLabelNode(self.gen_label())
        dowhile = cil.CILLabelNode(self.gen_label())
        end = cil.CILLabelNode(self.gen_label())
        self.instructions.append(start)
        v = self.visit(node.conditional_token, type_tree)
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
        tunels = [[]]
        bases = [[]]
        end = cil.CILLabelNode(self.gen_label())
        ends = []
        checkr = self.define_internal_local()
        case_var = None
        if isinstance(expr, VariableInfo) and expr.type.name == "Object":
            case_var = self.define_internal_local()
            self.instructions.append(cil.CILUnboxVariable(expr, case_var))

        for i in range(len(node.expresion_list)):
            temp = cil.CILLabelNode(self.gen_label())
            labels.append(temp)
            for j in range(i + 1, len(node.expresion_list)):
                t1 = cil.CILLabelNode(self.gen_label())
                t2 = cil.CILLabelNode(self.gen_label())
                tunels[len(tunels) - 1].append(t1)
                bases[len(bases) - 1].append(t2)
            bases.append([])
            tunels.append([])
            if isinstance(expr, VariableInfo) and expr.type.name == "Object":
                check = cil.CILCheckHierarchy(checkr, node.expresion_list[i].variable.type_token, case_var)
            else:
                check = cil.CILCheckHierarchy(checkr, node.expresion_list[i].variable.type_token, expr)
            self.instructions.append(check)
            self.instructions.append(cil.CILGotoIfNode(checkr, temp))
        self.instructions.append(cil.CILErrorNode)
        self.instructions.append(cil.CILGotoNode(end))

        for i in range(0, len(node.expresion_list)):
            self.instructions.append(labels[i])
            for j in range(i + 1, len(node.expresion_list)):
                e1 = type_tree.get_type(node.expresion_list[j].variable.type_token)
                e2 = type_tree.get_type(node.expresion_list[i].variable.type_token)
                check = type_tree.check_variance(e2, e1)
                #check = cil.CILCheckTypeHierarchy(checkr, e2, e1)
                #self.instructions.append(check)
                check = 1 if check else 0
                self.instructions.append(cil.CILGotoIfNode(check, tunels[i][j - i -1]))
                self.instructions.append(bases[i][j - i - 1])
            t = cil.CILLabelNode(self.gen_label())
            ends.append(t)
            self.instructions.append(cil.CILGotoNode(t))

        for i in range(0, len(bases)):
            for j in range(0, len(bases[i])):
                self.instructions.append(tunels[i][j])
                if isinstance(expr, VariableInfo) and expr.type.name == "Object":
                    self.instructions.append(cil.CILCheckHierarchy(checkr, node.expresion_list[i + j + 1].variable.type_token, case_var))
                else:
                    self.instructions.append(
                        cil.CILCheckHierarchy(checkr, node.expresion_list[i + j + 1].variable.type_token, expr))
                self.instructions.append(cil.CILGotoIfNode(checkr, labels[i + j + 1]))
                self.instructions.append(cil.CILGotoNode(bases[i][j]))

        r = self.define_internal_local()
        for i in range(len(ends)):
            self.instructions.append(ends[i])
            e = None
            if isinstance(expr, VariableInfo) and expr.type.name == "Object":
                e = self.visit(node.expresion_list[i], type_tree, case_var)
            else:
                e = self.visit(node.expresion_list[i], type_tree, expr)
            self.instructions.append(cil.CILAssignNode(r, e))
            self.instructions.append(cil.CILGotoNode(end))

        self.instructions.append(end)
        return r

    @visitor.when(ast.CaseItemNode)
    def visit(self, node: ast.CaseItemNode, type_tree, expr):
        self.instructions.append(cil.CILAssignNode(self.visit(node.variable, type_tree), expr))
        return self.visit(node.expr, type_tree)

    @visitor.when(ast.BooleanNode)
    def visit(self, node: ast.BooleanNode, type_tree):
        return True if node.value == "true" else False

    @visitor.when(ast.DispatchNode)
    def visit(self, node: ast.DispatchNode, type_tree):
        args = []
        r = self.define_internal_local()
        args.append(cil.CILArgNode(self.selftype))
        i = 0
        for param in node.expresion_list:
            p = self.visit(param, type_tree)
            if (not type(p) == VariableInfo and node.type.name == "Object") or (node.method_type.param_types[i] == "Object" and p.type.name in ["Int", "Bool"]):
                v = self.define_internal_local()
                v.type = type_tree.get_type(node.method_type.param_types[i])
                self.instructions.append(cil.CILBoxVariable(p, v))
                args.append(cil.CILArgNode(v))
            else:
                args.append(cil.CILArgNode(p))
            i += 1
        self.instructions += args
        self.instructions.append(cil.CILDinamicCallNode(self.current_typename.name, node.idx_token, r))
        r.type = node.type
        return r

    @visitor.when(ast.DispatchParentInstanceNode)
    def visit(self, node: ast.DispatchParentInstanceNode, type_tree:TypeTree):
        r = self.define_internal_local()
        args = []
        method = type_tree.get_type(node.parent).methods[node.method]
        args.append(cil.CILArgNode(self.visit(node.variable, type_tree)))
        i = 0
        for param in node.params:
            p = self.visit(param, type_tree)
            if (not type(p) == VariableInfo and node.type.name == "Object") or (method.param_types[i] == "Object" and p.type.name in ["Int", "Bool"]):
                v = self.define_internal_local()
                v.type = type_tree.get_type(method.params[i])
                self.instructions.append(cil.CILBoxVariable(p, v))
                args.append(cil.CILArgNode(v))
            else:
                args.append(cil.CILArgNode(p))
            i += 1
        self.instructions += args
        self.instructions.append(cil.CILStaticCallNode(node.parent, node.method, r))
        r.type = node.type
        return r

    @visitor.when(ast.DispatchInstanceNode)
    def visit(self, node: ast.DispatchInstanceNode, type_tree):
        r = self.define_internal_local()
        args = []
        args.append(cil.CILArgNode(self.visit(node.variable, type_tree)))
        method = node.method_type

        i = 0
        for param in node.params:
            p = self.visit(param, type_tree)
            if (not type(p) == VariableInfo and node.type.name == "Object") or (method.param_types[i] == "Object" and p.type.name in ["Int", "Bool"]):
                v = self.define_internal_local()
                v.type = type_tree.get_type(method.params[i])
                self.instructions.append(cil.CILBoxVariable(p, v))
                args.append(cil.CILArgNode(v))
            else:
                args.append(cil.CILArgNode(p))
            i += 1
        self.instructions += args
        self.instructions.append(cil.CILDinamicCallNode(node.variable.type.name, node.method, r))
        r.type = node.type
        return r

    @visitor.when(ast.LessThanNode)
    def visit(self, node: ast.LessThanNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        rigth_ret = self.visit(node.right, type_tree)
        ret_type = cil.CILLessThanNode(self.define_internal_local(), left_ret, rigth_ret)
        self.instructions.append(ret_type)
        ret_type.dest.type = node.type
        return ret_type.dest

    @visitor.when(ast.LessEqualNode)
    def visit(self, node: ast.LessEqualNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        rigth_ret = self.visit(node.right, type_tree)
        ret_type = cil.CILLessEqualNode(self.define_internal_local(), left_ret, rigth_ret)
        self.instructions.append(ret_type)
        ret_type.dest.type = node.type
        return ret_type.dest

    @visitor.when(ast.EqualNode)
    def visit(self, node: ast.EqualNode, type_tree):
        left_ret = self.visit(node.left, type_tree)
        rigth_ret = self.visit(node.right, type_tree)
        ret_type = cil.CILEqualNode(self.define_internal_local(), left_ret, rigth_ret)
        self.instructions.append(ret_type)
        ret_type.dest.type = node.type
        return ret_type.dest

    @visitor.when(ast.NotNode)
    def visit(self, node: ast.NotNode, type_tree):
        var = self.define_internal_local()
        r = cil.CILNotNode(self.visit(node.expr, type_tree), var)
        self.instructions.append(r)
        return var

    @visitor.when(ast.ComplementNode)
    def visit(self, node, type_tree):
        var = self.define_internal_local()
        r = cil.CILComplementNode(self.visit(node.expr, type_tree), var)
        self.instructions.append(r)
        var.type = node.type
        return var
    # ======================================================================