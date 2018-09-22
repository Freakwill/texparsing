# -*- coding: utf-8 -*-
# macro.py
# macro for python based on pyparsing
# example: see the end of the file

import re
import pyparsing as pp


# basic expressions
IDEN = pp.Word(pp.alphas+'_', pp.alphanums+'_')
_symbol = '-_[]<>%$^|{}*+/\\!~#?.,;:'
SYMBLE = pp.Word(_symbol)
LPAREN = pp.Suppress('(')
RPAREN = pp.Suppress(')')
LBRACE = pp.Suppress('{')
RBRACE = pp.Suppress('}')
STAR = pp.Suppress('*')
COMMA = pp.Suppress(',')
IDEXT = pp.Word(pp.alphas+_symbol, pp.alphanums + _symbol)
IDS = pp.delimitedList(IDEN)
VAR = IDEN('name')
ARGS = IDS('args') + pp.Optional(COMMA + STAR + IDEN('star')) | STAR + IDEN('star')
DIGIT = pp.Word(pp.nums)
NUMBER = DIGIT + pp.Optional('.' + DIGIT)
WORD = pp.Word(pp.alphas)
W = pp.Word(pp.alphanums)
TEXCMD = '\\' + WORD


def termList(term=IDEN, n=1):
    if n==0:
        return pp.empty
    if n==1:
        return pp.Group(term)
    else:
        return (term + COMMA)*(n-1) + term

# class for actions
class BaseAction:
    # base class for action-classes
    def __init__(self, tokens):  # instring, loc,
        self.tokens = tokens
        #self.instring = instring
        #self.loc = loc

    def has(self, name):
        return name in self.tokens

    def __eq__(self, other):
        if isinstance(other, BaseAction):
            return self.tokens == other.tokens
        else:
            return self.tokens == other


class LHSAction(BaseAction):
    # base action class for left hand side of macro
    def __init__(self, tokens):
        super(LHSAction, self).__init__(tokens)
        if self.has_args():
            self.args = tokens.args
        else:
            self.args =[]
        if self.has_star():
            self.star = tokens.star[0]
    # basic methods
    def has_star(self):
        return self.has('star')

    def has_args(self):
        return self.has('args')

    def arity(self):
        return len(self.args)

    def __repr__(self):
        return ', '.join(map(str, self.tokens))

    def topyp(self):
        return NotImplemented


class FunAction(LHSAction):
    # class of action for f(a, b, c)
    def __init__(self, tokens):
        super(FunAction, self).__init__(tokens)
        self.name = tokens.name

    def topyp(self, term=IDEN):
        # be implemented naccessarily
        terms = pp.delimitedList(term)
        if self.has_star():           # with varargs
            if self.arity()==0:
                PYP = pp.Literal(str(self.name)) + LPAREN + terms('args') + RPAREN
            else:
                PYP = pp.Literal(str(self.name)) + LPAREN + ((term + COMMA)*self.arity()+  terms)('args') + RPAREN
        else:
            # function(term, term, ..., term)
            PYP = pp.Literal(str(self.name)) + LPAREN + termList(term, self.arity())('args') + RPAREN
        return PYP

    def tore(self):
        if self.has_star():
            if self.arity()==0:
                return '%s((.*?,)*(.*?))'%self.name
            else:
                return '%s(%s, (,.*?)*)'%(self.name, ', '.join(['.*?']*self.arity()))
        else:
            return '%s(%s)'%(self.name, ', '.join(['.*?']*self.arity()))

    def __repr__(self):
        if self.has_star():
            if self.arity()==0:
                return '%s(*%s)'%(self.name, self.star)
            else:
                return '%s(%s, *%s)'%(self.name, ', '.join(self.args), self.star)
        else:
            return '%s(%s)'%(self.name, ', '.join(self.args))

