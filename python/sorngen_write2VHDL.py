##################################################################
##
## file: sorngen_write2VHDL.py
##
## (c) 2018/2019 Moritz Bärthel
##     University of Bremen
##
##################################################################

# function write2VHDL

def write2VHDL(FctnTab,*varargs):
	""" Writes SORN function to vhdl file.
	
	Input Arguments:
		sornTable	-- object of class "sornTable" containing the input and output datatypes and SORN values
		varargs: 	'name'      -- names the file after the string defined afterwards
					'author'    -- set author to the string defined afterwards
					'info'      -- declaration will be specified as given in the
								string afterwards
	"""
	
	# import necessary packages
	import re
	import numpy as np
	from sorngen_datatypes import sornDatatype
	from sorngen_datatypes import sornInterval
	from sorngen_datatypes import sornFctnTable
	
	# read optional input parameters
	name = "unknownSORNfunction"
	author = "unknown"
	info = "not specified"
	for arg in range(0,len(varargs),2):
		if re.search(r"[nN]ame",varargs[arg]):
			name = varargs[arg+1]
		elif re.search(r"[aA]uthor",varargs[arg]):
			author = varargs[arg+1] 
		elif re.search(r"[iI]nfo",varargs[arg]):
			info = varargs[arg+1] 	
		else:
			raise Exception("Parameter <" + varargs[arg] + "> not specified!")
	
	# generate SORN function
	vhdlSTR = ""
	
	# two input function
	if FctnTab.Nin == 2:
		
		# write result string
		for digitCTR in range(0,len(FctnTab.poolOUTSORN)): # loop over bits in result
			isFirstDigit = 0
			vhdlSTR = vhdlSTR + "result(" + str(digitCTR) + ") <= "
			for op0CTR in range(0,len(FctnTab.poolIN0SORN)): # loop over values in operand 0
				hasDigitONE = 0
				for op1CTR in range(0,len(FctnTab.poolIN1SORN)): # loop over values in operand 1
					c_SORN = FctnTab.resultSORN[op0CTR][op1CTR]
					if c_SORN[digitCTR] == 1:
						if hasDigitONE == 1 or isFirstDigit == 1:
							vhdlSTR = vhdlSTR + "or "
						isFirstDigit = 1
						hasDigitONE = 1
						vhdlSTR = vhdlSTR + "(x0(" + str(op0CTR) + ") and x1(" + str(op1CTR) + ")) "
				# write end of line
				if op0CTR == len(FctnTab.poolIN0SORN)-1:
					vhdlSTR = vhdlSTR + ";\n"
					hasDigitONE = 0
		
	# one input function	
	elif FctnTab.Nin == 1:
		
		# write result string
		for digitCTR in range(0,len(FctnTab.poolOUTSORN)): # loop over bits in result
			isFirstDigit = 0
			vhdlSTR = vhdlSTR + "result(" + str(digitCTR) + ") <= "
			for op0CTR in range(0,len(FctnTab.poolIN0SORN)): # loop over values in operand 0
				hasDigitONE = 0
				c_SORN = FctnTab.resultSORN[op0CTR]
				if c_SORN[digitCTR] == 1:
					if hasDigitONE == 1 or isFirstDigit == 1:
						vhdlSTR = vhdlSTR + "or "
					isFirstDigit = 1
					hasDigitONE = 1
					vhdlSTR = vhdlSTR + "x0(" + str(op0CTR) + ") "
				# write end of line
				if op0CTR == len(FctnTab.poolIN0SORN)-1:
					if isFirstDigit == 0:
						vhdlSTR = vhdlSTR + " '0'"
					vhdlSTR = vhdlSTR + ";\n"
					hasDigitONE = 0
	
	# remove space at the end of every line (") ;" -> ");")
	vhdlSTR = re.sub(r"\)\s;", r");", vhdlSTR)
	
	# generate comments
	vhdlIN0commentSTR = ""
	vhdlIN1commentSTR = ""
	vhdlOUTcommentSTR = ""
	for poolCTR in range(0,len(FctnTab.poolIN0SORN)):
		vhdlIN0commentSTR = vhdlIN0commentSTR + "-- x0(" + str(poolCTR) + "): " + FctnTab.datatypeIN0.intervals[poolCTR].getName() + "\n"
	if FctnTab.Nin == 2:
		for poolCTR in range(0,len(FctnTab.poolIN1SORN)):
			vhdlIN1commentSTR = vhdlIN1commentSTR + "-- x1(" + str(poolCTR) + "): " + FctnTab.datatypeIN1.intervals[poolCTR].getName() + "\n"
	for poolCTR in range(0,len(FctnTab.poolOUTSORN)):
		vhdlOUTcommentSTR = vhdlOUTcommentSTR + "-- result(" + str(poolCTR) + "): " + FctnTab.datatypeOUT.intervals[poolCTR].getName() + "\n"
		
	# open and fill template
	templateSTR = open("./templates/vhdlheader_function.tpl").read() if FctnTab.Nin == 2 else open("./templates/vhdlheader_function_1op.tpl").read()
	# set filename
	templateSTR = re.sub("#filename",name+".vhd",templateSTR)
	# set author
	templateSTR = re.sub("#author",author,templateSTR)
	# set info
	templateSTR = re.sub("#info",info,templateSTR)
	# set comments
	templateSTR = re.sub("#input0comment",vhdlIN0commentSTR,templateSTR)
	templateSTR = re.sub("#input1comment",vhdlIN1commentSTR,templateSTR) if FctnTab.Nin == 2 else templateSTR
	templateSTR = re.sub("#resultcomment",vhdlOUTcommentSTR,templateSTR)
	# set entityname
	templateSTR = re.sub("#entityname",name,templateSTR)
	# set portwidths
	templateSTR = re.sub("#sizeofd0",str(len(FctnTab.poolIN0SORN)-1),templateSTR)
	templateSTR = re.sub("#sizeofd1",str(len(FctnTab.poolIN1SORN)-1),templateSTR) if FctnTab.Nin == 2 else templateSTR
	templateSTR = re.sub("#sizeofr",str(len(FctnTab.poolOUTSORN)-1),templateSTR)
	# set function
	templateSTR = re.sub("#function",vhdlSTR,templateSTR)

	# write to file
	with open("./VHDL/VHDLbasic/" + name + ".vhd", "w") as output_file:
		print(templateSTR, file=output_file)
	
# EOF write2VHDL