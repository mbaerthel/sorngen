##################################################################
##
## file: sorngen_genFctnSORN.py
##
## (c) 2018/2019 Moritz Bärthel
##     University of Bremen
##
##################################################################

# function genFctnSORN

def genFctnSORN(OP,*datatypes):
	""" Defines a SORN LUT object for a certain math. operation.
	
	Input Arguments:
		op			-- mathematical operation formatted as a string (eg. "+", "*", "**2", "sqrt", "log", "log2")
		datatypes 	-- SORN datatype for {IN0/*IN1/OUT} formatted as class "sornDatatype"
		
	Output Arguments:
		sornTable	-- object of class "sornTable" containing the input and output datatypes and SORN values
	"""
	
	# import packages
	import re
	import numpy as np
	from sorngen_datatypes import sornDatatype
	from sorngen_datatypes import sornInterval
	from sorngen_datatypes import sornFctnTable
	from fractions import Fraction
	
	# define the SORN table object
	FctnTab = sornFctnTable()
		
	# determine number of inputs
	FctnTab.Nin = len(datatypes)-1
	if FctnTab.Nin > 2:
		raise Exception("More than 2 inputs are not implemented!")
		
	# set the operation
	FctnTab.OP = OP
		
	# set the datatypes
	FctnTab.datatypeIN0 = datatypes[0]
	FctnTab.datatypeIN1 = datatypes[1] if FctnTab.Nin == 2 else []
	FctnTab.datatypeOUT = datatypes[2] if FctnTab.Nin == 2 else datatypes[1]
	
	# set the pools of SORN values
	FctnTab.poolIN0SORN = np.eye(len(FctnTab.datatypeIN0.intervals), dtype=int)
	FctnTab.poolIN1SORN = np.eye(len(FctnTab.datatypeIN1.intervals), dtype=int) if FctnTab.Nin == 2 else []
	FctnTab.poolOUTSORN = np.eye(len(FctnTab.datatypeOUT.intervals), dtype=int)
	
	# calculate the resulting intervals
	if FctnTab.Nin == 2:
		
		# two inputs
		for op0CTR in range(0,len(FctnTab.datatypeIN0.intervals)): # loop over OP0
			FctnTab.resultValues.append([]) # create an (empty) row in the matrix "resultValues"
			FctnTab.resultSORN.append([]) # create an (empty) row in the matrix "resultSORN"
			for op1CTR in range(0,len(FctnTab.datatypeIN1.intervals)): # loop over OP1
				FctnTab.resultSORN[op0CTR].append([]) # create an (empty) col in the matrix "resultSORN"
			
				# left bound of result
				c_startValue = np.inf
				for caseCTR in range(0,4):
					# define the two operands (lower or upper boundary) and convert them to strings
					OPa = str(FctnTab.datatypeIN0.intervals[op0CTR].lowerBoundary) if ((caseCTR == 0) or (caseCTR == 1)) else str(FctnTab.datatypeIN0.intervals[op0CTR].upperBoundary)
					OPb = str(FctnTab.datatypeIN1.intervals[op1CTR].lowerBoundary) if ((caseCTR == 0) or (caseCTR == 2)) else str(FctnTab.datatypeIN1.intervals[op1CTR].upperBoundary)
					# replace "a/b" with "Fraction(a,b)"
					OPa = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",OPa)	
					OPb = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",OPb)	
					# check for infinity value and replace with "np.inf" in string
					OPa = re.sub("inf", "np.inf", OPa)
					OPb = re.sub("inf", "np.inf", OPb)
					c_intValue = eval(OPa + FctnTab.OP + OPb)
					if c_intValue < c_startValue:
						c_startValue = c_intValue
				
				# right bound of result
				c_endValue = -np.inf
				for caseCTR in range(0,4):
					# define the two operands (lower or upper boundary) and convert them to strings
					OPa = str(FctnTab.datatypeIN0.intervals[op0CTR].lowerBoundary) if ((caseCTR == 0) or (caseCTR == 1)) else str(FctnTab.datatypeIN0.intervals[op0CTR].upperBoundary)
					OPb = str(FctnTab.datatypeIN1.intervals[op1CTR].lowerBoundary) if ((caseCTR == 0) or (caseCTR == 2)) else str(FctnTab.datatypeIN1.intervals[op1CTR].upperBoundary)
					# replace "a/b" with "Fraction(a,b)"
					OPa = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",OPa)	
					OPb = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",OPb)	 
					# check for infinity value and replace with "np.inf" in string
					OPa = re.sub("inf", "np.inf", OPa)
					OPb = re.sub("inf", "np.inf", OPb)
					c_intValue = eval(OPa + FctnTab.OP + OPb)
					if c_intValue > c_endValue:
						c_endValue = c_intValue
						
				# calculate the "isopen" condition
				c_lowerIsOpen = 0 if (np.absolute(c_startValue) >= np.absolute(c_endValue)) else 1
				c_upperIsOpen = 0 if (np.absolute(c_startValue) <= np.absolute(c_endValue)) else 1
						
				# store the result values
				FctnTab.resultValues[op0CTR].append(sornInterval(c_startValue,c_endValue,c_lowerIsOpen,c_upperIsOpen))
				
				# generate the SORN result
				c_SORN = []
				for poolCTR in range(0,len(FctnTab.datatypeOUT.intervals)):
					c_poolStartValue = FctnTab.datatypeOUT.intervals[poolCTR].lowerBoundary
					c_poolEndValue = FctnTab.datatypeOUT.intervals[poolCTR].upperBoundary
					c_poolLowerIsOpen = FctnTab.datatypeOUT.intervals[poolCTR].lowerIsOpen
					c_poolUpperIsOpen = FctnTab.datatypeOUT.intervals[poolCTR].upperIsOpen
					if (c_endValue < c_poolStartValue) or ((c_endValue == c_poolStartValue) and (c_upperIsOpen == 1 or c_poolLowerIsOpen == 1)) or (c_startValue > c_poolEndValue) or ((c_startValue == c_poolEndValue) and (c_lowerIsOpen == 1 or c_poolUpperIsOpen == 1)):
						c_SORN.append(0)
					else:
						c_SORN.append(1)
				
				# store the SORN results
				FctnTab.resultSORN[op0CTR][op1CTR] = c_SORN 
				
	elif FctnTab.Nin == 1:
	
		# one input
		for op0CTR in range(0,len(FctnTab.datatypeIN0.intervals)): # loop over OP0
		
			c_startValue = np.inf # left bound of result
			c_endValue = -np.inf # right bound of result
			for caseCTR in range(0,2):
				OPa = str(FctnTab.datatypeIN0.intervals[op0CTR].lowerBoundary) if (caseCTR == 0) else str(FctnTab.datatypeIN0.intervals[op0CTR].upperBoundary)
				OPa = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",OPa)	# replace "a/b" with "Fraction(a,b)"
				OPa = re.sub("inf", "np.inf", OPa) # check for infinity value and replace with "np.inf" in string
				# determine the kind of operation
				if re.search(r"[a-zA-Z]+[\d]*",FctnTab.OP):
					c_intValue = eval("np." + FctnTab.OP + "(float(" + OPa + "))")
				else:
					c_intValue = eval("(" + OPa + ")" + FctnTab.OP)
				if c_intValue < c_startValue or np.isnan(float(c_intValue)):
					c_startValue = c_intValue
				if c_intValue > c_endValue or np.isnan(float(c_intValue)):
					c_endValue = c_intValue
					
			# calculate the "isopen" condition
			c_lowerIsOpen = 0 if (np.absolute(c_startValue) >= np.absolute(c_endValue)) else 1
			c_upperIsOpen = 0 if (np.absolute(c_startValue) <= np.absolute(c_endValue)) else 1
					
			# store the results
			FctnTab.resultValues.append(sornInterval(c_startValue,c_endValue,c_lowerIsOpen,c_upperIsOpen))
			
			# generate the SORN result
			c_SORN = []
			for poolCTR in range(0,len(FctnTab.datatypeOUT.intervals)):
				c_poolStartValue = FctnTab.datatypeOUT.intervals[poolCTR].lowerBoundary
				c_poolEndValue = FctnTab.datatypeOUT.intervals[poolCTR].upperBoundary
				c_poolLowerIsOpen = FctnTab.datatypeOUT.intervals[poolCTR].lowerIsOpen
				c_poolUpperIsOpen = FctnTab.datatypeOUT.intervals[poolCTR].upperIsOpen
				if np.isnan(float(c_startValue)) or np.isnan(float(c_endValue)) or (c_endValue < c_poolStartValue) or ((c_endValue == c_poolStartValue) and (c_upperIsOpen == 1 or c_poolLowerIsOpen == 1)) or (c_startValue > c_poolEndValue) or ((c_startValue == c_poolEndValue) and (c_lowerIsOpen == 1 or c_poolUpperIsOpen == 1)):
					c_SORN.append(0)
				else:
					c_SORN.append(1)
			
			# store the SORN results
			FctnTab.resultSORN.append(c_SORN)
			
	# return the output
	return FctnTab
	
# EOF genFctnSORN