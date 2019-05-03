-----------------------------------------------
-- SORN VHDL FUNCTION GENERATOR 
-- Engine: 		v1.0
-- Filename: 	"#filename"
-- Author: 		#author
-- Info: 		#info
-- (c) 2019 ITEM University of Bremen
------------------------------------------------------

library IEEE;
use IEEE.STD_LOGIC_1164.all;
use IEEE.NUMERIC_STD.all;
use IEEE.STD_LOGIC_UNSIGNED.all;

------------------------------------------------------
-- input 0 (input0) encoding
#input0comment
-- result  (output0) encoding
#resultcomment
------------------------------------------------------
 
entity #entityname is
	port(
	-- inputs
	input0	: IN std_logic_vector(#sizeofd0 downto 0);
	-- outputs
	output0 	: OUT std_logic_vector(#sizeofr downto 0)
);
end #entityname;

architecture behavior of #entityname is

	-- internal signal declaration
	signal x0 : std_logic_vector(#sizeofd0 downto 0);
	signal result : std_logic_vector(#sizeofr downto 0);

begin

-- IO assignments
x0 <= input0;
output0 <= result;

-- sorn function
#function
end behavior;
