##################################################################
##
## file: sorngen_global.py
##
## (c) 2018/2019 Jochen Rust
##     University of Bremen
##
##################################################################

import ast
import sorngen_global as sorn

class sornSyntaxTree:

  def __init__(self, env):
    self.maxDepth      = 0
    self.maxAddDepth   = 0
    self.root          = None
    self.lValue        = None
    self.name          = ""
    self.dictDepthNode = {}
    self.listNode      = []
    self.dictIdNode    = {}
    self.dictNameNode  = {}
    self.dictNodeIter  = {}
    self.hasRegister  = False
    self.env  = env
    self.listInternalConnection  = []

  def show(self):
    for nodeSST in self.listNode:
      print("Name: '"+str(nodeSST.name)+"', \t parent: [",end="")
      if not (nodeSST.parent is None):
        print("'"+nodeSST.parent.name+"'",end="")
      print("], \t siblings: [",end="")
      for nodeSibling in nodeSST.siblings:
        print("'"+nodeSibling.name+"', ",end="")
      print("], \t depth:",nodeSST.depth,end="")
      if not (nodeSST.function ==""):
        print(", \t function: "+str(nodeSST.function), end="")
      if nodeSST.islValue:
        print(" (LVALUE)")
      elif nodeSST.isRoot:
        print(" (ROOT)")
      else:
        print("")

 
class sornSyntaxTreeNode:

  def __init__(self, SST):
    self.SST                = SST
    self.instHDL            = None
    self.name               = ""
    self.function           = ""
    self.depth              = 0
    self.siblings           = []
    self.parent             = None
    self.isRoot             = False
    self.islValue           = False
    self.hasInternalConnection = False
    self.isRegister         = False
    self.ast                = None
    self.type               = None

  def setAST(self, nodeAST):
    self.ast = nodeAST
    if isinstance(nodeAST, ast.BinOp):
      self.type = typeNode.BINOP 
      self.operand = sorn.getOpAST(nodeAST)
      self.name = self.SST.env.getNodeName(sorn.getOpAST(nodeAST)[0])
      self.function = sorn.getOpAST(nodeAST)[1]
    elif isinstance(nodeAST, ast.Name):
      self.type = typeNode.VARIABLE 
      self.name = nodeAST.id
    elif isinstance(nodeAST, ast.Call):
      self.type = typeNode.CALL
      self.name = "@call"
    elif isinstance(nodeAST, ast.Num):
      self.type = typeNode.NUMERIC
      self.name = str(nodeAST.n)



class typeNode():

  BINOP = 0
  UNOP = 1
  FUNCTION = 2
  NUMERIC = 3
  CALL = 4
  VARIABLE = 5
  REGISTER = 6