class PrefixAction(LHSAction):
    # class of action for +(a, b, c)
    def __init__(self, tokens):
        super(PrefixAction, self).__init__(tokens)
        self.op = tokens.op

    def topyp(self, term=IDEN):
        terms = pp.delimitedList(term)
        if self.has_star():
            if self.arity()==0:
                PYP = pp.Literal(str(self.op)) + LPAREN + terms('args') + RPAREN
            else:
                PYP = pp.Literal(str(self.op)) + LPAREN + ((term + COMMA)*self.arity()+  terms)('args') + RPAREN
        else:
            PYP = pp.Literal(str(self.op)) + LPAREN + termList(term, self.arity())('args') + RPAREN
        return PYP

    def tore(self):
        if self.has_star():
            if self.arity()==0:
                return '%s((.*?,)*(.*?))'%self.op
            else:
                return '%s(%s, (,.*?)*)'%(self.op, ', '.join(['.*?']*self.arity()))
        else:
            return '%s(%s)'%(self.op, ', '.join(['.*?']*self.arity()))

    def __repr__(self):
        if self.has_star():
            if self.arity()==0:
                return '%s(*%s)'%(self.op, self.star)
            else:
                return '%s(%s, *%s)'%(self.op, ', '.join(self.args), self.star)
        else:
            return '%s(%s)'%(self.op, ', '.join(self.args))

class PostfixAction(LHSAction):
    # class of action for postfix notation such as (a, b, c)+
    def __init__(self, tokens):
        super(PostfixAction, self).__init__(tokens)
        self.op = tokens.op

    def topyp(self, term=IDEN):
        terms = pp.delimitedList(term)
        if self.has_star():
            if self.arity()==0:
                PYP = LPAREN + terms('args') + RPAREN + pp.Literal(str(self.op))
            else:
                PYP = LPAREN + ((term + COMMA)*self.arity()+  terms)('args') + RPAREN + pp.Literal(str(self.op))
        else:
            PYP = LPAREN + termList(term, self.arity())('args') + RPAREN + pp.Literal(str(self.op))
        return PYP

    def tore(self):
        if self.has_star():
            if self.arity()==0:
                return '((.*?,)*(.*?))%s'%self.op
            else:
                return '(%s, (,.*?)*)%s'%(', '.join(['.*?']*self.arity()), self.op)
        else:
            return '(%s)%s'%(', '.join(['.*?']*self.arity()), self.op)

    def __repr__(self):
        if self.has_star():
            if self.arity()==0:
                return '(*%s)%s'%(self.star, self.op)
            else:
                return '(%s, *%s)%s'%(', '.join(self.args), self.star, self.op)
        else:
            return '(%s)%s'%(', '.join(self.args), self.op)


class BifixAction(LHSAction):
    # class of action for bifix notation such as |a, b, c|
    def __init__(self, tokens):
        super(BifixAction, self).__init__(tokens)
        self.lop, self.rop = tokens.lop, tokens.rop
        self.op = str(self.lop) +' '+ str(self.rop)

    def topyp(self, term=IDEN):
        terms = pp.delimitedList(term)
        if self.has_star():
            if self.arity()==0:
                PYP = pp.Literal(str(self.lop)) + LPAREN + terms('args') + RPAREN + pp.Literal(str(self.rop))
            else:
                PYP = pp.Literal(str(self.lop)) + LPAREN + ((term + COMMA)*self.arity()+  terms)('args') + RPAREN + pp.Literal(str(self.rop))
        else:
            PYP =  pp.Literal(str(self.lop)) + termList(term, self.arity())('args') + pp.Literal(str(self.rop)) \
            | pp.Literal(str(self.lop)) + LPAREN + termList(term, self.arity())('args') + RPAREN + pp.Literal(str(self.rop))
        return PYP

    def tore(self):
        if self.has_star():
            if self.arity()==0:
                return '%s((.*?,)*(.*?))%s'%(self.lop, self.rop)
            else:
                return '%s(%s, (,.*?)*)%s'%(self.lop, ', '.join(['.*?']*self.arity()), self.rop)
        else:
            return '%s(%s)%s'%(self.lop, ', '.join(['.*?']*self.arity()), self.rop)

    def __repr__(self):
        if self.has_star():
            if self.arity()==0:
                return '%s*%s%s'%(self.lop, self.star, self.rop)
            else:
                return '%s%s, *%s%s'%(self.lop, ', '.join(self.args), self.star, self.rop)
        else:
            return '%s%s%s'%(self.lop, ', '.join(self.args), self.rop)


