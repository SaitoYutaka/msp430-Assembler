import sys
import re
import traceback
import msp430x2xx
import msp430x2xx_registers
import msp430_bin2ihex
import stepasm
from optparse import OptionParser


def InitUsage():
    usage = "usage: %prog [file] > output"
    parser = OptionParser(usage=usage)

    parser.add_option("-d", "--debug",
                      help="debug" )

    parser.add_option("-s", "--step",
                      help="step assemble" )

    return parser

def Get1BytesList(data):
    ret = []
    for x in data:
        ret.append((x & 0xff00) >> 8)
        ret.append( x & 0x00ff)
    return ret

parser = InitUsage()
options, args = parser.parse_args()

# Open file and read all line
try:
    if options.debug != None:
        f = open(options.debug,'r')
    elif options.step != None:
        f = open(options.step,'r')
    else:
        f = open(sys.argv[1],'r')
except:
    usage()
    sys.exit()
allline = f.readlines()
f.close()

# Remove new line, white space and tab
def RemoveNewLineSpaceTab(lines):
    ret = []
    for x in lines:
        x = x.strip('\n')
        x = x.lstrip()
        x = x.replace('\t',' ')
        ret.append(x)
    return ret
lines = RemoveNewLineSpaceTab(allline)

# Convert register name to address
def Preprocess(lines):
    ret = []
    tmp = ''
    for line in lines:
        tmp = line
        for reg in msp430x2xx_registers.registers.keys():
            if reg in line:
                tmp = line.replace(reg,'0x'+'{0:04x}'.format(msp430x2xx_registers.registers[reg]))
                break
        for reg in msp430x2xx_registers.registers.keys():
            if reg in line:
                tmp = line.replace(reg,'0x'+'{0:04x}'.format(msp430x2xx_registers.registers[reg]))
                break
        ret.append(tmp)
    return ret
lines_after_p = Preprocess(lines)

# Get labels
class Label(object):
    def __init__(self):
        self.d = {}

    def GetLabel(self, s):
        if s.find(' ') == -1:
            return s
        else: return s[0:s.find(' ')]

    def SetAddress(self, l, addr):
        label = self.GetLabel(l)
        self.d[label[:-1]] = addr

    def GetAllLabel(self, f):
        dummyval = 0
        for line in f:
            if line.strip() == '': continue
            if line.strip()[-1] == ':':
                self.d[line.strip()[:-1]] = dummyval
                dummyval += 1
                continue

    def GetLabelInLine(self, line):
        for label in self.d.keys():
            if label in line:
                return label
        return ''

l = Label()
l.GetAllLabel(lines_after_p)

# Get assembler directives
# The address will get after all lines assembled
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
            if line == '' or line[0] == ';' : continue
            if '.org' in line:
                self.ORG = int(line[5:],16)

            elif '.iv' in line:
                for i, v in enumerate(self.INTERRUPT_VECTOR):
                    if v[0] in line:
                        if '0x' in line[6:]:
                            self.INTERRUPT_VECTOR[i][1] = int(line[6:],16)
                        else:
                            self.INTERRUPT_VECTOR[i][1] = line[6:]

AsmDirect = AssemblerDirectives()
AsmDirect.GetAsmDirectives(lines_after_p)


# Assemble all line
# Make assembleInfo
# assembleInfo =[ LINE, LINE_PREP, LINE_LABEL2SDDR, LABEL, LABEL ADDRESS, ADDRESS, OPCODE ]
assembleInfo = []
lineno = 1   
address = AsmDirect.ORG
MSP430x2xx = msp430x2xx.MSP430x2xx()

def setAsmInfo(LINE='', LINE_PREP='', LINE_LABEL2SDDR='', 
               LABEL='', LABEL_ADDR='', ADDR='', OPCODE=''):
    assembleInfo.append([ LINE, LINE_PREP, LINE_LABEL2SDDR, LABEL, LABEL_ADDR, ADDR, OPCODE ])

