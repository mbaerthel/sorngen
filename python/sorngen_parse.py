##################################################################
##
## file: sorngen_parse.py
##
## (c) 2018/2019 Jochen Rust
##     University of Bremen
##
##################################################################

## import packages
import ast
import re
import math
import sys

import sorngen_error as error
import sorngen_syntaxTree as sst
import sorngen_global as sorn
from sorngen_defineSORN import defineSORN

def elaborate(env):

    print("2/ Elaborate...")
    print("INFO: Converting AST to SST...")
    # 1/ convert AST to SST (sorn syntax tree)
    lValueDictSST = {}
    for node in env.lValueDictAST:
        SST = extractSST(env, env.lValueDictAST[node])
        env.lValueDictSST[node] = SST
        print(" "+str(len(SST.listNode))+" node(s) found")
       #SST.show()

    
    # 2/ mark internal connections within the SST
    print("INFO: Searching for internal connections...", end="")
    icCTR, env = markInternalConnections(env, env.lValueDictSST)
    print(" "+str(icCTR)+" internal connection(s) found")
    for nameSST in env.lValueDictSST:
        print("******************* "+nameSST+" *****************")
        env.lValueDictSST[nameSST].show()
        print("*******************")

    print("INFO: Locating register...", end="")
    env = locateRegister(env, env.lValueDictSST)
    print(" "+str(len(env.pipelineLocation))+" pipeline stages found")

    return env


## function parse SORN file
def file(env, argv):
    ## 0/ default assignments
    # 0.1/ local AST tree
    treeAST = []
    # 0.2/ local dictionary id -> AST node
    dictIdAST={}
    # 0.3/ global pipeline list
    env.pipeline = []

    ## 1/ global input data hanlding
    print("1/ Parsing equations...")
    # 1.0/ catch invalid number of input arguments
    if not len(argv) == 2: error.message(error.ID.INPUT_ARGS, argv)
    filename = argv[1]
    # 1.1/ read from the specified file (catch exceptions)
    try:
        with open(filename, 'r') as f: 
            lines = f.readlines()
        f.close()
    except:
        error.message(error.ID.FILE_NOT_FOUND,filename)

    ## 2/ read config data from file
    for cLine in lines:
        cRegex=re.match('@(.*) (.*)',cLine,re.I)
        if not cRegex: continue
        # 2.3/ get name
        if re.match('name',cRegex.group(1),re.I):
            env.name = cRegex.group(2)
            print("INFO: name: '"+env.name+"'")
		# 2.4a/ get datatype
        elif re.match('datatype',cRegex.group(1),re.I):
            datatypeInputs = eval(cRegex.group(2))
            if len(datatypeInputs) == 5:
                env.datatype = defineSORN(datatypeInputs[0],datatypeInputs[1],datatypeInputs[2],datatypeInputs[3],datatypeInputs[4])
            elif len(datatypeInputs) == 4:
                env.datatype = defineSORN(datatypeInputs[0],datatypeInputs[1],datatypeInputs[2],datatypeInputs[3])
            elif len(datatypeInputs) == 3:
                env.datatype = defineSORN(datatypeInputs[0],datatypeInputs[1],datatypeInputs[2])
            else:
                env.datatype = defineSORN(datatypeInputs[0],datatypeInputs[1])
            print("INFO: SORNsize: " + str(env.datatype.sornsize))
            print("INFO: datatype: ",end="")
            env.datatype.showIV()		
        # 2.4b/ get pipeline configuration
        elif re.match('Pipeline',cRegex.group(1),re.I):
            pipeline = cRegex.group(2)
            # 2.4.1/ neglect invalid pipeline statement
            if not ((isinstance(eval(pipeline),list)) or (isinstance(eval(pipeline),int))): continue
            env.pipeline = eval(pipeline)
            print("INFO: pipeline configuration: "+pipeline)
        # 2.4 catch unknown config data
        else:
            error.message(error.ID.UNKNOWN_CONFIG_DATA, cRegex.group())

    ## 3/ read equations and store as abstract syntax tree (AST)
    for cLine in lines:
        # 3.1/ neglect invalid inputs
        cRegex=re.match('.',cLine,re.I)
        if not cRegex : continue
        if (not cRegex.group()) or (cRegex.group()=='@') or (cRegex.group()=='#'): continue
        # 3.2/ match input
        cRegex=re.match('(.*)',cLine,re.I)
        # 3.3/ write to AST
        treeAST.append(ast.parse(cRegex.group()))
        print("INFO: parsing equation: "+cRegex.group())
        # 3.4 set up new dict (id -> ast)
        for node in ast.walk(treeAST[-1]):
            if isinstance(node, ast.Assign):
                dictIdAST[node.targets[0].id] = node
    # 3.5/ register dict to env (catch exceptions)
    if (dictIdAST == {}): error.message(error.ID.NO_EQUATIONS_FOUND, filename)
    env.lValueDictAST = dictIdAST
    return env


