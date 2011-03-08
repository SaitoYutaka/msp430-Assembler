import sys
import re
import traceback
import msp430x2xx
import msp430x2xx_registers
import msp430_bin2ihex
from optparse import OptionParser

class AssemblerDirectives(object):
    def __init__(self):
        self.ORG               = 0
        self.INTERRUPT_VECTOR = [['.iv16',0xffff],
                                 ['.iv17',0xffff],
                                 ['.iv18',0xffff],
                                 ['.iv19',0xffff],
                                 ['.iv20',0xffff],
                                 ['.iv21',0xffff],
                                 ['.iv22',0xffff],
                                 ['.iv23',0xffff],
                                 ['.iv24',0xffff],
                                 ['.iv25',0xffff],
                                 ['.iv26',0xffff],
                                 ['.iv27',0xffff],
                                 ['.iv28',0xffff],
                                 ['.iv29',0xffff],
                                 ['.iv30',0xffff],
                                 ['.iv31',0xffff]]

    def littleendian(self, num):
        tmp1 = (num & 0x00ff) << 8
        tmp2 = (num & 0xff00) >> 8
        return  tmp1 | tmp2

    def GetAsmDirectives(self, f):
        for readline in f:
            line = readline
            if '.org' in line:
                self.ORG = int(line[5:],16)

            elif '.iv' in line:
                for i, v in enumerate(self.INTERRUPT_VECTOR):
                    if v[0] in line:
                        if '0x' in line[6:]:
                            self.INTERRUPT_VECTOR[i][1] = int(line[6:],16)
                        else:
                            self.INTERRUPT_VECTOR[i][1] = line[6:]

def InitUsage():
    usage = "usage: %prog [file] > output"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug",
                      help="debug" )


    return parser

def RemoveNewLineSpaceTab(lines):
    ret = []
    for x in lines:
        x = x.strip('\n')
        x = x.lstrip()
        x = x.replace('\t',' ')
        ret.append(x)
    return ret


class Label(object):
    def __init__(self):
        self.d = {}

    def GetLabel(self, s):
        if s.find(' ') == -1:
            return s
        else: return s[0:s.find(' ')]

    def SetAddress(self, l, addr):
        label = self.GetLabel(l)
        self.d[label[1:]] = addr

    def IsOnlyLabelInLine(self, line):
        for x in self.d.keys():
            if x in line:
                tmp = line.replace(x,'')
                tmp = tmp.replace(':','')
                tmp = tmp.strip()
                if tmp == '': return True
                else: return False

    def GetAllLabel(self, f):
        dummyval = 0
        for line in f:
            if line[0] == ':':
                tmp = self.GetLabel(line)
                self.d[tmp[1:]] = dummyval
                dummyval += 1
                continue

    def GetLabelInLine(self, line):
        for label in self.d.keys():
            if label in line:
                return label
        return ''

def Preprocess(lines):
    ret = []
    tmp = ''
    for line in lines:
        tmp = line
        for reg in msp430x2xx_registers.registers.keys():
            if reg in line:
                tmp = line.replace(reg,str(msp430x2xx_registers.registers[reg]))
                break
        for reg in msp430x2xx_registers.registers.keys():
            if reg in line:
                tmp = tmp.replace(reg,str(msp430x2xx_registers.registers[reg]))
                break
        ret.append(tmp)
    return ret

def Get1BytesList(data):
    ret = []
    for x in data:
        ret.append((x & 0xff00) >> 8)
        ret.append( x & 0x00ff)
    return ret

#if __name__ == "__main__":

parser = InitUsage()
options, args = parser.parse_args()

#if args == []:
#    parser.print_usage()
#    sys.exit()

#if len(sys.argv) == 1:
#    usage()
#    sys.exit()

try:
    if options.debug != None:
        f = open(options.debug,'r')
    else:
        f = open(sys.argv[1],'r')
except:
    #print(sys.argv[1] + ': No such file')
    usage()
    sys.exit()
allline = f.readlines()
f.close()

lines = RemoveNewLineSpaceTab(allline)

