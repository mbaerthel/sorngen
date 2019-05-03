##################################################################
##
## file: sorngen_writeToFile.py
##
## (c) 2018/2019 Jochen Rust
##     University of Bremen
##
#################################################################

import string
import sys
import sorngen_syntaxTree as sst

from sorngen_write2VHDL import write2VHDL


def writeEqsToVHDL(env, HDL, name, st):

    ## 1/ header: set default data
    header = string.Template(st["header"]).substitute({'version': "0.1", 'filename': name+".vhd", 'author': "n/a", 'info': "SORNGEN TOPLEVEL", 'date': "2019"})
    # write to template
    toplevel = header;

    ## 2/ entity
    inputPorts = ""
    outputPorts = ""
    # 2.1/ sequential ports
    if HDL.instances[0].nodeSST.SST.hasRegister: inputPorts = inputPorts + st['sequential_port_declarations']
    # 2.2/ extract global ports from environment
    for it in HDL.ports:
        if it.isGlobal:
            if it.isInput:
                inputPorts = inputPorts + string.Template(st["port_declaration"]).substitute({'portname': it.name, 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
            else:
                outputPorts = outputPorts + string.Template(st["port_declaration"]).substitute({'portname': it.name, 'direction': "OUT", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
                
    # cleanup
    inputPorts=inputPorts[0:-1]
    outputPorts=outputPorts[0:-2]
    # write to template
    entity =  string.Template(st["entity"]).substitute({'entityname': name, 'inputports': inputPorts, 'outputports': outputPorts});


    ## 3/ components
    hasRegister = False
    components=""
    for it in HDL.instances:
        # 3.1/ catch register component
        if it.nodeSST.type == sst.typeNode.REGISTER:
            if not hasRegister: components = components+st["register_component"]
            hasRegister = True
            continue
            
        # 3.2/ other components
        inputPorts = ""
        outputPorts = ""
        for it2 in it.ports:
                if it2.isInput:
                    inputPorts = inputPorts + string.Template(st["port_declaration"]).substitute({'portname': it2.name, 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
                else:
                    outputPorts = outputPorts + string.Template(st["port_declaration"]).substitute({'portname': it2.name, 'direction': "OUT", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
        # ports cleanup
        inputPorts=inputPorts[0:-1]
        outputPorts=outputPorts[0:-2]
        components = components+string.Template(st["component"]).substitute({'componentname': it.name, 'inputports': inputPorts, 'outputports': outputPorts});


    ## 4/ signals
    signals=""
    for it in HDL.nets:
        signals = signals + string.Template(st["signal_declaration"]).substitute({'signalname': it.name, 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
    

    ## 5/ instances
    instances=""
    for it in HDL.instances:
        # 3.1/ component ports
        ports = ""
        for it2 in it.ports:
            ports = ports + string.Template(st["port_assignment"]).substitute({'portname': it2.name, 'signalname': it2.nets[0].name})+",\n"
        # ports cleanup
        ports=ports[0:-2]
        # create instance
        if not it.nodeSST.type == sst.typeNode.REGISTER:
            instances = instances + string.Template(st["instance"]).substitute({'instancename': "i_"+it.name, 'componentname': it.name, 'portassignment': ports})+"\n"
        else:
            instances = instances + string.Template(st["register_instance"]).substitute({'instancename': "i_"+it.name, 'uppervalue': env.datatype.sornsize, 'portassignment': ports})+"\n"


    ## 6/ assignments
    assignments=""
    for it in HDL.ports:
        if it.isGlobal:
            if it.isInput:
                assignments = assignments + string.Template(st["signal_assignment"]).substitute({'signalname': it.nets[0].name, 'value': it.name})+";\n"
            else:
                assignments = assignments + string.Template(st["signal_assignment"]).substitute({'signalname': it.name, 'value': it.nets[0].name})+";\n"
    

    ## 6/ architecture
    architecture = string.Template(st["architecture"]).substitute({'behavior': "Behavior", 'archname': name, 'components': components, 'signals': signals, 'instances': instances, 'assignments': assignments})

    ## 8/ registers
    if hasRegister:
        with open('./VHDL/'+'REG.vhd', 'w') as f: 
            f.write(st['register_module'])
        f.close()

    ## 7/ toplevel
    with open('./VHDL/'+name+'.vhd', 'w') as f: 
        f.write(header+entity+architecture);
    f.close()


def writeTopToVHDL(env, HDL, name, st):

    ## 1/ header: set default data
    header = string.Template(st["header"]).substitute({'version': "0.1", 'filename': name+".vhd", 'author': "n/a", 'info': "SORNGEN TOPLEVEL", 'date': "2019"})
    # write to template
    toplevel = header;

    ## 2/ entity
    inputPorts = ""
    outputPorts = ""
    # 2.1/ sequential ports
    if env.hasRegister: inputPorts = inputPorts + st['sequential_port_declarations']
    # 2.2/ extract global ports from environment
    for it in HDL.ports:
        if it.isGlobal:
            if it.isInput:
                inputPorts = inputPorts + string.Template(st["port_declaration"]).substitute({'portname': it.name, 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
            else:
                outputPorts = outputPorts + string.Template(st["port_declaration"]).substitute({'portname': it.name, 'direction': "OUT", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
                
    # cleanup
    inputPorts=inputPorts[0:-1]
    outputPorts=outputPorts[0:-2]
    # write to template
    entity =  string.Template(st["entity"]).substitute({'entityname': name, 'inputports': inputPorts, 'outputports': outputPorts});


    ## 3/ components
    components=""
    for cValue in env.HDL:
        if env.HDL[cValue].isToplevel: continue
        inputPorts = ""
        outputPorts = ""
        # 3.1/ sequential ports
        if env.HDL[cValue].instances[0].nodeSST.SST.hasRegister: inputPorts = inputPorts + st['sequential_port_declarations']
        # 3.2/ component ports
        for cPort in env.HDL[cValue].ports:
            if not cPort.isGlobal: continue
            if cPort.isInput:
                inputPorts = inputPorts + string.Template(st["port_declaration"]).substitute({'portname': cPort.name, 'direction': "IN", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
            else:
                outputPorts = outputPorts + string.Template(st["port_declaration"]).substitute({'portname': cPort.name, 'direction': "OUT", 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
        # ports cleanup
        inputPorts=inputPorts[0:-1]
        outputPorts=outputPorts[0:-2]
        components = components+string.Template(st["component"]).substitute({'componentname': env.HDL[cValue].name, 'inputports': inputPorts, 'outputports': outputPorts});


    ## 4/ signals
    signals=""
    for it in HDL.nets:
        signals = signals + string.Template(st["signal_declaration"]).substitute({'signalname': it.name, 'uppervalue': env.datatype.sornsize-1,'lowervalue': 0 })+";\n"
    

    ## 5/ instances
    instances=""
    for cValue in env.HDL:
        if env.HDL[cValue].isToplevel: continue
        ports = ""
        # 5.1/ sequential ports
        if env.HDL[cValue].instances[0].nodeSST.SST.hasRegister: ports = ports + st['sequential_port_assignments']
        # 5.2/ component ports
        for cPort in env.HDL[cValue].ports:
            if not cPort.isGlobal: continue
            ports = ports + string.Template(st["port_assignment"]).substitute({'portname': cPort.name, 'signalname': cPort.name})+",\n"
        # ports cleanup
        ports=ports[0:-2]
        # create instance
        instances = instances + string.Template(st["instance"]).substitute({'instancename': "i_"+cValue, 'componentname': env.HDL[cValue].name, 'portassignment': ports})+"\n"

  
    ## 6/ architecture
    architecture = string.Template(st["architecture"]).substitute({'behavior': "Behavior", 'archname': name, 'components': components, 'signals': signals, 'instances': instances, 'assignments': "-- none"})

    ## 7/ toplevel
    with open('./VHDL/'+name+'.vhd', 'w') as f: 
        f.write(header+entity+architecture);
    f.close()



def writeToVHDL(env):
    # 1./ load templates
    st = loadVHDLTemplates()
    # 2./ generate VHDL instances for each equation
    for lValueDictHDL in env.HDL:
        if env.HDL[lValueDictHDL].isToplevel:
            writeTopToVHDL(env, env.HDL[lValueDictHDL], env.HDL[lValueDictHDL].name, st)
        else:
            writeEqsToVHDL(env, env.HDL[lValueDictHDL], env.HDL[lValueDictHDL].name, st)
		
			# 3./ generate vhdl files for basic operations
            for cInst in env.HDL[lValueDictHDL].instances:
                if cInst.nodeSST.type == sst.typeNode.REGISTER: continue
                write2VHDL(cInst.FctnTable,'name',cInst.FctnTable.name)


def loadVHDLTemplates():
    st = {}
    with open('templates/template_VHDL_entity.stpy', 'r') as f: 
        st["entity"] = f.read()
    f.close()
    with open('templates/template_VHDL_component.stpy', 'r') as f: 
        st["component"] = f.read()
    f.close()
    with open('templates/template_VHDL_architecture.stpy', 'r') as f: 
        st["architecture"] = f.read()
    f.close()
    with open('templates/template_VHDL_header.stpy', 'r') as f: 
        st["header"] = f.read()
    f.close()
    with open('templates/template_VHDL_instance.stpy', 'r') as f: 
        st["instance"] = f.read()
    f.close()
    with open('templates/template_VHDL_port_declaration.stpy', 'r') as f: 
        st["port_declaration"] = f.read()
    f.close()
    with open('templates/template_VHDL_port_assignment.stpy', 'r') as f: 
        st["port_assignment"] = f.read()
    f.close()
    with open('templates/template_VHDL_signal_declaration.stpy', 'r') as f: 
        st["signal_declaration"] = f.read()
    f.close()
    with open('templates/template_VHDL_signal_assignment.stpy', 'r') as f: 
        st["signal_assignment"] = f.read()
    f.close()
    with open('templates/template_VHDL_register_module.stpy', 'r') as f: 
        st["register_module"] = f.read()
    f.close()
    with open('templates/template_VHDL_register_instance.stpy', 'r') as f: 
        st["register_instance"] = f.read()
    f.close()
    with open('templates/template_VHDL_register_component.stpy', 'r') as f: 
        st["register_component"] = f.read()
    f.close()
    with open('templates/template_VHDL_sequential_port_declarations.stpy', 'r') as f: 
        st["sequential_port_declarations"] = f.read()
    f.close()
    with open('templates/template_VHDL_sequential_port_assignments.stpy', 'r') as f: 
        st["sequential_port_assignments"] = f.read()
    f.close()
    return st
