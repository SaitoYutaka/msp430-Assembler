import sys
import re
import traceback
import msp430x2xx
import msp430x2xx_registers
import msp430_bin2ihex

class AssemblerDirectives(object):
    def __init__(self):
        self.ORG               = 0
        self.INTTERRUPT_VECTOR = []

    def GetAsmDirectives(self, f):
        flag    = False
        for readline in f:
            line = RemoveNewLineSpaceTab(readline)
            if '.org' in line:
                self.ORG = int(line[5:],16)
            elif '.ivector' in line:
                flag = True
                continue

            if flag:
                self.INTTERRUPT_VECTOR.append(line)
                if len(self.INTTERRUPT_VECTOR) == 16:
                    flag = False


def usage():
    print('usage: asm.py [file]')

def RemoveNewLineSpaceTab(line):
    line = line.strip('\n')
    line = line.lstrip()
    line = line.replace('\t',' ')
    return line

class Label(object):
    def __init__(self):
        self.d = {}

    def GetLabel(self, s):
        if s.find(' ') == -1:
            return s
        else: return s[0:s.find(' ')]

    def GetAllLabel(self, f):
        dummyval = 0
        for line in f:
            line = RemoveNewLineSpaceTab(line)
            if line[0] == ':':
                tmp = self.GetLabel(line)
                self.d[tmp[1:]] = dummyval
                dummyval += 1
                continue

    def GetReplaceLabel(self, line):
        for label in self.d.keys():
            if label in line:
                return label
        return ''

#if __name__ == "__main__":

if len(sys.argv) == 1:
    usage()
    sys.exit()

try:
    f = open(sys.argv[1],'r')
except:
    print(sys.argv[1] + ': No such file')
    usage()
    sys.exit()
allline = f.readlines()
f.close()

l = Label()
l.GetAllLabel(allline)

AsmDirect = AssemblerDirectives()
AsmDirect.GetAsmDirectives(allline)

def littleendian(num):
    tmp1 = num & 0x00ff; tmp1 <<= 8
    tmp2 = num & 0xff00; tmp2 >>= 8
    return  tmp1 | tmp2

for i, v in enumerate(AsmDirect.INTTERRUPT_VECTOR):
    if v[:2] == '0x':          base = 16
    elif re.match('^[1-9]',v): base = 10
    else: continue
    AsmDirect.INTTERRUPT_VECTOR[i] = littleendian(int(v,base))


lineno = 1   
assembleInfo = []
OpcodeList   = []

address = AsmDirect.ORG
MSP430x2xx = msp430x2xx.MSP430x2xx()
for readline in allline:

    line = RemoveNewLineSpaceTab(readline)
    if line == '.ivector': break

    if line == '' or line[0] == ';' or line[0] == '.':
        lineno += 1
        continue

    if line[0] == ':' :
        label = l.GetLabel(line)
        l.d[label[1:]] = address
        if line.replace(label,'') == '':
            lineno += 1
            continue
        line = RemoveNewLineSpaceTab(line)
        line = line.replace(label,'')

    rLabel    = ''
    asmSource = ''
    rLabel    = l.GetReplaceLabel(line)
    if rLabel == '': asmSource = line
    else:
        asmSource = line.replace(rLabel,str(l.d[rLabel]))

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
    for byte in opcode:
        address += 2


    lineno += 1



SOURCE,LABEL,ADDRESS,OPCODE = range(4)

for i, asminfo in enumerate(assembleInfo):
    #print ('%-30s' % asminfo[SOURCE],end='')
    #print ("0x%04x " % asminfo[ADDRESS],end='')
    if asminfo[LABEL] != '': # label?
        opcode = x.asm(asminfo[SOURCE].replace(asminfo[LABEL],str(l.d[asminfo[LABEL]])))
        assembleInfo[i][OPCODE] = opcode
        assembleInfo[i][LABEL]  = ''
        #for byte in opcode:
        #    print ("0x%04x " % byte,end='')
    else:pass
       # for byte in asminfo[OPCODE]:
       #     print ("0x%04x " % byte,end='')
    #print()


for i, x in enumerate(AsmDirect.INTTERRUPT_VECTOR):
    if l.d.get(x):
        AsmDirect.INTTERRUPT_VECTOR[i] = l.d.get(x)


def Get1BytesList(data):
    ret = []
    for x in data:
        ret.append((x & 0xff00) >> 8)
        ret.append( x & 0x00ff)
    return ret

for data in assembleInfo:
    for opcode in data[OPCODE]:
        OpcodeList.append(opcode)

data = Get1BytesList(OpcodeList)
msp430_bin2ihex.MakeIntelHexLines(AsmDirect.ORG, data)
data = Get1BytesList(AsmDirect.INTTERRUPT_VECTOR)
msp430_bin2ihex.MakeIntelHexLines(0xffe0, data)
print(':00000001FF')
sys.exit()


