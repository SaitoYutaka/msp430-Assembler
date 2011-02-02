import sys
import traceback
import msp430x2xx

def usage():
    print('usage: asm.py [file]')

if len(sys.argv) == 1:
    usage()
    sys.exit()

try:
    f = open(sys.argv[1],'r')
except:
    print(sys.argv[1] + ': No such file')
    usage()
    sys.exit()

dLabel = {}
lineno = 1    
x = msp430x2xx.MSP430x2xx()
for line in f:
    if line[0] == ':':
        dLabel[line] = None
        continue
f.seek(0)

for line in f:
    line = line.strip('\n')
    line = line.lstrip()

    if line == '' or line[0] == ';' or line[0] == ':' : continue
    opcode = x.asm(line)

    if opcode[0] == -1:
        print(opcode[1],end='')
        print(' line:' + str(lineno))
        sys.exit()

    print ('%-30s' % line,end='')
    for byte in opcode:
        print ("0x%04x " % byte,end='')
    print()
    lineno += 1

print(dLabel.keys())
f.close()