class InfixAction(LHSAction):

    def __init__(self, tokens):
        super(InfixAction, self).__init__(tokens)
        self.op = tokens.op
        self.args = [tokens.arg1, tokens.arg2]

    def topyp(self, term=IDEN):
        return term('arg1') + pp.Literal(str(self.op)) + term('arg2')

    def tore(self):
        return '(.*?)%s(.*?)'%self.op

    def __repr__(self):
        return '%s %s %s'%(self.args[0], self.op, self.args[1])


class Infix3Action(LHSAction):

    def __init__(self, tokens):
        super(Infix3Action, self).__init__(tokens)
        self.op1, self.op2 = tokens.op1, tokens.op2
        self.args = [tokens.arg1, tokens.arg2, tokens.arg3]

    def topyp(self, term=IDEN):
        return term('arg1') + pp.Literal(self.op1) + term('arg2') + pp.Literal(self.op2) + term('arg3')

    def tore(self):
        return '(.*?)%s(.*?)%s(.*?)'%(self.op1, self.op2)

    def __repr__(self):
        return '%s %s %s %s %s'%(self.args[0], self.op1, self.args[1], self.op2, self.args[2])

class AssocAction(LHSAction):

    def __init__(self, tokens):
        super(AssocAction, self).__init__(tokens)
        self.args = tokens.args
        self.op = ''
        if self.has_op():
            self.lop, self.rop = tokens.lop, tokens.rop
            self.op = str(self.lop) +' '+ str(self.rop)

    def has_op(self):
        return self.has('lop') and self.has('rop')

    def topyp(self, term=IDEN):
        if self.has_op():
            return pp.Literal(str(self.lop)) + (term * self.arity())('args') + pp.Literal(str(self.rop))
        else:
            return (term * self.arity())('args') | LPAREN + (term * self.arity())('args') + RPAREN

    def tore(self):
        if self.has_op():
            return str(self.lop) + '(.*?)'*self.arity() + str(self.rop)
        return '(.*?)'*self.arity()

    def __repr__(self):
        if self.has_op():
            return str(self.lop) + ' '.join(self.args) + str(self.rop)
        return ' '.join(self.args)


"""class RedAction(LHSAction):

    def __init__(self, tokens):
        super(RedAction, self).__init__(tokens)
        self.args = tokens.args
        self.op = ''

    def topyp(self, term=IDEN):
        return (term + pp.OneOrMore(term))('args') | LPAREN + (term + pp.OneOrMore(term))('args') + RPAREN

    def __repr__(self):
        return '(.*?){2,}'"""


#CMD = FUN + pp.Literal('=').suppress() + EXP
FUN = IDEN('name') + LPAREN + ARGS + RPAREN # f(a,b)
# LISP = LPAREN + IDEXT('name') + pp.OneOrMore(IDEN)('args') + RPAREN
PREFIX = SYMBLE('op') + LPAREN + ARGS + RPAREN  # +(a,b)
POSTFIX = LPAREN + ARGS + RPAREN + SYMBLE('op')  # (a,b)+
BIFIX = SYMBLE('lop') + ARGS + SYMBLE('rop')  # <a,b>
INFIX = IDEN('arg1') + SYMBLE('op') + IDEN('arg2')  # a + b
INFIX3 = IDEN('arg1') + SYMBLE('op1') + IDEN('arg2') + SYMBLE('op2') + IDEN('arg3')   # a + b - c
# INFIXn = IDEN('arg1') + pp.OneOrMore(SYMBLE + IDEN)('arg2')
LATEX = pp.Suppress('\\') + WORD + pp.ZeroOrMore(LBRACE + IDEN + RBRACE)('args')

ASS = (IDEN + pp.OneOrMore(IDEN))('args') | LPAREN + (IDEN + pp.OneOrMore(IDEN))('args') + RPAREN \
 | SYMBLE('lop') + (IDEN + pp.OneOrMore(IDEN))('args') + SYMBLE('rop')   # a b or |a b| or (a b)

LHS = BIFIX.setParseAction(BifixAction) | FUN.setParseAction(FunAction) | PREFIX.setParseAction(PrefixAction) \
| POSTFIX.setParseAction(PostfixAction) | INFIX3.setParseAction(Infix3Action)  | INFIX.setParseAction(BifixAction)| ASS.setParseAction(AssocAction)

