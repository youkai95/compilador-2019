import sys

from ply import yacc
from ply import lex
from checksemantics import CheckSemanticsVisitor

import ast_hierarchy as ast
import logging

from checktype import CheckTypeVisitor
from cilwriter import CILWriterVisitor
from cool_to_cil import COOLToCILVisitor
from mipswriter import MIPSWriterVisitor
from scope import Scope
from typevisitor import CheckTypeVisitor_1st, CheckTypeVisitor_2nd

logging.basicConfig(
    level=logging.DEBUG,
    filename="parselog.txt",
    filemode="w",
    format="%(filename)10s:%(lineno)4d:%(message)s"
)
log = logging.getLogger()

###############################################################Tokens################################################################
reserved = {
    'class': 'CLASS',
    'let': 'LET',
    'loop': 'LOOP',
    'inherits': 'INHERITS',
    'pool': 'POOL',
    'if': 'IF',
    'then': 'THEN',
    'else': 'ELSE',
    'fi': 'FI',
    'while': 'WHILE',
    'case': 'CASE',
    'of': 'OF',
    'esac': 'ESAC',
    'new': 'NEW',
    'not': 'NOT',
    'true': 'TRUE',
    'false': 'FALSE',
    'isvoid': 'ISVOID',
    'in': 'IN',
}
tokens = ['white_space',
          'comma', 'semicolon', 'obracket', 'cbracket', 'ocurly', 'ccurly', 'assign', 'plus', 'minus',
          'star', 'div', 'printx',
          'scanx', 'idx', 'string', 'complement', 'number', 'less', 'less_equal', 'equal', 'case_expr', 'arrobe', 'dot',
          'doubledot'] + list(reserved.values())

t_white_space = r"[ \t\r\f\v\n]+"
t_comma = r','
t_semicolon = r';'
t_obracket = r'\('
t_cbracket = r'\)'
t_ocurly = r'\{'
t_ccurly = r'\}'
t_assign = r'<-'
t_plus = r'\+'
t_minus = r'\-'
t_star = r'\*'
t_div = r'/'
t_printx = r'print'
t_scanx = r'scan'
t_number = r'[0-9]+'
t_string =  r'\"([^\\\n]|(\\.))*?\"' #r'\"(([_-\x09\x0b-!\#-_])*(\\\n))*\"' # #  #r'\"(([a-z\x0b-!\#-_])*(\\\n))*\"'
t_complement = r'~'
t_less = r'<'
t_less_equal = r'<='
t_equal = r'='
t_case_expr = r'=>'
t_arrobe = r'@'
t_dot = r'\.'
t_doubledot = r':'

t_ignore = ' \t'

precedence = (
    ('right', 'assign'),
    ('left', 'NOT'),
    ('nonassoc', 'less', 'less_equal', 'equal'),
    ('left', 'plus', 'minus'),
    ('left', 'star', 'div'),
    ('right', 'ISVOID'),
    ('right', 'complement'),
    ('left', 'dot'),
)


def t_idx(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'idx')  # Check for reserved words
    return t


####################################################################Rules#################################################################
def p_empty(p):
    'empty :'
    pass


def p_binary_operator(p):
    '''binary_operator : v_expr plus v_expr
                    | v_expr minus v_expr
                | v_expr star v_expr
            | v_expr div v_expr'''
    if p[2] == '+':
        p[0] = ast.PlusNode(p[1], p[3])
    elif p[2] == '-':
        p[0] = ast.MinusNode(p[1], p[3])
    elif p[2] == '*':
        p[0] = ast.StarNode(p[1], p[3])
    elif p[2] == '/':
        p[0] = ast.DivNode(p[1], p[3])


def p_program(p):
    '''program : class_expresion semicolon program_a'''
    p[0] = ast.ProgramNode([p[1]] + p[3])


def p_program_a(p):
    '''program_a : class_expresion semicolon program_a
		    | empty'''
    if len(p) > 2:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = []


def p_neg(p):
    '''neg : NOT expr'''
    p[0] = ast.NotNode(p[2])


