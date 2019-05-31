##################################################################
##
## file: sorngen_builder.py
##
## (c) 2018/2019 Jochen Rust
##     University of Bremen
##
##################################################################
 
import parser
import ast
import sorngen_datapath as dp
import sorngen_syntaxTree as sst

import sys


def insertRegisterToSST(SST, registerLocation):

    # 0/ default assignments
    rCTR = 0

    print("INFO: Adding pipeline register to SST...",end="")
    for cNode in SST.listNode:
        if not ((cNode.type == sst.typeNode.BINOP) or (cNode.type == sst.typeNode.FUNCTION)): continue
        if cNode.depth in registerLocation:
            # 1.1/ create new register node
            rNode=sst.sornSyntaxTreeNode(SST)
            rNode.type = sst.typeNode.REGISTER
            SST.hasRegister = True
            SST.env.hasRegister = True
            rNode.name = SST.env.getNodeName("REG")
            rNode.depth = cNode.depth
            rNode.siblings= [cNode]
            rNode.parent = cNode.parent
            # 1.2/ modify parent node
            pNode = cNode.parent
            if id(pNode.siblings[0]) == id(cNode):
                pNode.siblings[0] = rNode
            else:
                pNode.siblings[1] = rNode
            # 1.3/ modify current node
            cNode.parent = rNode
            # 1.4/ register new node to SST
            SST.listNode.append(rNode)
            SST.dictNameNode[rNode.name] = rNode
            rCTR += 1

    print("INFO: "+str(rCTR)+" register(s) added")

    return SST

def createHDLGlobalPortsFromSST(HDL,SST):

    # 0/ default assignments
    iCTR = 0
    oCTR = 0

    ## 1/ walk the SST to create intances
    print("INFO: Creating global ports from SST...",end="")
    for cNode in SST.listNode:
        
        # 1.1/ input ports 
        if cNode.type == sst.typeNode.VARIABLE:
            newPort =dp.sornPort(HDL)
            newPort.name = cNode.name
            if not cNode.islValue:
                iCTR += 1
                newPort.isInput = True
            else:
                oCTR += 1
            newPort.isGlobal = True

    print("INFO: "+str(iCTR)+" input and "+str(oCTR)+" output global port(s) found")

    return HDL

def createHDLInstancesFromSST(HDL,SST):
    
    ## 1/ walk the SST to create intances
    print("creating sorn instances from SST...",end="")
    for cNode in SST.listNode:
        
        # 1.1/ binary operator
        if cNode.type == sst.typeNode.BINOP:

            # 1.1.1/ create and configure new i/0 ports
            newInputPort0 = dp.sornPort(HDL)
            newInputPort0.isInput = True
            newInputPort0.name = "input0"

            if not (cNode.siblings[0].type == sst.typeNode.NUMERIC or cNode.siblings[1].type == sst.typeNode.NUMERIC):
                newInputPort1  = dp.sornPort(HDL)
                newInputPort1.isInput = True
                newInputPort1.name  = "input1"

            newOutputPort = dp.sornPort(HDL)
            newOutputPort.name = "output0"

            # 1.1.2/ create and configure new instance
            cInst = dp.sornInstance(HDL, cNode.name, cNode.function, [])
            cInst.nodeSST = cNode
            cInst.depth = cNode.depth
            cNode.instHDL = cInst
            # 1.1.4/ register instance to ports and vice versa
            dp.register(newInputPort0, cInst)
            if not (cNode.siblings[0].type == sst.typeNode.NUMERIC or cNode.siblings[1].type == sst.typeNode.NUMERIC):
                dp.register(newInputPort1, cInst)
            dp.register(newOutputPort, cInst)

        # 1.2/ (function) call
        if cNode.type == sst.typeNode.FUNCTION:
            # 1.2.1/ create and configure new i/0 ports
            newInputPort  = dp.sornPort(HDL)
            newInputPort.isInput = True
            newInputPort.name = "input0"

            newOutputPort = dp.sornPort(HDL)
            newOutputPort.name = "output0"

            # 1.2.2/ create and configure new instance
            cInst = dp.sornInstance(HDL, cNode.name, cNode.function, [])
            cInst.nodeSST = cNode
            cInst.depth = cNode.depth
            cNode.instHDL = cInst
            # 1.2.3/ register instance to ports and vice versa
            dp.register(newInputPort, cInst)
            dp.register(newOutputPort, cInst)

        # 1.3/ pipeline register
        if cNode.type == sst.typeNode.REGISTER:
            # 1.3.1/ create and configure new i/0 ports
            newInputPort  = dp.sornPort(HDL)
            newInputPort.isInput = True
            newInputPort.name = "input0"

            newOutputPort = dp.sornPort(HDL)
            newOutputPort.name = "output0"

            # 1.3.2/ create and configure new instance
            cInst = dp.sornInstance(HDL, cNode.name, [], [])
            cInst.nodeSST = cNode
            cInst.depth = cNode.depth
            cNode.instHDL = cInst
            cInst.isRegister = True
            # 1.3.3/ register instance to ports and vice versa
            dp.register(newInputPort, cInst)
            dp.register(newOutputPort, cInst)


    print(str(len(HDL.instances))+" instance(s) in total")
    
    return HDL