restOfString = pp.Regex(r".*", flags=re.DOTALL).setName("rest of string")
CMD = LHS('lhs') + pp.Suppress('=') + restOfString('rhs')

def subaction(rhs, args):
    # subsitute the arguments in rhs with real arguments appearing in input string
    # for example, define f(x) = x + x, "f(helloworld)" => "helloworld + helloworld"
    def F(tokens):
        if 'args' in tokens:           # Fun Prefix Postfix Bifix
            targs = tokens.args
        elif 'arg1' in tokens and 'arg2' in tokens:
            if 'arg3' in tokens:
                targs = targs = tokens.arg1, tokens.arg2, tokens.arg3  # Infix3
            else:
                targs = tokens.arg1, tokens.arg2                       # Infix
        exp = rhs
        for arg, targ in zip(args, targs):
            argsub = pp.Literal(arg).setParseAction(pp.replaceWith(targ)) # subsitute the arguments
            exp = argsub.transformString(exp)
        return exp
    return F

# expressions that are supported
default_list = [BIFIX.setParseAction(BifixAction), FUN.setParseAction(FunAction), PREFIX.setParseAction(PrefixAction), POSTFIX.setParseAction(PostfixAction), INFIX3.setParseAction(Infix3Action), INFIX.setParseAction(InfixAction), ASS.setParseAction(AssocAction)]


class Macro:
    # Macro class
    def __init__(self, commands=[], term=IDEN):
        # commands: dict of commands
        # term: token for the argument of commands. substitute F(x, y) = G(x, y) for terms x, y
        self.commands = []
        self.term = pp.Combine(term)
        self.lhs_list = default_list
        for lhs_rhs in commands:
            if isinstance(lhs_rhs, str):
                p = CMD.parseString(lhs_rhs)
                self.commands.append((str(p.lhs), p.rhs))
            else:
                lhs, rhs = lhs_rhs
                self.commands.append(lhs, rhs)
        self.make_parser()

    def make_parser(self):
        self.parser = pp.MatchFirst(self.lhs_list)

    def append(self, lhs):
        self.lhs_list.append(lhs)
        self.parser = pp.MatchFirst(self.lhs_list)

    def find(self, s):
        # s need be substituted
        for lhs, rhs in self.commands:
            p = self.parser.parseString(lhs, parseAll=True)[0]
            pyp = p.topyp(self.term)
            try:
                if pyp.searchString(s):
                    return True
            except:
                continue
        return False


    def sub(self, s):
        if not self.find(s):
            return s
        for lhs, rhs in self.commands:
            p = self.parser.parseString(lhs, parseAll=True)[0]
            pyp = p.topyp(self.term)    # transform lhs to parser (of pyparsing)
            pyp.setParseAction(subaction(rhs, p.args))
            s = pyp.transformString(s)
        return s

    def __repr__(self):
        return repr(self.commands)

# test
if __name__ == "__main__":
    R = pp.Forward()
    baseExpr = pp.Regex('(\\b|(?<=\d))\w\\b') | DIGIT
    L1 = baseExpr | '(' + R +')'
    L2 = L1 + pp.ZeroOrMore(pp.Optional('*') + L1)
    R <<= L2 + pp.ZeroOrMore('+' + L2)

    mac = Macro(commands=['x y= x * y'], term = baseExpr | R)

    test='''in math, x y + x z is equal to x (y + z), 3x == 3*x'''

    print('1: %s => %s'%(test, mac.sub(test)))

    mac = Macro(commands=['||x||=norm(x)', '|x|=abs(x)', '<x, y>=innerProduct(x, y)'], term = pp.quotedString | IDEN)

    test='''||hello|| + |world| + <"Hello", "World">'''

    print('2: %s => %s'%(test, mac.sub(test)))

    mac = Macro(commands=['+(a, b, c)=a, b love c', '(a, b, c)+ = a, b miss c'], term = pp.quotedString | IDEN)

    test='''+(Lily, I, You). Moreover, (Lily, I, You)+.'''

    print('3:%s => %s'%(test, mac.sub(test)))