def p_compl(p):
    '''compl : complement expr'''
    p[0] = ast.ComplementNode(p[2])


def p_assign_expresion(p):
    '''assign_expresion : idx assign expr'''
    p[0] = ast.AssignNode(p[1], p[3])


def p_declare_expresion(p):
    '''declare_expresion : idx doubledot idx assign expr
    				| idx doubledot idx'''
    if len(p) > 4:
        p[0] = ast.DeclarationNode(p[1], p[3], p[5])
    else:
        p[0] = ast.DeclarationNode(p[1], p[3])


def p_declare_method(p):
    '''declare_method : idx doubledot idx'''
    p[0] = ast.DeclarationNode(p[1], p[3])


def p_new_expresion(p):
    '''new_expresion : NEW idx'''
    p[0] = ast.NewNode(p[2])


def p_class_expresion(p):  #
    '''class_expresion : CLASS idx ocurly feature
		  | CLASS idx INHERITS idx ocurly feature'''
    if p[3] == '{':
        p[0] = ast.ClassNode(p[2], None, p[4])
    elif p[3] == 'inherits':
        p[0] = ast.ClassNode(p[2], p[4], p[6])


def p_feature(p):
    '''feature : method_decl feature
                | property_decl feature
				| ccurly'''
    if len(p) > 2:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []

def p_method_decl(p):
    '''method_decl : idx obracket formal cbracket doubledot idx ocurly expr ccurly semicolon'''
    p[0] = ast.MethodNode(p[1], p[3], p[6], p[8])


def p_formal(p):
    ''' formal : declare_method formal_a
                | empty '''
    if len(p) > 2:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = []


def p_formal_a(p):
    '''formal_a : comma declare_method formal_a
                | empty'''
    if len(p) > 2:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []

def p_expr(p):
    '''expr : assign_expresion
            | while_expresion
            | v_expr'''
    p[0] = p[1]


def p_comparison_expresion(p):
    '''comparison_expresion : v_expr less v_expr
                            | v_expr less_equal v_expr
                            | v_expr equal v_expr'''
    if p[2] == '<':
        p[0] = ast.LessThanNode(p[1], p[3])
    elif p[2] == '<=':
        p[0] = ast.LessEqualNode(p[1], p[3])
    elif p[2] == '=':
        p[0] = ast.EqualNode(p[1], p[3])


def p_v_expr(p):
    '''v_expr : conditional_expresion
            | let_expresion
            | case_expresion
            | dispatch_expresion
            | dispatch_instance
            | block_expresion
            | binary_operator
            | neg
            | compl
            | is_void
            | new_expresion
            | term
            | comparison_expresion'''
    p[0] = p[1]

def p_term(p):
    '''term : var
            | num
            | str
            | bool
            | negnum
            | obracket v_expr cbracket'''
    if p[1] == '(':
        p[0] = p[2]
    else:
        p[0] = p[1]


def p_var(p):
    '''var : idx'''
    p[0] = ast.VariableNode(p[1])


def p_num(p):
    '''num : number'''
    p[0] = ast.IntegerNode(p[1])

def p_negnum(p):
    '''negnum : minus term'''
    p[0] = ast.NegationNode(p[2])

def p_str(p):
    '''str : string'''
    p[0] = ast.StringNode(p[1])


def p_bool(p):
    '''bool : TRUE
            | FALSE'''
    p[0] = ast.BooleanNode(p[1])

def p_block_expresion(p):
    '''block_expresion : ocurly block_expr ccurly'''
    p[0] = ast.BlockNode(p[2])


def p_block_expr(p):
    '''block_expr : expr semicolon block_expr_a'''
    p[0] = [p[1]] + p[3]


def p_block_expr_a(p):
    '''block_expr_a : expr semicolon block_expr_a
                    | empty'''
    if len(p) > 2:
        p[0] = [p[1]] + p[3]
    else:
        p[0] = []


def p_property_decl(p):
    '''property_decl : declare_expresion semicolon'''
    p[0] = ast.PropertyNode(p[1])


def p_conditional_expresion(p):
    '''conditional_expresion : IF v_expr THEN expr ELSE expr FI'''
    p[0] = ast.IfNode(p[2], p[4], p[6])


