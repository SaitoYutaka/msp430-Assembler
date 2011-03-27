##msp430 tiny assembler
This script require python version 3.
Usage : python asm.py [file]

##1. What is msp430 tiny assembler?
The msp430 tiny assembler is a small assembler (written by python).
This assembler convert a assembly lauguage source file to intel hex format.


##2. How to write assembly lauguage for msp430 tiny assembler ?

##2.1 Layout of source file

      ;; Some comments
      .org 0xf800

      :LABEL	   
      instruction operands

      .iv31 LABEL
      .iv30 LABEL
      .iv29 LABEL
      .iv28 0x0000
      .iv27 0x0000
      .iv26 0x0000
      .iv25 0x0000
      .iv24 0x0000
      .iv23 0x0000
      .iv22 0x0000
      .iv21 0x0000
      .iv20 0x0000
      .iv19 0x0000
      .iv18 0x0000
      .iv17 0x0000
      .iv16 0x0000

##2.2 Comment
Commment is a start semicolon(;) .

##2.3 Labels
Label is a start icolon(:) .
You can't write Labels a line on assembly code.

    Example
    :LOOP jmp LOOP <-- incorrect
    
    :LOOP          <-- need newline
    	   jmp LOOP

##2.4 .org : Program Origin
The .org directive is to specify the origin address which assembler will
assume the program begins at when it is loaded into flash memory.

##2.5 .iv31 ...  .iv16 : Interrupt vector
.iv[num]: Interrupt Vector[Priority]
The .iv31, .iv30 , .iv29 ,,,, .iv16 directives are to specify the interrupt vector address.

##2.6 Instructions
Msp430 tiny assembler is supported those instructions.
RRC[.B], SWPB, RRA[.B], SXT, PUSH[.B], CALL, RETI, JNE, JNZ, JEQ,
JZ, JNC, JC, JN, JG, JL, JMP, MOV[.B], ADD[.B], ADDC[.B], SUBC[.B], SUB[.B]
CMP[.B], DADD[.B], BIT[.B], BIC[.B], BIS[.B], XOR[.B], AND[.B]

It doesn't support emulated instructions such as NOP, RET and DEC.

##2.7 Operands
You can write register name on operands.

    Example
    ; Set value to watchdog timer control register(WDTCTL).
    MOV #0x5a80, &WDTCTL
    ; Set Bits to digital I/O Port1 Direction register(P1DIR).
    BIS.B #0x0041, &P1DIR

