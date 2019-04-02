# -*- coding: utf-8 -*-

'''
Example:
>>> pr = mathEq.parseString('\\int_0^\\infty f(x) d x\\approx\\sum_{i=1}w_ie^{x_i}f(x_i)')
>>> print(pr)
[approx(int(f(x), x, 0, infty), sum(*(w_i, ^(e, x_i), f(x_i)), i, 1, infty))]
'''

from pyparsing import *
from pyparsing_ext import *

digit = Word(nums)
ESC = Suppress('\\')
SUB = Suppress('_')
SUP = Suppress('^')
DOT = Suppress('.')

def totree(x):
    print(type(x))
    if isinstance(x, str):
        return x
    else:
        return x.totree()



class ActionIntExp(BaseAction):
    names = ('integrated', 'variable', 'lower_bound', 'upper_bound')
    op = 'int'
    def __init__(self, instring='', loc=0, tokens=[]):
        super(ActionIntExp, self).__init__(instring, loc, tokens)
        self.integrated = tokens.integrated
        self.variable = tokens.variable
        self.lower_bound = tokens.lower_bound[0]
        self.upper_bound = tokens.upper_bound[0]

    def __repr__(self):
        return '%s(%s, %s, %s, %s)'%(self.op, self.integrated, self.variable, self.lower_bound, self.upper_bound)

    def totree(self):
        return [self.op, self.integrated.totree(), self.variable, self.lower_bound.totree(), self.upper_bound.totree()]

class ActionSumExp(BaseAction):
    names = ('item', 'index', 'lower_bound', 'upper_bound')
    op = 'sum'

    def __init__(self, instring='', loc=0, tokens=[]):
        super(ActionSumExp, self).__init__(instring, loc, tokens)
        self.item = tokens.item
        self.index = tokens.index
        if 'lower_bound' in tokens:
            self.lower_bound = tokens.lower_bound[0]
        else:
            self.lower_bound = '0'
        if 'upper_bound' in tokens:
            self.upper_bound = tokens.upper_bound[0]
        else:
            self.upper_bound = 'infty'

    def totree(self):
        return [self.op, self.item.totree(), totree(self.index), self.lower_bound.totree(), self.upper_bound.totree()]

    def __repr__(self):
        return '%s(%s, %s, %s, %s)'%(self.op, self.item, self.index, self.lower_bound, self.upper_bound)


class ActionLimExp(BaseAction):
    op = 'lim'
    names = ('item', 'variable', 'value')

    def totree(self):
        return [self.op, self.item.totree(), self.variable, self.value.totree()]

    def __repr__(self):
        return '%s(%s, %s, %s)'%(self.op, self.item, self.variable, self.value)


class ActionFuncExp(BaseAction):
    names = ('function', 'args')
    def __init__(self, instring='', loc=0, tokens=[]):
        super(ActionFuncExp, self).__init__(instring, loc, tokens)
        self.function = tokens.function[0]

    def totree(self):
        return [self.function] + [arg.totree() for arg in self.args]

    def __repr__(self):
        return '%s(%s)'%(self.function, ', '.join(str(arg) for arg in self.args))


class ActionPrefix(BaseAction):
    # prefix operator as -a
    def __init__(self, instring='', loc=0, tokens=[]):
        super(ActionNegExp, self).__init__(instring, loc, tokens)
        self.operand, self.op = tokens[0][0], tokens[0][-1]

    def totree(self):
        return [self.op] + self.operand.totree()

    def __repr__(self):
        return '%s%s'%(slef.op, self.operand)


class ActionCmdExp(BaseAction):
    def __init__(self, instring='', loc=0, tokens=[]):
        super(ActionCmdExp, self).__init__(instring, loc, tokens)
        if 'command1' in tokens:
            self.command = tokens.command1
            self.args=[tokens.arg.content]
        else:
            self.command = tokens.command
            self.args=[arg.content for arg in tokens.args]

    def arity(self):
        return len(self.args)

    def totree(self):
        return [self.command] + [arg.totree() for arg in self.args]

    def __repr__(self):
        return '%s(%s)'%(self.command, ', '.join(str(arg) for arg in self.args))


class ActionOperator(BaseAction):
    # action class for binary operator
    def __init__(self, instring='', loc=0, tokens=[]):
        super(ActionOperator, self).__init__(instring, loc, tokens)
        if 'op' not in tokens[0]:
            self.op = '*'
            self.operands = tokens[0][:]
        else:
            self.op = tokens[0][1]
            self.operands = tokens[0][0::2]

    def totree(self):
        return [self.op] + [operand.totree() for operand in self.operands]

    # def __eq__(self, other):
    #     return isinstance(other, ActionOperator) and self.operands == other.operands and self.op == other.op

    def arity(self):
        return len(self.operands)

    def __repr__(self):
        if hasattr(self, 'op'):
            return '%s(%s)'%(self.op, ', '.join(map(str, self.operands)))
        else:
            return str(self.operands[0])

class ActionBlock(BaseAction):
    names = ('block_content',)

    def totree(self):
        return totree(self.block_content)

    def __repr__(self):
        return '{%s}'%self.block_content

