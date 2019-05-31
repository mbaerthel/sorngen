##################################################################
##
## file: sorngen_error.py
##
## (c) 2018/2019 Jochen Rust
##     University of Bremen
##
##################################################################

import sys

class ID():
    INPUT_ARGS          = 0
    FILE_NOT_FOUND      = 1
    NO_EQUATIONS_FOUND  = 2
    UNKNOWN_CONFIG_DATA = 3
    
def message(msg, data):
    print("ERROR("+str(msg)+"): ",end="")
    if (msg==ID.INPUT_ARGS):
        print("Invalid number of arguments: "+str(data[1:]))
    elif (msg==ID.FILE_NOT_FOUND):
        print("Input file '"+data+"' not found")
    elif (msg==ID.NO_EQUATIONS_FOUND):
        print("No input data found in file '"+data+"'")
    elif (msg==ID.UNKNOWN_CONFIG_DATA):
        print("Instruction '"+data+"' is unknown")
    
    print("sorngen halted with error(s)")
    sys.exit(2)



