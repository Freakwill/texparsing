# -*- coding: utf-8 -*-
'''myfile.texfile1

to process tex files
-------------------------------
Path: mywork\myfile\texfile1.py
Author: William/2015-07-27
'''

import basic
from pyparsing import *
from pyparsing_ext  import *
# from myparsing import *

WORD = Word(alphas)
VARIABLE = Word(alphas,exact=1)
DIGIT = Word(nums)
OTHERS = oneOf('+ - * / | ? ! , . = < > \' "')
EQ = Literal('=')
NUM = DIGIT+Optional('.'+ DIGIT)
ESC = Escape()
CMD = ESC.suppress() + WORD
NEWLINE = ESC + Literal('\\')
OPEN = Suppress('{')
CLOSE = Suppress('}')
NOBRACE = CharsNotIn('{}')
CMDX = CMD('command_name') + ZeroOrMore(OPEN.suppress() + NOBRACE + CLOSE.suppress())
BEGIN = ESC+Literal('begin')
END = ESC+Literal('end')
SUB = Literal('_')
SUP = Literal('^')
AND = Literal('&')
LBRACKET = Literal('[')
RBRACKET = Literal(']')
LBRACE = ESC + Literal('{')
RBRACE = ESC + Literal('}')
LPARAN = Literal('[')
RPARAN = Literal(']')
DOLLAR = Literal('$')
DDOLLAR = Literal('$$')
NEWCMD = ESC + Literal('newcommand')
TEXCOMMENT = Literal('%') + restOfLine
PERCENT = ESC + Literal('%')
CMDsf = Regex('(?<!\\\\)(?:\\\\\\\\)*([a-zA-Z]+)')
ATOM = VARIABLE | DIGIT | CMD


class Action:
    # base class for action-classes
    def __init__(self, tokens):
        self.tokens=tokens

    # basic methods
    #def tostr(self):
    #    return ' '.join(self.tokens)

    def __len__(self):
        return len(self.tokens)

    def __eq__(self, other):
        if isinstance(other, Action):
            return self.tokens == other.tokens
        else:
            return self.tokens == other

    def __repr__(self):
        return ' '.join((map(str, self.tokens)))

# operators
class ActionOperator1(Action):
    # action class for unary operator
    def __init__(self, tokens):
        super(ActionOperator1, self).__init__(tokens)
        self.operand, self.op = tokens[0][0], tokens[0][-1]

    def toTree(self):
        return [self.op, self.operand.toTree()]

    def __eq__(self, other):
        return isinstance(other, ActionOperator1) and self.operand == other.operand and self.op == other.op


        
class ActionOperator2(Action):
    # action class for binary operator
    def __init__(self, tokens):
        super(ActionOperator2, self).__init__(tokens)
        self.op = tokens[0][1]
        self.operands = tokens[0][0::2]

    def toTree(self):
        return [self.op, [operand.toTree() for operand in self.operands]]

    def __eq__(self, other):
        return isinstance(other, ActionOperator2) and self.operands == other.operands and self.op == other.op

    def __len__(self):
        return len(self.operands)


class ActionFun(ActionOperator1):
    # action for funcion
    def __init__(self, tokens):
        super(ActionFun, self).__init__(tokens)
        self.function = tokens.function
        self.args = tokens.args if 'args' in tokens else ()

    def __repr__(self):
        return "%s(%s)" %(self.function, str(self.operand))

class ActionAssoc(ActionOperator2):

    def __init__(self, tokens):
        super(ActionAssoc, self).__init__(tokens)
        self.op = ''
        self.operands = tokens[0]

class ActionAdd(ActionOperator2):

    def __init__(self, tokens):
        super(ActionAdd, self).__init__(tokens)
        self.op = '+'
        self.operands = tokens[0]


def cmdx(cmd=WORD, *args):
    ret = Suppress('\\')+cmd
    L=len(args)
    for arg in args:
        ret += OPEN.suppress()+arg+CLOSE.suppress()
    return ret