for line, dline in zip(lines_after_p, lines):

    # Skip only new line in line , comment and assembler directives
    if line == '' or line[0] == ';' or line[0] == '.':
        if '.org' in line:
            setAsmInfo(LINE=line,LINE_PREP=line)
            #assembleInfo.append([line,'','','',''])
        lineno += 1
        continue

    # Make Label inforamation
    if line[-1] == ':' :
        l.SetAddress(line, address)
        lineno += 1
        setAsmInfo(LINE=line,LINE_PREP=line)
        #assembleInfo.append([line,'','','',''])
        continue

    # Convert label to dummy address(0x0000)
    # Get real address after assembled all line
    rLabel    = l.GetLabelInLine(line)
    if rLabel == '':
        asmSource = line
    else:
        asmSource = line.replace(rLabel,'0x0000')

    # Assemble
    opcode = MSP430x2xx.asm(asmSource)

    if opcode[0] == -1:
        print(lines[lineno - 1])
        print(opcode[1],end='')
        print(' line:' + str(lineno))
        sys.exit()

    setAsmInfo(LINE=dline, LINE_PREP=line,
               LABEL=rLabel, ADDR=address, OPCODE=opcode)
    
    #assembleInfo.append([dline,rLabel,'',address,opcode])

    for byte in opcode:address += 2

    lineno += 1

# Assemble lines which include label
LINE, LINE_PREP, LINE_LABEL2SDDR, LABEL, LABEL_ADDR, ADDR, OPCODE = range(7)
#SOURCE,LABEL,L_ADDRESS,ADDRESS,OPCODE = range(5)

def isJumps():
    jmps = ("jne","jnz", "jeq", "jz", "jnc", "jc", "jn",
            "jge", "jl", "jmp")
    for x in jmps:
        if x in asminfo[LINE] or x.upper() in asminfo[LINE]:
            if asminfo[ADDR] + 1 < l.d[asminfo[LABEL]]:
                offset = int((l.d[asminfo[LABEL]] - (asminfo[ADDR] + 1))/2)
                stroffset = '0x' + '{0:03x}'.format(offset)
            else:
                offset = (asminfo[ADDR] + 1) - l.d[asminfo[LABEL]]
                offset = int(offset * -1 / 2) - 1
                stroffset = '0x' + '{0:03x}'.format(0x3ff & ~(offset * -1) + 1)

            opcode = MSP430x2xx.asm(asminfo[LINE].replace(asminfo[LABEL],stroffset))
            assembleInfo[i][OPCODE] = opcode

            return True

    return False

for i, asminfo in enumerate(assembleInfo):
    if asminfo[LABEL] != '':
        if isJumps(): continue

        opcode = MSP430x2xx.asm(asminfo[LINE].replace(asminfo[LABEL],str(l.d[asminfo[LABEL]])))
        assembleInfo[i][OPCODE] = opcode
    elif asminfo[LINE][-1] == ':':
        assembleInfo[i][LABEL_ADDR] = l.d[asminfo[LINE][:-1]]

# Get interrupt vector address
for i, x in enumerate(AsmDirect.INTERRUPT_VECTOR):
    if l.d.get(x[1]):
        AsmDirect.INTERRUPT_VECTOR[i][1] = l.d.get(x[1])

# print assemble info
if options.debug != None:
    print('Address',end=' ')
    print('{:<26}'.format('Source'),end='')
    print('Machine code(Hex)')
    for data in assembleInfo:
        if data[ADDR] != '':
            print('{0:#x}'.format(data[ADDR],),end='  ')
            print('{:<25}'.format(data[LINE],),end='')
            for j in data[OPCODE]:
                print(' ' + '{0:04x}'.format(j) + ' ',end='')
            print()
        else:
            print('        ',end='')
            print(data[LINE])
    sys.exit()

# step assemble mode
if options.step != None:
    stepasm.stepasm(assembleInfo)
    sys.exit()

# Make intel hex format
# Machine code
OpcodeList = []
for data in assembleInfo:
    for opcode in data[OPCODE]:
        OpcodeList.append(opcode)

data = Get1BytesList(OpcodeList)
msp430_bin2ihex.MakeIntelHexLines(AsmDirect.ORG, data)

# Interrupt vector
tmp = []
for x in AsmDirect.INTERRUPT_VECTOR:
    tmp.append(x[1])

data = []
for x in tmp:
    data.append( x & 0x00ff)
    data.append((x & 0xff00) >> 8)

msp430_bin2ihex.MakeIntelHexLines(0xffe0, data)
print(':00000001FF')
sys.exit()