class ActionTerm(BaseAction):
    names = ('term', 'index')
    def __init__(self, instring='', loc=0, tokens=[]):
        super(ActionTerm, self).__init__(instring, loc, tokens)
        self.term = tokens.term
        self.index = tokens.index[0]

    def totree(self):
        if hasattr(self, 'index'):
            return ['index', self.term, totree(self.index)]
        elif isinstance(self.term, (ActionIntExp, ActionFuncExp, ActionSumExp)):
            return self.term.totree()
        else:
            return totree(self.term)

    def __repr__(self):
        if 'index' in self.tokens:
            if isinstance(self.index, AtomAction):
                return f'{self.term}_{self.index}'
            return f'{self.term}_{{{self.index}}}'
        return str(self.term)


class ActionMathExp(BaseAction):
    names = ('expr',)

    def totree(self):
        return self.expr.totree()

    def __repr__(self):
        return str(self.expr)


class ActionMathEq(BaseAction):
    names = ('lhs', 'rhs', 'sign')

    def totree(self):
        return [self.sign, self.lhs.totree(), self.rhs.totree()]

    def __repr__(self):
        return '%s(%s, %s)'%(self.sign, self.lhs, self.rhs)


intcmd = ESC + Literal('int')
sumcmd = ESC + Literal('sum')
limcmd = ESC + Literal('lim')

# printable = Word(alphanums+'+-=<>*/|(),.;:\'', exact=1)
greek = ESC + oneOf('alpha beta gamma delta epsilon lambda mu nu theta sigma phi psi pi eta theta omega')('content')
variable = oneOf('A B C D E F G H I J K L M N O P Q R S T U V W X Y Z a b c e f g h i j k l m n o p q r s t u v w x y z')('content') | greek  # don't use d
variable.setParseAction(VariableAction)

constant = ESC + Literal('infty')('content') | digit('content')
atom = constant | variable
atom.setParseAction(AtomAction)

mathExp = Forward()
mathExp.setParseAction(ActionMathExp)

mathEq = mathExp('lhs') + (oneOf('= < >')('sign') | ESC + oneOf('leq geq approx sim')('sign')) + mathExp('rhs')
mathEq.setParseAction(ActionMathEq)

block = atom |  LBRACE + (mathEq | mathExp) + RBRACE
# block.setParseAction(ActionBlock)

# absExp = Suppres('|') + mathExp('operand') + Suppress('|') | Suppres('\\|') + mathExp('operand') + Suppress('\\|')
# absExp.setParseAction(ActionAbsExp)
# inprodExp = Suppres('\\langle') + mathExp('operand1') + Suppress(',') + mathExp('operand2') + Suppress('\\rangle')

CMD1 = ESC + oneOf('bar sqrt tilde hat check dot ddot')('command1')
CMD2 = ESC + oneOf('frac')('command')
cmdExp = CMD1 + block('arg') | CMD2 + (block + block)('args')
cmdExp.setParseAction(ActionCmdExp)

sumExp = sumcmd.suppress() + ((SUB + LBRACE + variable('index') + Suppress('=') + block('lower_bound') + RBRACE | 
    SUB + variable('index')) & Optional(SUP + block('upper_bound'))) + mathExp('item')
sumExp.setParseAction(ActionSumExp)

intExp = intcmd.suppress() + ((SUB + block('lower_bound')) & (SUP + block('upper_bound'))) \
 + mathExp('integrated') + Suppress('d') + variable('variable')
intExp.setParseAction(ActionIntExp)

limExp = limcmd.suppress() + SUB + LBRACE + variable('variable') + Suppress('\\to') + atom('value') +RBRACE + mathExp('item')
limExp.setParseAction(ActionLimExp)

term = variable('term') + SUB + block('index') | atom('term') \
 | Suppress('(')+ mathExp('term') + Suppress(')')| cmdExp('term') \
 | intExp('term') | sumExp('term')
term.setParseAction(ActionTerm)

func = ESC + oneOf('sin cos tan cot sinh cosh tanh'
    'arcsin arccos arctan arccot ln log exp')('function')
funcExp = (variable('function') | func) + Suppress('(') + delimitedList(mathExp)('args') +Suppress(')') \
| func + Group(variable)('args')
funcExp.setParseAction(ActionFuncExp)

atomExp = funcExp | term | sumExp|  intExp | limExp | block
mathExp <<= operatorPrecedence(atomExp, [(Literal('^')('op'), 2, opAssoc.RIGHT, ActionOperator),
    (Literal('-')('op'), 1, opAssoc.RIGHT, ActionPrefix),
    (Optional('*')('op'), 2, opAssoc.LEFT, ActionOperator),
    (Literal('+')('op'), 2, opAssoc.LEFT, ActionOperator)])('expr')


if __name__ == "__main__":
    # test1
    try:
        pr = mathEq.parseString('\\int_0^\\infty f(x) d x\\approx\\sum_{i=1}w_ie^{x_i}f(x_i)')
        print(pr)
        # [approx(int(f(x), x, 0, infty), sum(*(w_i, ^(e, x_i), f(x_i)), i, 1, infty))]
    except pp.ParseException as pe:
        print(pp.ParseException.explain(pe))