def cmd_(cmd_name=WORD):
    if isinstance(cmd_name, str):
        cmd_name = Literal(cmd_name)
    return ESC + cmd_name


def env(name=WORD):
    return BEGIN + OPEN + name + CLOSE + SkipTo('\\end') + END + OPEN + name + CLOSE



math_expr = QuotedString('$', multiline=True)


filename = "test.tex"
'''with open(filename) as fo:
    s = fo.read()
    for t, l, n in CMDX.scanString(s):
        print(t)
'''

#for t, l, n in scanFile(CMDX, filename):
#    print(t)


# class ActionTexExps(Action):
#     def __init__(self, tokens):
#         super(ActionTexExps, self).__init__(tokens)

#     def toTree(self):
#         if len(self)==1:
#             return self.tokens[0].toTree()
#         else:
#             return [token.toTree() for token in self.tokens]

#     def __repr__(self):
#         if len(self)==1:
#             return super(ActionTexExps, self).__repr__()
#         else:
#             return '\'('+super(ActionTexExps, self).__repr__()+')'

# class ActionBlock(Action):
#     def __init__(self, tokens):
#         super(ActionBlock, self).__init__(tokens)
#         if self.isatom():
#             self.atom=tokens[0]

#     def isatom(self):
#         return isinstance(self.tokens[0], ActionAtom)

#     def toTree(self):
#         return self.tokens[0].toTree()

#     def __repr__(self):
#         if self.isatom():
#             return str(self.atom)
#         else:
#             return super(ActionBlock, self).__repr__()


# class ActionAtom(Action):
#     def __init__(self, tokens):
#         super(ActionAtom, self).__init__(tokens)
#         self.expr = tokens.arg

#     def toTree(self):
#         return self.expr

#     def __repr__(self):
#         return self.expr


# class ActionCMDX(Action):
#     def __init__(self, tokens):
#         super(ActionCMDX, self).__init__(tokens)
#         self.command=tokens.command
#         self.args=tokens[1:]

#     def arity(self):
#         return len(self.args)

#     def toTree(self):
#         return [self.command] + [arg.toTree() for arg in self.args]

#     def __repr__(self):
#         return '%s(%s)'%(self.command, ' '.join(str(arg) for arg in self.args))

#     def print_(self):
#         pass
        


# CMD0=Suppress('\\')+oneOf('sin cos alpha beta gamma int sum prod subset approx infty')('command')
# CMD1=Suppress('\\')+oneOf('bar sqrt tilde hat check dot ddot')('command')
# CMD2=Suppress('\\')+oneOf('frac')('command')
# printable = Word(alphanums+'+-=<>*/|(),.;:\'', exact=1)

# TexExp = Forward()
# TexExps = OneOrMore(TexExp).setParseAction(ActionTexExps)

# atom = printable | CMD0
# atom.setParseAction(ActionAtom)
# block = (atom('arg') | OPEN + atom('arg') + CLOSE | OPEN + TexExps('arg') + CLOSE)
# block.setParseAction(ActionBlock)
# TexExp << (block | ( (SUB | SUP)('command') + block | CMD1 + block | CMD2 + (block + block)).setParseAction(ActionCMDX))
# TexExps.setParseAction(ActionTexExp)


#pr=TexExps.parseString('\\int_0^\infty f(x)dx\\approx\sum_{i=1}w_ie^{x_i}f(x_i)')
#print(pr[0])


class ActionIntExp(Action):

    def __init__(self, tokens):
        super(ActionIntExp, self).__init__(tokens)
        self.op = 'int'
        self.function = tokens.function
        self.variable=tokens.variable
        self.lower_bound=tokens.lower_bound
        self.upper_bound=tokens.upper_bound

    def __repr__(self):
        return '%s(%s, %s, %s, %s)'%(self.op, self.function, self.variable,self.lower_bound,self.upper_bound)

