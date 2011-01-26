#!/usr/local/bin/python3

import mmap
import sys
import traceback
import msp430x2xx

assource = [
"MOV #0x280,SP",
"MOV #0x5a80,&0x0120",
#"CLR     R15",
#"TST     R15",
#"JZ      0xf81c",
#"DECD    R15",
"MOV 0xf880(R15),0x200(R15)",
#"JNZ     0xf812",
#"CLR     R15",
#"TST     R15",
#"JZ      0xf82c",
#"DEC     R15",
#"CLR.B   0x200(R15)",
#"JNZ     0xf824",
#"BR      #0xf842",
#"BR      #0xf87e",
"BIS.B #0x41,&0x0022",
"BIS.B #0x41,&0x0021",
#"RET     ",
"MOV #0x280,SP",
"MOV #0x5a80,&0x0120",
"BIS.B #0x41,&0x0022",
"BIS.B #0x41,&0x0021",
"BIS.B #0x20,&0x0053",
"MOV #0x110,&0x0160",
"MOV #0x10,&0x0162",
"MOV #0x2edf,&0x0172",
"MOV #0x8,R15",
"MOV R15,SR",
"JMP 0xf874",
"XOR.B #0x41,&0x0021",
"RETI",
"RETI",]

for line in assource:
    x = msp430x2xx.MSP430x2xx()
    print ('%-30s' % line,end='')
    opcode = x.asm(line)
    for byte in opcode:
        print ("0x%04x " % byte,end='')
    print()

while True:
    line = input('-->')
    if line == '': sys.exit()
    try:
        opcode = x.asm(line)
        if opcode[0] == -1:
            print(opcode[1])
            continue
        print ('%-30s' % line,end='')
        for byte in opcode:
            print ("0x%04x " % byte,end='')
    except ValueError as x:
        print (x)
    print()