## function extractSST: AST -> SST
def extractSST(env, AST):

    ## 0/ default assignments
    # 0.1/ initialize new sorn syntax tree (SST)
    SST = sst.sornSyntaxTree(env)
    # 0.2/ register SST to sorn environment
    env.SST = SST
    # 0.3/ initialize AST id dict
    dictIdAST = {}

    # 1/ iterate through ast nodes
    for node in ast.walk(AST):

        # 1.1/ assignment
        if isinstance(node, ast.Assign):

            root=sst.sornSyntaxTreeNode(SST)
            # 1.1.1/ set up sorn syntax tree node
            root.operand = ast.Assign
            root.setAST(node.targets[0])
            root.depthLocal = -1
            root.name = node.targets[0].id
            root.type = sst.typeNode.VARIABLE 
            root.parent = None
            root.isRoot = True
            SST.rootNode = root
            dictIdAST[id(node.targets[0])] = root
            # 1.1.2/ update SST dictionaries and lists
            SST.listNode.append(root)
            SST.dictDepthNode[root.depth] = root 
            SST.dictNameNode[root.name] = root 
            
            # 1.3.1/ append sibling nodes for value
            sNode0=sst.sornSyntaxTreeNode(SST)
            sNode0.setAST(node.value)
            sNode0.depthLocal = 0
            sNode0.parent = root
            root.siblings.append(sNode0)
            # 1.3.2/ update AST dict
            dictIdAST[id(node.value)] = sNode0
            # 1.3.3/ register node to SST
            if not isinstance(node.value, ast.Call):
                SST.listNode.append(sNode0)
                SST.dictDepthNode[sNode0.depthLocal] = sNode0
                SST.dictNameNode[sNode0.name] = sNode0

        # 2/ BinOp
        if isinstance(node, ast.BinOp):
            # 2.1/ get current node from AST id list
            cNode= dictIdAST[id(node)]
            # 2.2 set current tree depth
            cDepth = cNode.depthLocal + 1
            SST.maxDepthLocal = cDepth if cDepth > SST.maxDepthLocal else SST.maxDepthLocal

            # 2.3.1./ set up new sorn syntax tree sibling node
            sNode0=sst.sornSyntaxTreeNode(SST)
            sNode0.setAST(node.left)
            sNode0.depthLocal = cDepth
            sNode0.parent = cNode
            cNode.siblings.append(sNode0)
            # 2.3.2./ append to id list
            dictIdAST[id(node.left)] = sNode0
            # 2.3.3/ register node to SST
            if not isinstance(node.left, ast.Call):
                SST.listNode.append(sNode0)
                SST.dictDepthNode[sNode0.depthLocal] = sNode0
                SST.dictNameNode[sNode0.name] = sNode0

            # 2.4.1./ set up new sorn syntax tree sibling node
            sNode1=sst.sornSyntaxTreeNode(SST)
            sNode1.setAST(node.right)
            sNode1.depthLocal = cDepth
            sNode1.parent = cNode
            cNode.siblings.append(sNode1)
            # 2.4.2./ append to id list
            dictIdAST[id(node.right)] = sNode1
            # 2.4.3/ register node to SST
            if not isinstance(node.right, ast.Call):
                SST.listNode.append(sNode1)
                SST.dictDepthNode[sNode1.depthLocal] = sNode1
                SST.dictNameNode[sNode1.name] = sNode1

        # 3/ function calls
        if isinstance(node, ast.Call):
            # 3.1/ get current node from AST id list
            cNode= dictIdAST[id(node)]
            # 3.2/ set current tree depth
            cDepth = cNode.depthLocal + 1
            SST.maxDepthLocal = cDepth if cDepth > SST.maxDepthLocal else SST.maxDepthLocal
            # 3.3.1/ set up new sorn syntax tree sibling node
            sNode0=sst.sornSyntaxTreeNode(SST)
            sNode0.setAST(node.args[0])
            sNode0.depthLocal = cDepth+1
            cNode.siblings.append(sNode0)
            # 3.3.2/ append to id list
            dictIdAST[id(node.args[0])] = sNode0
            # 3.3.3/ register node to SST
            if not isinstance(node.args[0], ast.Call):
                SST.listNode.append(sNode0)
                SST.dictDepthNode[sNode0.depthLocal] = sNode0
                SST.dictNameNode[sNode0.name] = sNode0

            # 3.4.1/ set up new sorn syntax tree sibling node
            sNode1=sst.sornSyntaxTreeNode(SST)
            sNode1.setAST(node.func)
            # Note: SST type must be set manually to function call 
            sNode1.type = sst.typeNode.FUNCTION
            sNode1.name = env.getNodeName(node.func.id)
            sNode1.function = sorn.getFuncAST(node.func)
            #
            sNode1.depthLocal = cDepth
            sNode1.parent = cNode.parent
            sNode1.siblings.append(sNode0)
            sNode0.parent = sNode1
            cNode = sNode1
            # 3.4.2/ append to id list
            dictIdAST[id(node.func)] = sNode1
            # 3.4.3/ register node to SST
            if not isinstance(node.func, ast.Call):
                SST.listNode.append(sNode1)
                SST.dictDepthNode[sNode1.depthLocal] = sNode1
                SST.dictNameNode[sNode1.name] = sNode1

        # 4/ Name
        if isinstance(node, ast.Name) or isinstance(node, ast.Num):
            cNode= dictIdAST[id(node)]

    # wtf?
    SST.maxAddDepth = SST.maxDepthLocal
    SST.maxDepth = SST.maxDepthLocal
    return SST


