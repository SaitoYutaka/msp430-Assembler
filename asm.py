import sys
import traceback
import msp430x2xx
import msp430x2xx_registers
import intelhex

def usage():
    print('usage: asm.py [file]')

def RemoveNewLineSpaceTab(line):
    line = line.strip('\n')
    line = line.lstrip()
    line = line.replace('\t',' ')
    return line

def GetLabel(s):
    if s.find(' ') == -1:
        return s
    else: return s[0:s.find(' ')]

def GetAllLabel(f):
    dLabel = {}
    dummyval = 0
    for line in f:
        line = RemoveNewLineSpaceTab(line)
        if line[0] == ':':
            tmp = GetLabel(line)
            dLabel[tmp[1:]] = dummyval
            dummyval += 1
            continue
    return dLabel

def GetReplaceLabel(line):
    for label in dLabel.keys():
        if label in line:
            return label
    return ''

if len(sys.argv) == 1:
    usage()
    sys.exit()

try:
    f = open(sys.argv[1],'r')
except:
    print(sys.argv[1] + ': No such file')
    usage()
    sys.exit()

dLabel = GetAllLabel(f)
f.seek(0)

address = 0
orgaddress = 0
for readline in f:
    line = RemoveNewLineSpaceTab(readline)
    if '.org' in line:
        address = int(line[5:],16)
        orgaddress = int(line[5:],16)

f.seek(0)
lineno = 1   
assembleInfo = []

MSP430x2xx = msp430x2xx.MSP430x2xx()
for readline in f:

    line = RemoveNewLineSpaceTab(readline)
    if line == '' or line[0] == ';' or line[0] == '.': continue

    if line[0] == ':' :
        label = GetLabel(line)
        dLabel[label[1:]] = address
        if line.replace(label,'') == '':continue
        line = RemoveNewLineSpaceTab(line)
        line = line.replace(label,'')

    rLabel    = ''
    asmSource = ''
    rLabel    = GetReplaceLabel(line)
    if rLabel == '': asmSource = line
    else:
        asmSource = line.replace(rLabel,str(dLabel[rLabel]))

    for n in range(2):
        for reg in msp430x2xx_registers.registers.keys():
            if reg in asmSource:
                asmSource = asmSource.replace(reg,str(msp430x2xx_registers.registers[reg]))

    opcode = MSP430x2xx.asm(asmSource)

    if opcode[0] == -1:
        print(opcode[1],end='')
        print(' line:' + str(lineno))
        sys.exit()

    assembleInfo.append([line,rLabel,address,opcode])
    for byte in opcode: address += 2
    lineno += 1
f.close()

SOURCE,LABEL,ADDRESS,OPCODE = range(4)

for i, asminfo in enumerate(assembleInfo):
    #print ('%-30s' % asminfo[SOURCE],end='')
    #print ("0x%04x " % asminfo[ADDRESS],end='')
    if asminfo[LABEL] != '': # label?
        opcode = x.asm(asminfo[SOURCE].replace(asminfo[LABEL],str(dLabel[asminfo[LABEL]])))
        assembleInfo[i][OPCODE] = opcode
        assembleInfo[i][LABEL]  = ''
        #for byte in opcode:
        #    print ("0x%04x " % byte,end='')
    else:pass
       # for byte in asminfo[OPCODE]:
       #     print ("0x%04x " % byte,end='')
    #print()


data = []
for asminfo in assembleInfo:
    for x in asminfo[OPCODE]:
        data.append(x)


cnt = 0
offset = 0
hex = []
for x in data:
    hex.append(x)
    if cnt >= 7:
        if orgaddress + offset >= 0xffff:
            print('size error')
            sys.exit()
        foo = intelhex.MakeIntelHex('00', orgaddress + offset, hex)
        print(foo)
        hex = []
        cnt = 0
        offset += 16
        continue
    cnt += 1
foo = intelhex.MakeIntelHex('00', orgaddress + offset, hex)
print(foo)