def createHDLNetsFromSST(HDL, SST):

    print("creating nets...",end="")
    for cInst in HDL.instances:
        # get corresponding SST node
        cNode = cInst.nodeSST
        # 1/ binary operator
        if cNode.type == sst.typeNode.BINOP:
            
            # 0/ port counter, handles different occurances of numeric values
            pCTR = 0

            # 1/ get sibling instances of actual node
            if not (cNode.siblings[0].type == sst.typeNode.NUMERIC):
                lNode = cNode.siblings[0]
                lInst = lNode.instHDL
                newNetLeft = dp.sornNet(HDL,lNode.name+"_to_"+cInst.name)
                dp.register(newNetLeft, cInst.ports[pCTR])
                pCTR += 1
                # assign to instance of output port
                # 1.1/ local ports
                if not (lNode.type == sst.typeNode.VARIABLE):
                    for it in lInst.ports:
                        if not it.isInput:
                            dp.register(newNetLeft, it)
                # 1.2/ global ports
                else:
                    # iterate through global ports and compare name
                    for it in HDL.ports:
                        if not it.isGlobal: continue
                        if (it.name == lNode.name):
                            dp.register(newNetLeft, it)

            if not (cNode.siblings[1].type == sst.typeNode.NUMERIC):
                rNode = cNode.siblings[1]
                rInst = rNode.instHDL
                newNetRight = dp.sornNet(HDL,rNode.name+"_to_"+cInst.name)
                dp.register(newNetRight, cInst.ports[pCTR])
                # assign to instance of output port
                if not (rNode.type == sst.typeNode.VARIABLE):
                    for it in rInst.ports:
                        if not it.isInput:
                            dp.register(newNetRight, it)
                else:
                    # iterate through global ports and compare name
                    for it in HDL.ports:
                        if not it.isGlobal: continue
                        if (it.name == rNode.name):
                            dp.register(newNetRight, it)
            
        ## 2/ (function) calls
        if (cNode.type == sst.typeNode.FUNCTION) or (cNode.type == sst.typeNode.REGISTER):

            # 1/ get sibling instances of actual node
            sNode = cNode.siblings[0]
            sInst = sNode.instHDL
            newNet = dp.sornNet(HDL, sNode.name+"_to_"+cInst.name)
            dp.register(newNet, cInst.ports[0])

            # assign to instance of output port
            if sNode.type == sst.typeNode.VARIABLE: continue
            for it in sInst.ports:
                if not it.isInput:
                    dp.register(newNet, it)
            else:
                # iterate through global ports and compare name
                for it in HDL.ports:
                    if not it.isGlobal: continue
                    if (it.name == sNode.name):
                        dp.register(newNet, it)

        ## 3/ connect global outputs
        if cNode.parent.isRoot:
            
            newNet = dp.sornNet(HDL, cNode.name+"_to_"+cNode.SST.lValue.name)
            for it in cInst.ports:
                if not it.isInput:
                    dp.register(newNet, it)
            # iterate through global ports and compare name
            for it in HDL.ports:
                if not it.isGlobal: continue
                if (it.name == cNode.SST.lValue.name):
                    dp.register(newNet, it)


    print(str(len(HDL.nets))+" net(s) in total")
    
    return HDL


def createToplevelInstance(env):

    # 1/ default assignments and preliminaries
    cPortNameDict = {}
    print("creating toplevel instance...",end="")
    HDL = dp.sornHDL(env.name)
    HDL.isToplevel = True
    print(env.name)
    # 2/ get input and output lists
    for cValue in env.HDL:
        for cPort in env.HDL[cValue].ports:
            if cPort.isGlobal:
                if not cPort.name in cPortNameDict:
                    cPortNameDict[cPort.name] = [cPort]
                else:
                    cPortNameDict[cPort.name].append(cPort)
    # 3/ get internally connected ports
    for cName in cPortNameDict:
        equalDirection = True
        cDirection = cPortNameDict[cName][0].isInput
        for cNode in cPortNameDict[cName]:
            if not (cNode.isInput == cDirection): equalDirection = False
        if equalDirection:
            cPortNameDict[cName] = [cPortNameDict[cName][0]]
    # 4/ set up ports
    for cName in cPortNameDict:
            if len(cPortNameDict[cName]) == 1:
                newPort = dp.sornPort(HDL)
                newPort.name = cName
                newPort.isGlobal = True;
                newPort.isInput = cPortNameDict[cName][0].isInput;
            else:
                newNet = dp.sornNet(HDL,cName)
    print("DONE! ")
    print(str(len(HDL.nets))+" net(s) in total")
    env.HDL[env.name] = HDL
    return env.HDL
            
def generateFunctionTable(env):
    
    from sorngen_genFctnSORN import genFctnSORN
    import re

    for cHDL in env.HDL:
        for cInst in env.HDL[cHDL].instances:
            if cInst.nodeSST.type == sst.typeNode.REGISTER: continue
            # determine the kind of operation (one or two operands)
            if len(re.findall(r"<op\d*>",cInst.function)) == 2: 
                OP = re.findall(r"\s.*\s",cInst.function)
                cInst.FctnTable = genFctnSORN(OP[0],env.datatype,env.datatype,env.datatype)
            elif len(re.findall(r"<op\d*>",cInst.function)) == 1:
                # search for operation with keyword such as "sqrt" or "log" or "log2"
                if re.search(r"[a-zA-Z]+\d*\(\s*<op>\s*\)",cInst.function):
                    OP = re.findall(r"[a-zA-z]+\d*(?=\(\s*<op\d*>\s*\))",cInst.function)
                else:
                    OP = re.findall(r"(?<=<op>\s).*",cInst.function)
                cInst.FctnTable = genFctnSORN(OP[0],env.datatype,env.datatype)
            else:
                raise Exception(" ERROR: more than 2 inputs for genFctnSORN are not implemented!")
			
            cInst.FctnTable.name = cInst.name
	