## function markInternalConnections: get internal connections
def markInternalConnections(env, lValueDictSST):

    ## 0/ default assignments
    lValues = []
    icCTR = 0
    ## 1/ extract and store lValues
    for lValue in lValueDictSST: 
        lValues.append(lValue)
    
    ## 2/ find rValues
    # 2.1/ traverse through list of nodes of each stored SST
    for lValue in lValueDictSST: 
        for nodeSST in lValueDictSST[lValue].listNode:
            # 2.2/ skip root nodes (self-references)
            if (nodeSST.isRoot): continue
            # 2.2.1 increase internal connection counter
            if ((nodeSST.type == sst.typeNode.VARIABLE) and (nodeSST.name in lValues)):
                # 2.3.1/ mark current node as internally conencted
                icCTR += 1
                nodeSST.hasInternalConnection = True
                # 2.3.2/ register this internally conencted node to SST
                lValueDictSST[lValue].listInternalConnection.append(nodeSST)
                lValueDictSST[lValue].listNameInternalConnection.append(nodeSST.name)


    ## 3/ set global depth of nodes
    # 3.1/ get number of sub-trees (NoT)
    NoT = len(lValueDictSST)
    cNoT = 0
    # 3.2/ iterate through list of trees
    rNameNodeList = [];
    rNameNodeDict = {};
    orderedNameNodeList = [];
    isTouched = True
    for lValue in lValueDictSST: 
        # 3.4.1/ set up list of roots
        rNameNodeList.append(lValueDictSST[lValue].rootNode.name)
        rNameNodeDict[lValueDictSST[lValue].rootNode.name] = lValueDictSST[lValue].rootNode
    while (cNoT < NoT):
        # 3.3/ estimate processing order of all SSTs
        if not isTouched:
            print("ERROR found a loop in the syntax tree... EXITING")
            sys.exit(0)

        isTouched = False
        # 3.4/ estimate processing order of all SSTs
        cIcNameNodeList = [];
        for cNameRoot in rNameNodeList: 
            # 3.4.2/ set up list of internal connections
            for cNodeIc in lValueDictSST[cNameRoot].listNameInternalConnection:
                if cNodeIc == []: continue
                cIcNameNodeList.append(cNodeIc)
        # 3.5/ check dependencies of roots vs internal connections
        for it in rNameNodeList:
            # 3.5.1/ skip current root node if it is internally connected
            if cIcNameNodeList.count(it) > 0: continue
            # 3.5.2/ else add entry to processing order list
            orderedNameNodeList.append(it)
            # 3.5.3/ remove entry from nodeList
            rNameNodeList.remove(it)
            # 3.5.4/ mark processing
            isTouched = True
            cNoT = cNoT+1
            # 3.5.5/ continue processing
            break

        
    # 3.6/ set maximum depths
    for cRootName in orderedNameNodeList:
        cMaxDepth = 0
        # 3.6.1/ iterate through internal connection lists
