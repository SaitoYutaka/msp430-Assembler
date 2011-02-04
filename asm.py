import sys
import traceback
import msp430x2xx

def usage():
    print('usage: asm.py [file]')

def deletenl(line):
    line = line.strip('\n')
    line = line.lstrip()
    return line

def getLabel(s):
    if s.find(' ') == -1: return s
    else: return s[0:s.find(' ')]

def GetAllLabel(f):
    dLabel = {}
    dummyval = 0
    for line in f:
        line = deletenl(line)
        if line[0] == ':':
            tmp = getLabel(line)
            dLabel[tmp[1:]] = dummyval
            dummyval += 1
            continue
    return dLabel

if len(sys.argv) == 1:
    usage()
    sys.exit()

try:
    f = open(sys.argv[1],'r')
except:
    print(sys.argv[1] + ': No such file')
    usage()
    sys.exit()

lineno = 1   
x = msp430x2xx.MSP430x2xx()
dLabel = GetAllLabel(f)
f.seek(0)

tmparr = []
addrnum = 0xf800
for line in f:
    line = deletenl(line)
    isLabel = ''
    source = ''


    if line == '' or line[0] == ';': continue

    if line[0] == ':' :
        tmp = getLabel(line)
        dLabel[tmp[1:]] = addrnum
        
        if line.replace(tmp,'') == '':continue
        else: 
            line = line.replace(tmp,'')
            line = deletenl(line)

    for label in dLabel.keys():
        if label in line:
            source = line.replace(label,str(dLabel[label]))
            isLabel = label

    if isLabel == '': source = line

    opcode = x.asm(source)

    if opcode[0] == -1:
        print(opcode[1],end='')
        print(' line:' + str(lineno))
        sys.exit()

    tmparr.append([line,isLabel,opcode,addrnum])
    for byte in opcode: addrnum += 2
    lineno += 1

SOURCE  = 0
LABEL   = 1
OPCODE  = 2
ADDRESS = 3
for asminfo in tmparr:
    print ('%-30s' % asminfo[SOURCE],end='')
    print ("0x%04x " % asminfo[ADDRESS],end='')
    if asminfo[LABEL] != '': # label?
        opcode = x.asm(asminfo[SOURCE].replace(asminfo[LABEL],str(dLabel[asminfo[LABEL]])))
        for byte in opcode:
            print ("0x%04x " % byte,end='')
    else:
        for byte in asminfo[OPCODE]:
            print ("0x%04x " % byte,end='')
    print()
print(dLabel)
f.close()