class ActionSumExp(Action):

    def __init__(self, tokens):
        super(ActionSumExp, self).__init__(tokens)
        self.op = 'sum'
        self.item = tokens.item
        self.index=tokens.index
        self.lower_bound=tokens.lower_bound
        if 'upper_bound' in tokens:
            self.upper_bound=tokens.upper_bound
        else:
            self.upper_bound='infty'

    def __repr__(self):
        return '%s(%s, %s, %s, %s)'%(self.op, self.item, self.index,self.lower_bound,self.upper_bound)

class ActionFunExp(Action):

    def __init__(self, tokens):
        super(ActionFunExp, self).__init__(tokens)
        self.function = tokens.function[0]
        self.args=tokens.args

    def __repr__(self):
        return '%s(%s)'%(self.function, ', '.join(str(arg) for arg in self.args))

class ActionMathExp(Action):

    def __init__(self, tokens):
        super(ActionMathExp, self).__init__(tokens)

class ActionBlock(Action):

    def __init__(self, tokens):
        super(ActionBlock, self).__init__(tokens)
        if isinstance(tokens.content, ActionBlock):
            self.content = tokens.content.content
        else:
            self.content = tokens.content

    def __repr__(self):
        return str(self.content)

class ActionCmdExp(Action):
    def __init__(self, tokens):
        super(ActionCmdExp, self).__init__(tokens)
        self.command=tokens.command
        self.args=tokens[1:]

    def arity(self):
        return len(self.args)

    def __repr__(self):
        return '%s(%s)'%(self.command, ' '.join(str(arg) for arg in self.args))

class ActionMathEq(Action):

    def __init__(self, tokens):
        super(ActionMathEq, self).__init__(tokens)
        self.lhs=tokens.lhs
        self.rhs=tokens.rhs
        self.sign=tokens.sign

    def __repr__(self):
        return '%s(%s, %s)'%(self.sign, self.lhs, self.rhs)

CMD0=Suppress('\\')+oneOf('sin cos alpha beta gamma int sum prod subset approx infty')('command')
CMD1=Suppress('\\')+oneOf('bar sqrt tilde hat check dot ddot')('command')
CMD2=Suppress('\\')+oneOf('frac')('command')

intcmd=Suppress('\\')+Literal('int')
sumcmd=Suppress('\\')+Literal('sum')
printable = Word(alphanums+'+-=<>*/|(),.;:\'', exact=1)
MathExp=Forward()
VARIABLE = Word(alphas, exact=1)
ATOM = VARIABLE | DIGIT | Suppress('\\')+oneOf('alpha beta gamma infty')
FUNC = VARIABLE | CMD0
FunExp = VARIABLE('function') + Suppress('(') + delimitedList(MathExp)('args') +Suppress(')') # | VARIABLE('args')
FunExp.setParseAction(ActionFunExp)
block = ((printable | CMD0)('content') | OPEN + MathExp('content') + CLOSE)
block.setParseAction(ActionBlock)
IntExp=intcmd.suppress() + ((SUB.suppress() + block('lower_bound')) & (SUP.suppress() + block('upper_bound'))) + FunExp('function') + Suppress('d') + VARIABLE('variable')
IntExp.setParseAction(ActionIntExp)
SumExp=sumcmd.suppress() + ((SUB.suppress() + OPEN + VARIABLE('index') + '='+ MathExp('lower_bound') +CLOSE) & Optional(SUP.suppress() + block('upper_bound'))) + restOfLine('item') #+ MathExp('item')
SumExp.setParseAction(ActionSumExp)
CmdExp= (SUB | SUP)('command') + block('args') | CMD1 + block('args') | CMD2 + (block + block)('args')
CmdExp.setParseAction(ActionCmdExp)
MathExp << ATOM | '('+ MathExp +')' | FunExp | IntExp | SumExp | CmdExp | OneOrMore(MathExp)
MathExp.setParseAction(ActionMathExp)
MathEq = IntExp('lhs') + (oneOf('= < >') | Suppress('\\') + oneOf('leq geq approx'))('sign') + SumExp('rhs')
MathEq.setParseAction(ActionMathEq)


# test
pr=MathEq.parseString('\\int_0^\\infty f(x) d x\\approx\\sum_{i=1}w_ie^{x_i}f(x_i)')

print(pr)