lines_after_p = Preprocess(lines)

l = Label()
l.GetAllLabel(lines_after_p)

AsmDirect = AssemblerDirectives()
AsmDirect.GetAsmDirectives(lines_after_p)

lineno = 1   
assembleInfo = []

address = AsmDirect.ORG
MSP430x2xx = msp430x2xx.MSP430x2xx()

for line in lines_after_p:

    if line == '.ivector': break

    if line == '' or line[0] == ';' or line[0] == '.':
        lineno += 1
        continue

    if line[0] == ':' :
        l.SetAddress(line, address)
        if l.IsOnlyLabelInLine(line):
            lineno += 1
            continue
        line = line.replace(l.GetLabel(line),'')

    rLabel    = l.GetLabelInLine(line)
    if rLabel == '':
        asmSource = line
    else:
        asmSource = line.replace(rLabel,str(l.d[rLabel]))

    opcode = MSP430x2xx.asm(asmSource)

    if opcode[0] == -1:
        print(lines[lineno - 1])
        print(opcode[1],end='')
        print(' line:' + str(lineno))
        sys.exit()

    assembleInfo.append([line,rLabel,address,opcode])

    for byte in opcode:
        address += 2

    lineno += 1


SOURCE,LABEL,ADDRESS,OPCODE = range(4)

jmps = ("jne","jnz", "jeq", "jz", "jnc", "jc", "jn",
"jge", "jl", "jmp")
        
def isJumps():
    for x in jmps:
        if x in asminfo[SOURCE] or x.upper() in asminfo[SOURCE]:
            if asminfo[ADDRESS] + 1 < l.d[asminfo[LABEL]]:
                offset = int((l.d[asminfo[LABEL]] - (asminfo[ADDRESS] + 1))/2)
                stroffset = '0x' + '{0:03x}'.format(offset)
            else:
                offset = (asminfo[ADDRESS] + 1) - l.d[asminfo[LABEL]]
                offset = int(offset * -1 / 2) - 1
                stroffset = '0x' + '{0:03x}'.format(0x3ff & ~(offset * -1) + 1)

            #print(offset)
            #print(asminfo[LABEL],'{0:03x}'.format(l.d[asminfo[LABEL]]))
            #print(asminfo[SOURCE].replace(asminfo[LABEL],stroffset))
            opcode = MSP430x2xx.asm(asminfo[SOURCE].replace(asminfo[LABEL],stroffset))
            assembleInfo[i][OPCODE] = opcode
            assembleInfo[i][LABEL]  = ''
            return True

    return False

for i, asminfo in enumerate(assembleInfo):
    if asminfo[LABEL] != '': # label?

        if isJumps(): continue

        opcode = MSP430x2xx.asm(asminfo[SOURCE].replace(asminfo[LABEL],str(l.d[asminfo[LABEL]])))
        assembleInfo[i][OPCODE] = opcode
        assembleInfo[i][LABEL]  = ''

for i, x in enumerate(AsmDirect.INTERRUPT_VECTOR):
    if l.d.get(x[1]):
        AsmDirect.INTERRUPT_VECTOR[i][1] = l.d.get(x[1])

if options.debug != None:
    for data in assembleInfo:
        print(data[SOURCE],end='')
        for j in data[OPCODE]:
            print(' ' + '{0:04x}'.format(j) + ' ',end='')
        print()

    sys.exit()

OpcodeList = []
for data in assembleInfo:
    for opcode in data[OPCODE]:
        OpcodeList.append(opcode)

data = Get1BytesList(OpcodeList)
msp430_bin2ihex.MakeIntelHexLines(AsmDirect.ORG, data)

tmp = []
for x in AsmDirect.INTERRUPT_VECTOR:
    tmp.append(x[1])

def Get1BytesList2(data):
    ret = []
    for x in data:
        ret.append( x & 0x00ff)
        ret.append((x & 0xff00) >> 8)
    return ret

data = Get1BytesList2(tmp)
msp430_bin2ihex.MakeIntelHexLines(0xffe0, data)
print(':00000001FF')
sys.exit()
