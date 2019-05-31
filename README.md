Hardware Generator for SORN Arithmetic

This is a python-based tool to generate VHDL code for arithmetic algorithms processed in SORN arithmetic.

SORN (set of real numbers) is a datatype related to type-2 unum format. For more information see http://www.johngustafson.net/pubs/RadicalApproach.pdf

The tool is implemented for python 3 and requires a numpy installation.

The up-to-date tool version can be found in "python/". Older versions are stored folder "archive/<YYMMDD>". Version changes are documented in the CHANGELOG.

Specification:

The specification file has a '.sorn' ending and contains all information about name, datatype, pipeline registers and the equations.

- Name: Set the name of the design. The toplevel VHDL file will be "name.vhd".

- Datatype: ['lin'/'log'/'man', '[start,stop,step]', 'zero', 'negative', 'infinity']

	-- 'lin'/'log': choose either a linear or logarithmic spacing of the lattice values

		-- '[start,stop,step]': choose the start and end value for the lattice values and a stepsize for a linear scale 

		-- 'zero', 'negative', 'infinity': extend the datatype by the given options (any combination can be choosen)
		
	-- 'man': choose a fully manually defined datatype
	
		-- define datatype as ['man','{<interval1>;<interval2>;<...>}'] with <interval> having open "(" and closed "[" interval bounds

		-- see "MIMO_solver_N2" for an example
	
- Pipeline registers: The amount of specified registers will be inserted in the design.

- Equations: Specify one or multiple equations with consistent variable names, round brackets and python-based arithmetic operators. Variables may appear in multiple equations.

- Examples: See the files "MIMO_solver_N2.sorn" and "MIMO_solver_N4.sorn".


Execution:

With a valid specification file "SPEC.sorn" the tool can be executed with:

	python .\sorgen_main.py .\SPEC.sorn
	
	
Outputs:

The folder ".\VHDL" contains all the created VHDL files including submodules and the toplevel file. The basic arithmetic SORN modules are stored in the subfolder ".\VHDL\VHDLbasic".



