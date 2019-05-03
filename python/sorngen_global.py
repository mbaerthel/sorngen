##################################################################
##
## file: sorngen_global.py
##
## (c) 2018/2019 Jochen Rust
##     University of Bremen
##
##################################################################

import ast
import re

class sornEnv:

  env      = "n/a"
  name      = "n/a"
  datatype  = "n/a"
  HDL = {}
  lValueDictAST = {}
  lValueDictSST = {}
  dictNodeIter = {}
  maxDepth = 0
  hasRegister  = False


  def getNodeName(self,name):
    if not (name in self.dictNodeIter):
      self.dictNodeIter[name] = 0  
    else:
      self.dictNodeIter[name] += 1
    return name+str(self.dictNodeIter[name])


def getOpAST(AST):
  
  ## 0/ default assignments
  strOP = ""
  strFunc = ""

  ## 1/ set up initial operand namings and functions
  if type(AST.op) is ast.Add:
    strOP = "ADD"
    strFunc = "<op0> + <op1>"
  elif type(AST.op) is ast.Sub:
    strOP = "SUB"
    strFunc = "<op0> - <op1>"
  elif type(AST.op) is ast.Div:
    strOP = "DIV"
    strFunc = "<op0> / <op1>"
  elif type(AST.op) is ast.Mult:
    strOP = "MUL"
    strFunc = "<op0> * <op1>"
  elif type(AST.op) is ast.Mod:
    strOP = "MOD"
    strFunc = "<op0> % <op1>"
  elif type(AST.op) is ast.Pow:
    strOP = "POW"
    strFunc = "<op0> ** <op1>"
  

  ## 2/ replace with numeric (if specified)
  if (type(AST.left) is ast.Num):
    strFunc= re.sub('<op0>', str(AST.left.n), strFunc)
  else:
    strFunc= re.sub('<op0>', '<op>', strFunc)

  if (type(AST.right) is ast.Num):
    strFunc= re.sub('<op1>', str(AST.right.n), strFunc)
    
  else:
    strFunc= re.sub('<op1>', '<op>', strFunc)

  return strOP, strFunc


def getFuncAST(ast):

  strFunc = ast.id+"( <op> ) "

  return strFunc