def p_is_void(p):
    '''is_void : ISVOID expr'''
    p[0] = ast.IsVoidNode(p[2])


def p_while_expresion(p):
    '''while_expresion : WHILE v_expr LOOP expr POOL'''
    p[0] = ast.WhileNode(p[2], p[4])


def p_case_expresion(p):
    '''case_expresion : CASE expr OF case_list ESAC'''
    p[0] = ast.CaseNode(p[2], p[4])


def p_case_list(p):
    '''case_list : declare_method case_expr expr semicolon case_list_a'''
    p[0] = [ast.CaseItemNode(p[1], p[3])] + p[5]


def p_case_list_a(p):
    '''case_list_a : declare_method case_expr expr semicolon case_list_a
                | empty'''
    if len(p) > 2:
        p[0] = [ast.CaseItemNode(p[1], p[3])] + p[5]
    else:
        p[0] = []


def p_let_expresion(p):
    '''let_expresion : LET let_declr_list IN expr'''
    p[0] = ast.LetInNode(p[2], p[4])


def p_let_declr_list(p):
    '''let_declr_list : declare_expresion let_declr_list_a'''
    p[0] = [p[1]] + p[2]


def p_let_declr_list_a(p):
    '''let_declr_list_a : comma declare_expresion let_declr_list_a
                        | empty'''
    if len(p) > 3:
        p[0] = [p[2]] + p[3]
    else:
        p[0] = []


def p_dispatch_expresion(p):
    '''dispatch_expresion : idx obracket dispatch_p_list cbracket '''
    p[0] = ast.DispatchNode(p[1], p[3])


def p_dispatch_instance(p):
    '''dispatch_instance : v_expr dot idx obracket dispatch_p_list cbracket
                        | v_expr arrobe idx dot idx obracket dispatch_p_list cbracket '''
    if len(p) > 7:
        p[0] = ast.DispatchParentInstanceNode(p[1], p[3], p[5], p[7])
    else:
        p[0] = ast.DispatchInstanceNode(p[1], p[3], p[5])


def p_dispatch_p_list(p):
    '''dispatch_p_list : v_expr dispatch_p_list_a
                    | empty'''
    if len(p) > 2:
        p[0] =  [p[1]] + p[2]
    else:
        p[0] = []

def p_dispatch_p_list_a(p):
    '''dispatch_p_list_a : comma v_expr dispatch_p_list_a
                    | empty'''
    if len(p) > 2:
        p[0] =  [p[2]] + p[3]
    else:
        p[0] = []

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

parser = yacc.yacc(start="program")
l = lex.lex(debug=True, debuglog=log)

f = open(sys.argv[1], 'r')
text = "".join(f.readlines())
v = parser.parse(text, lexer=l)

# CUSTOM TYPES CHECK (1st step)
errors = []
tvisitor = CheckTypeVisitor_1st()
type_tree = tvisitor.visit(v, errors)

if len(errors) > 0:
    for e in errors:
        print(e)
    exit()

# CUSTOM TYPES CHECK (2nd step)
tvisitor = CheckTypeVisitor_2nd()
tvisitor.visit(v, type_tree, errors)

if len(errors) > 0:
    for e in errors:
        print(e)
    exit()

# CHECK SEMANTICS
errors = []
scope = Scope()
csvisitor = CheckSemanticsVisitor()
is_ok = csvisitor.visit(v, scope, errors)

if len(errors) > 0:
    print('Fail!')
    for e in errors:
        print(e)
    exit()

typecheck = CheckTypeVisitor()
typecheck.visit(v, type_tree, errors)

if len(errors) > 0:
    print('Fail!')
    for e in errors:
        print(e)
    exit()
# ===============================================================

if not is_ok:
    exit()

# CIL GENERATION
cil = COOLToCILVisitor()
a = cil.visit(v, type_tree)

writer = MIPSWriterVisitor()
writer.visit(a, type_tree)

file = open(sys.argv[2], 'w')
file.writelines(writer.output)
file.close()

print('Succeed!')