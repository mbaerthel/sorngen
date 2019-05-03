##################################################################
##
## file: sorngen_defineSORN.py
##
## (c) 2018/2019 Moritz Bärthel
##     University of Bremen
##
##################################################################

# function defineSORN 

def defineSORN(style,res_str,*varargs):
	""" Defines the interval ranges and boundary conditions of a SORN datatype.
	
	Input Arguments:
		style = "lin"/"log"         			 -- defines the shape of the SORN datatype
		res_str = (start,end,*step)     			 -- defines the start and endpoints of the datatype (start...end for linear style with stepsize step, 2^start...2^end for logarithmic style)
		varargs = "zero","infinity","negative"   -- when set, the datatype includes zero and/or infinity and negative values
	
	Output Arguments:
		DATATYPE		-- formatted as class "sornDatatype"
	"""
	
	# import necessary packages
	import re 					
	import numpy as np
	from sorngen_datatypes import sornDatatype
	from sorngen_datatypes import sornInterval
	from fractions import Fraction
	
	# set default arguments
	ENABLE_ZERO = 0
	ENABLE_INFTY = 0
	ENABLE_NEGATIVE = 0
	
	# read input arguments
	ENABLE_LINEAR = 1 if re.search(r"[lL]in(ear){,1}",style) else 0
	for arg in varargs:
		ENABLE_ZERO = 1 if re.search(r"[zZ]ero",arg) else ENABLE_ZERO
		ENABLE_INFTY = 1 if re.search(r"[iI]nf(inity){0,1}",arg) else ENABLE_INFTY
		ENABLE_NEGATIVE = 1 if re.search(r"[nN]eg(ative){0,1}",arg) else ENABLE_NEGATIVE
	
	# evaluate input "res_str" (Resolution)
	res_str = re.sub(r"(\d+)\/(\d+)",r"Fraction(\g<1>,\g<2>)",res_str)
	res=eval(res_str)
	
	# build value sequence
	valSeq_LEFT = [] 	# sequence of values of the left interval bound 
	valSeq_RIGHT = []	# sequence of values of the right interval bound
	
	# zero
	if ENABLE_ZERO == 1:
		valSeq_LEFT.append(0)
		valSeq_RIGHT.append(0)
	# logarithmic style	
	if ENABLE_LINEAR == 0: 
		# positive numbers
		for element_CNT in range(res[0],res[1]+1):
			valSeq_LEFT.append(0.0 if element_CNT == res[0] else 2**(element_CNT-1))
			valSeq_RIGHT.append(2**element_CNT)
	# linear style
	elif ENABLE_LINEAR == 1: 
		# positive numbers
		for element_CNT in range(int(res[0]/res[2]),int(res[1]/res[2])):
			valSeq_LEFT.append(element_CNT*res[2]) 
			valSeq_RIGHT.append((element_CNT+1)*res[2]) 
	# infinity
	if ENABLE_INFTY == 1:
		valSeq_LEFT.append(valSeq_RIGHT[-1])
		valSeq_RIGHT.append(np.inf)
	# negative numbers
	if ENABLE_NEGATIVE == 1:
		for element_CNT in range(0,len(valSeq_LEFT)-1):
			valSeq_LEFT.insert(0,-valSeq_RIGHT[2*element_CNT+1])
			valSeq_RIGHT.insert(0,-valSeq_LEFT[2*element_CNT+2])
	
	# set interval conditions
	condSeq_LEFT = []; # entries: isopen=0/1
	condSeq_RIGHT = [];

	for index in range(0,len(valSeq_LEFT)):
		if index < (len(valSeq_LEFT)-1)/2: # negative values
			condSeq_LEFT.append(0) 
			condSeq_RIGHT.append(1)
		elif index == (len(valSeq_LEFT)-1)/2: # zero value
			condSeq_LEFT.append(0)
			condSeq_RIGHT.append(0)
		elif index > (len(valSeq_LEFT)-1)/2: # positve values
			condSeq_LEFT.append(1) 
			condSeq_RIGHT.append(0)
			
	# convert to sornDatatype class
	DATATYPE = sornDatatype()
	for index in range(0,len(valSeq_LEFT)):
		DATATYPE.intervals.append(sornInterval(valSeq_LEFT[index],valSeq_RIGHT[index],condSeq_LEFT[index],condSeq_RIGHT[index]))
	
	# save the SORN size
	DATATYPE.sornsize = len(valSeq_LEFT)
	
	# return the output
	return DATATYPE

# EOF defineSORN