#        print("Traversing: "+cRootName)
        for lValue in lValueDictSST: 
            icNameList = []
            for cNode in lValueDictSST[lValue].listInternalConnection:
                icNameList.append(cNode.name)
            
            # 3.6.1.1/ skip current root node if is is internally connected
#            print(icNameList)
#            print(cRootName)
            if icNameList.count(cRootName) == 0: continue
            # 3.6.1.2/ else set new current depth addend
#            print("Found a node")
            cMaxDepth = lValueDictSST[lValue].maxDepth if (cMaxDepth < lValueDictSST[lValue].maxDepthLocal) else cMaxDepth 

        # 3.6.2/ add depth to current SST
        rNameNodeDict[cRootName].SST.maxDepth = rNameNodeDict[cRootName].SST.maxDepth + cMaxDepth
        # 3.6.3/ add depth to all nodes of SST
        for cNode in rNameNodeDict[cRootName].SST.listNode:
            cNode.depth = cNode.depthLocal + cMaxDepth
    return icCTR, env


    ## 4/ increase depths of nodes
    for lValue in lValueDictSST: 
        # 3.1/ skip unconnected SSTs
        if not (lValueDictSST[lValue].listInternalConnection == []):
            # 3.2/ get depth of internally connected sub-SST
            addDepth = lValueDictSST[lValue].maxDepth
            # 3.3/ modify depth
            for nodeIcSST in lValueDictSST[lValue].listInternalConnection:
                # 3.3.1/ get name
                rValue = nodeIcSST.name
                SST = lValueDictSST[rValue]
                # 3.3.2/ skip if max depth does not increase
                if not (SST.maxDepth + addDepth > SST.maxAddDepth): continue
                # 3.3.3/ modify maximum additive depth
                SST.maxAddDepth = SST.maxDepth + addDepth
                # 3.3.2/ traverse through rValue sub-SST
                for nodeSST in SST.listNode:
                    # 3.3.3/ modifiy depth
                    nodeSST.depth = nodeSST.depth + addDepth
    ## 4/ return values
    return icCTR, env

## function markInternalConnections: get internal connections
def locateRegister(env, lValueDictSST):

    ## 0/ default assignments
    maxDepth = env.maxDepth-1
    pipelineLocation = []
    lValues = []
    ## 1/ extract data
    # 1.1/ extract lValue list
    for lValue in lValueDictSST: 
        lValues.append(lValue)
    # 1.2/ extract maximum depth
    for lValue in lValues: 
        maxDepth = lValueDictSST[lValue].maxDepth if lValueDictSST[lValue].maxDepth > maxDepth else maxDepth
    ## 2/ handle pipeline divider
    if isinstance(env.pipeline, int):
        if env.pipeline >= maxDepth:
            for it in range(maxDepth,0,-1): pipelineLocation.append(it)
        if env.pipeline > 0 and env.pipeline < maxDepth:
            pipeStep = maxDepth/(env.pipeline+1)
            pipeCTR = pipeStep;
            while pipeCTR < maxDepth:
                if not math.ceil(maxDepth-pipeCTR) in pipelineLocation:
                    pipelineLocation.append(math.ceil(maxDepth-pipeCTR))
                    pipeCTR +=pipeStep
    ## 3/ handle fixed position of pipelines
    else:
        for cValue in env.pipeline:
            if cValue in range(maxDepth,0,-1): pipelineLocation.append(maxDepth-cValue+1)
            
    env.pipelineLocation = pipelineLocation

    ## 4/ mark global output
    for lValue in lValues:
        for nodeSST in lValueDictSST[lValue].listNode:
            if isinstance(nodeSST.ast, ast.Assign):
                # 3.1/ get sibling
                nodeSST.siblings[0].isGlobalOutput = True

    return env


