# -*- coding: utf-8 -*-

'''
to parse tex files
'''

import basic
from pyparsing import *
from pyparsing_ext  import *

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
BEGIN = ESC + Literal('begin')
END = ESC + Literal('end')
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

#for t, l, n in parseFile(filename):
#    print(t)



class ActionAtom(BaseAction):
    def __init__(self, instring='', loc=0, tokens=[]):
        super(ActionAtom, self).__init__(instring, loc, tokens)
        self.content = tokens[0]

    def toTree(self):
        return self.content

    def __repr__(self):
        return self.content


# class ActionCMDX(BaseAction):
#     def __init__(self, instring='', loc=0, tokens=[]):
#         super(ActionCMDX, self).__init__(tokens=tokens)
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


class ActionIntExp(BaseAction):
    names = ('integrated', 'variable', 'lower_bound', 'upper_bound')
    op = 'int'

    def __repr__(self):
        return '%s(%s, %s, %s, %s)'%(self.op, self.integrated, self.variable,self.lower_bound,self.upper_bound)

class ActionSumExp(BaseAction):
    names = ('item', 'index', 'lower_bound', 'upper_bound')
    op = 'sum'
    def __init__(self, instring='', loc=0, tokens=[]):
        super(ActionSumExp, self).__init__(instring, loc, tokens)
        if 'upper_bound' in tokens:
            self.upper_bound=tokens.upper_bound
        else:
            self.upper_bound='infty'

    def __repr__(self):
        return '%s(%s, %s, %s, %s)'%(self.op, self.item, self.index,self.lower_bound,self.upper_bound)

class ActionFunExp(BaseAction):
    names = ('function', 'args')

    def arity(self):
        return len(self.args)

    def __repr__(self):
        return '%s(%s)'%(self.function, ', '.join(str(arg) for arg in self.args))

class ActionMathExp(BaseAction):
    pass

class ActionBlock(BaseAction):

    names = ('block',)

    def __repr__(self):
        return str(self.block)

class ActionCmdExp(BaseAction):
    names = ('command', 'args', 'options')

    def arity(self):
        return len(self.args)

    def __repr__(self):
        return '%s[](%s)'%(self.command, ' '.join(map(str, self.options)), ' '.join(map(str, self.args)))

class ActionMathEq(BaseAction):
    names = ('lhs', 'rhs', 'sign')

    def __repr__(self):
        return '%s(%s, %s)'%(self.sign, self.lhs, self.rhs)

CMD0 = Suppress('\\') + oneOf('sin cos alpha beta gamma int sum prod subset approx infty')('command')
CMD1 = Suppress('\\') + oneOf('bar sqrt tilde hat check dot ddot')('command')
CMD2 = Suppress('\\') + oneOf('frac')('command')

intcmd = Suppress('\\') + Literal('int')
sumcmd = Suppress('\\') + Literal('sum')
MathExp = Forward()
VARIABLE = Word(alphas, exact=1)
ATOM = VARIABLE('content') | DIGIT('content') | Suppress('\\') + oneOf('alpha beta gamma infty')('content')
ATOM.setParseAction(ActionAtom)
FUNC = VARIABLE | CMD0
FunExp = VARIABLE('function') + Suppress('(') + delimitedList(MathExp)('args') + Suppress(')') # | VARIABLE('args')
FunExp.setParseAction(ActionFunExp)
block = ATOM('block') | CMD0('block') | OPEN + MathExp('block') + CLOSE
block.setParseAction(ActionBlock)
IntExp = intcmd.suppress() + ((SUB.suppress() + block('lower_bound')) & (SUP.suppress() + block('upper_bound'))) + FunExp('integrated') + Suppress('d') + VARIABLE('variable')
IntExp.setParseAction(ActionIntExp)
SumExp = sumcmd.suppress() + ((SUB.suppress() + OPEN + VARIABLE('index') + '='+ MathExp('lower_bound') +CLOSE) & Optional(SUP.suppress() + block('upper_bound'))) + restOfLine('item') #+ MathExp('item')
SumExp.setParseAction(ActionSumExp)
CmdExp = (SUB | SUP)('command') + block('args') | CMD1 + block('args') | CMD2 + (block + block)('args')
CmdExp.setParseAction(ActionCmdExp)
MathExp << ATOM | '('+ MathExp +')' | FunExp | IntExp | SumExp | CmdExp | OneOrMore(MathExp)
MathExp.setParseAction(ActionMathExp)
MathEq = IntExp('lhs') + (oneOf('= < >')('sign') | Suppress('\\') + oneOf('leq geq approx')('sign')) + SumExp('rhs')
MathEq.setParseAction(ActionMathEq)


if __name__ == '__main__':
    
    pr = MathEq.parseString('\\int_0^\\infty f(x) d x\\approx\\sum_{i=1}w_ie^{x_i}f(x_i)')
    print(pr[0])


