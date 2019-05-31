##################################################################
##
## file: sorngen_datatypes.py
##
## (c) 2018/2019 Moritz Bärthel
##     University of Bremen
##
##################################################################


## 1/ SORN Datatype containing a whole set of SORN intervals
class sornDatatype:
	name = ""
	intervals = []
	sornsize = 0
	
	def __init__(self):
		self.name = self.name
		self.intervals = []
		self.sornsize = 0

	def showIV(self):
		for it in self.intervals:
			print(it.name, end=" ")
		print("")
		
	def getLowerBound(self):
		return self.intervals.lowerBoundary

## 2/ SORN interval with values of lower and upper bound and boundary conditions 
class sornInterval:

	name =""
	lowerBoundary = 0
	upperBoundary = 0
	upperIsOpen = 0
	lowerIsOpen = 0

	def __init__(self, lowerBoundary, upperBoundary, lowerIsOpen, upperIsOpen):
		self.lowerBoundary = lowerBoundary
		self.upperBoundary = upperBoundary
		self.lowerIsOpen = lowerIsOpen
		self.upperIsOpen = upperIsOpen
		# create name
		self.name = "(" if self.lowerIsOpen == 1 else "["
		self.name = self.name + str(float(self.lowerBoundary)) + "," + str(float(self.upperBoundary))
		self.name = self.name + (")" if self.upperIsOpen == 1 else "]")
		
	def getName(self):
		return self.name

## 3/ datatype containing all information about a SORN operatation with one or two inputs
class sornFctnTable:

	name			= ""
	OP				= ""
	Nin				= 0
	datatypeIN0		= []
	datatypeIN1		= []
	datatypeOUT		= []
	poolIN0SORN 	= []
	poolIN1SORN 	= []
	poolOUTSORN 	= []
	resultValues 	= []
	resultSORN 		= []
	
	def __init__(self):
		self.name 			= self.name
		self.OP				= ""
		self.Nin			= 0
		self.datatypeIN0	= []
		self.datatypeIN1	= []
		self.datatypeOUT	= []
		self.poolIN0SORN 	= []
		self.poolIN1SORN 	= []
		self.poolOUTSORN 	= []
		self.resultValues 	= []
		self.resultSORN 	= []

