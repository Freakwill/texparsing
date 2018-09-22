# -*- coding: utf-8 -*-
'''myfile.parsepy

parse py file

-------------------------------
Path: mywork\myfile\parsepy.py
Author: William/2015-10-20
'''

import pyparsing

import myparse

class ParseClass:
    def __init__(self, tokens):
        self.child = tokens['Child']
        self.parents = tokens['Parents']

    def generateList(self):
        return [str(self.child)]+list(map(str, self.parents))

    def __repr__(self):
        return str(self.child)+'->'+','.join(map(str, self.parents))


ClassName = pyparsing.Combine(pyparsing.Optional('_')+ pyparsing.Word(pyparsing.srange('[A-Z]'), pyparsing.alphanums)) | pyparsing.Literal('object')
ClassDef = myparse.classkey.suppress() + ClassName.setResultsName('Child') + pyparsing.Literal('(').suppress() + pyparsing.delimitedList(ClassName).setResultsName('Parents')+pyparsing.Literal(')').suppress() + pyparsing.Literal(':').suppress()
ClassDef.setParseAction(ParseClass)

import graphx
G=graphx.DGraph()
fname='D:\\Python\\mytest\\myparsing.py'
with open(fname) as f:
    c = f.read()

for t, a, b in ClassDef.scanString(c):
    t=t[0]
    G.add_star(t.generateList())

G.drawx()
