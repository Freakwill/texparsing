# -*- coding: utf-8 -*-
'''myfile.texfile1

to process tex files
-------------------------------
Path: mywork\myfile\texfile1.py
Author: William/2015-07-27
'''

import basic
import re
from texfile import *
import mystr

CMD='\\\\'+WORD
CMDX=CMD+'(?:\{.*?\})*'

def cmdx(m=0,n=9):
    return CMD+'(?:\{.*?\}){%d,%d}'%(m,n)

CMD_='(?<!\\\\)(?:\\\\\\\\)*('+CMD+')' # (?![a-zA-Z])
CMDX_='(?<!\\\\)(?:\\\\\\\\)*('+CMDX+')'
rxCMD=re.compile(CMD_)
rxCMDX=re.compile(CMDX_)
rxNEWCMD=re.compile('\\\\[re]?newcommand\{%s}'%CMD)

ENV='\\\\begin{(?P<name>%s)}(?P<option>\[.*?\])?(?P<content>.*?)\\\\end{(?P=name)}'%WORD
rxENV=re.compile('(?<!\\\\)(?:\\\\\\\\)*'+ENV,re.DOTALL)

def rxenv(name=WORD):
    ENV='\\\\begin{(?P<name>%s)}(?P<option>\[.*?\])?(?P<content>.*?)\\\\end{(?P=name)}'%name
    return re.compile('(?<!\\\\)(?:\\\\\\\\)*'+ENV,re.DOTALL)

DOLLAR='\$.+?\$'
DDOLLAR='\$\$.*?\$\$'
rxDOLLAR=re.compile(DOLLAR,re.DOTALL)
rxDDOLLAR=re.compile(DDOLLAR,re.DOTALL)

EQUATION='\\\\\\[.*?\\\\\\]'
rxEQUATION=re.compile(EQUATION,re.DOTALL)
    
COMMENT='%.*'
rxCOMMENT=re.compile(COMMENT)

def findrx(fname,rx):
    '''fname: tex file name
'''
    with open(fname+'.tex') as fo:
        m=rx.findall(fo.read())
    return m


def findrx2(fname,rx):
    '''fname: tex file name
'''
    with open(fname+'.tex') as fo:
       ms=[(rx.findall(line), k) for k, line in enumerate(fo.readline(),1) if rx.findall(line)]
    return ms

def findcmd(fname):
    '''fname: tex file name
'''
    return findrx(fname,re.compile(CMD_))

def findcmdx(fname):
    '''fname: tex file name
'''
    return findrx(fname,re.compile(CMDX_))

def findnewcmd(fname):
    return findrx(fname, rxNEWCMD)

def findenv(fname,name=WORD):
    '''fname: tex file name
return a list of tuple (name,option,content)
'''
    return findrx(fname,rxenv(name))

def finddol(fname):
    '''fname: tex file name
'''
    return findrx(fname,rxDOLLAR)

'''
class myClass(parent):
    # myClass
    def __init__(self):
        parent.__init__(self)
        
    def method(self):
        body
'''

# test
fname='nlsms'
with open(fname+'.tex') as fo:
    for k, line in enumerate(fo.readlines(),1):
        print(line)
        m=re.compile('\\\\S(?![a-zA-Z])').findall(line)
        if m:
            print(k,m)
            x=input()
