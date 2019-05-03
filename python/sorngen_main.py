##################################################################
##
## file: sorngen_main.py
##
## (c) 2018/2019 Jochen Rust
##     University of Bremen
##
##################################################################
 
import sys
import sorngen_global as sorn

import sorngen_datapath as dp
import sorngen_parse as parse
import sorngen_builder as builder
import sorngen_writeToFile as write
import string
import ast


print("###################################################")
print("##")
print("## SORNGEN HDL CODE GENERATOR")
print("##")
print("## (c) 2018/2019 University of Bremen")
print("##")
print("###################################################")


## 1/ read data
# 1.1/ initialize global sorngen environment
env = sorn.sornEnv()
# 1.2/ read input data
env = parse.file(env, sys.argv)

## 2/ elaborate
## 2.1/ save abstract syntax tree (AST) to  sorn syntax tree (SST)
env = parse.elaborate(env)

## 3/ generate sorn HDL data
for cValue in env.lValueDictSST:

    print("3/ *** Start of '"+cValue+"' SORN HDL file build ***")
    # 3.1/ insert register
    env.lValueDictSST[cValue] = builder.insertRegisterToSST(env.lValueDictSST[cValue], env.pipelineLocation)
    # 3.2/ set up new HDL datatype
    HDL = dp.sornHDL(cValue+"_module")
    # 3.3/ build instances
    HDL = builder.createHDLInstancesFromSST(HDL, env.lValueDictSST[cValue])
    # 3.4/ build instances
    HDL = builder.createHDLGlobalPortsFromSST(HDL, env.lValueDictSST[cValue])
    # 3.5/ build nets
    HDL = builder.createHDLNetsFromSST(HDL, env.lValueDictSST[cValue])
    HDL.show()
    # 3.6/ register HDL data to SORN environment
    env.HDL[cValue] = HDL.deepcopy()
    # 3.7/ clear local HDL datatype
    HDL.clear()
	
# 3.8/ build toplevel
env.HDL = builder.createToplevelInstance(env)


# 3.9/ build sorn components
builder.generateFunctionTable(env)

# 4/ write HDL data to file
write.writeToVHDL(env)

