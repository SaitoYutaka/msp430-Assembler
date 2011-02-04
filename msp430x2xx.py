import re
import unittest
import unittest_msp430x2xx

def GetIntValue(str):
    if re.match('#{0,1}0x[a-fA-F0-9]+',str):
        base = 16
    elif re.match('#{0,1}-{0,1}[0-9]+',str):
        base = 10
    else: return None
    str = str.replace('#','')
    return int(str,base)

class OPcode(object):
    def __init__(self):
        self.DOUBLE = 0
        self.SINGLE = 1
        self.JUMP   = 2
        self.mnemonic = (
                ("rrc",   0x1000 , self.SINGLE ),
                ("swpb",  0x1080 , self.SINGLE ),
                ("rra",   0x1100 , self.SINGLE ),
                ("sxt",   0x1180 , self.SINGLE ),
                ("push",  0x1200 , self.SINGLE ),
                ("call",  0x1280 , self.SINGLE ),
                ("reti",  0x1300 , self.SINGLE ),
                ("jne",   0x2000 , self.JUMP ),
                ("jnz",   0x2000 , self.JUMP ),
                ("jeq",   0x2400 , self.JUMP ),
                ("jz",    0x2400 , self.JUMP ),
                ("jnc",   0x2800 , self.JUMP ),
                ("jc",    0x2C00 , self.JUMP ),
                ("jn",    0x3000 , self.JUMP ),
                ("jge",   0x3400 , self.JUMP ),
                ("jl",    0x3800 , self.JUMP ),
                ("jmp",   0x3C00 , self.JUMP ),
                ("mov",   0x4000 , self.DOUBLE ),
                ("add",   0x5000 , self.DOUBLE ),
                ("addc",  0x6000 , self.DOUBLE ),
                ("subc",  0x7000 , self.DOUBLE ),
                ("sub",   0x8000 , self.DOUBLE ),
                ("cmp",   0x9000 , self.DOUBLE ),
                ("dadd",  0xA000 , self.DOUBLE ),
                ("bit",   0xB000 , self.DOUBLE ),
                ("bic",   0xC000 , self.DOUBLE ),
                ("bis",   0xD000 , self.DOUBLE ),
                ("xor",   0xE000 , self.DOUBLE ),
                ("and",   0xF000 , self.DOUBLE ),
            )
    def GetOPcode(self, nm):
        bwmode = 0
        nm = nm.lower()
        if nm[-2:] == ".b":
            bwmode = 0x0040
            nm = nm[:-2]
        elif nm[-2:] == ".w":
            nm = nm[:-2]
        for x in self.mnemonic:
            if nm.lower() == x[0]:
                return x[2], x[1] | bwmode
        return None, None

class Register(object):
    def __init__(self):
        self.dicReg = (
            ("R0",0),
            ("PC",0),
            ("R1",1),
            ("SP",1),
            ("R2",2),
            ("GC1",2), 
            ("SR",2), 
            ("R3",3),
            ("GC2",3),
            ("R4",4), 
            ("R5",5), 
            ("R6",6),
            ("R7",7),
            ("R8",8), 
            ("R9",9),
            ("R10",10),
            ("R11",11), 
            ("R12",12),
            ("R13",13),
            ("R14",14), 
            ("R15",15),
            )

    def getRegNum(self, reg):
        for x in self.dicReg:
            if reg == x[0]:return x[1]
        return None

class AddressingMode(Register, object):
    def __init__(self):
        Register.__init__(self)
        self.REGISTERMODE          = 0
        self.IMMEDIATEMODE         = 1
        self.INDEXEDMODE           = 2
        self.ABSOLUTEMODE          = 3
        self.INDIRECTAUTOINCREMENT = 4
        self.INDIRECTREGISTERMODE  = 5
        self.SYNBOLICMODE          = 6

    def GetAddressingMode(self,src):
        if self.getRegNum(src) != None:
            return self.REGISTERMODE
        if   src[0]  == "#":
            return self.IMMEDIATEMODE
        elif src[-1] == ")":
            return self.INDEXEDMODE
        elif src[0]  =="&":
            return self.ABSOLUTEMODE
        elif src[0]  == "@" and src[-1] == "+": 
            return self.INDIRECTAUTOINCREMENT
        elif src[0]  == "@":
            return self.INDIRECTREGISTERMODE
        elif GetIntValue(src) != None:
            return self.SYNBOLICMODE
        else:
            return None

class ConstantGeneratorRegister(object):
    def __init__(self):
        self.CGval = (4,8,0,1,2,-1)
        self.CGReg = ((2,2),(2,3),(3,0),(3,1),(3,2),(3,3))

    def IsConstangGenerator(self, str):
        if str[0] != '#': return False
        val = GetIntValue(str)
        if val != None:
            return val in self.CGval

    def GetCGval(self, str):
        if self.IsConstangGenerator(str) == False:
            return None
        val = GetIntValue(str)
        for x, y in zip(self.CGval, self.CGReg):
            if val == x:
                return y

class MSP430x2xx(OPcode, AddressingMode, ConstantGeneratorRegister, object):
    def __init__(self):
        OPcode.__init__(self)
        AddressingMode.__init__(self)
        ConstantGeneratorRegister.__init__(self)

    def _GetSource(self, str):
        srcadmode = self.GetAddressingMode(str)
        if   srcadmode == self.REGISTERMODE:
            SReg, As = self.getRegNum(str), 0
        elif srcadmode == self.SYNBOLICMODE:
            SReg, As = 0, 1
        elif srcadmode == self.ABSOLUTEMODE:
            SReg, As = 2, 1
        elif srcadmode == self.INDIRECTREGISTERMODE:
            str = str.replace('@','')
            SReg, As = self.getRegNum(str), 2
        elif srcadmode == self.INDIRECTAUTOINCREMENT:
            str = str.replace('@','')
            str = str.replace('+','')
            SReg, As = self.getRegNum(str), 3
        elif srcadmode == self.IMMEDIATEMODE:
            SReg, As = 0, 3
        elif srcadmode == self.INDEXEDMODE:
            str = str[str.find('('):]
            str = str.replace('(','')
            str = str.replace(')','')
            SReg, As = self.getRegNum(str), 1
        else:
            SReg, As = None, None
        return SReg, As

    def _GetDestination(self, str):
        destadmode = self.GetAddressingMode(str)
        if destadmode == self.REGISTERMODE:
            drnum = self.getRegNum(str)
            DReg, Ad = drnum, 0
        elif destadmode == self.INDEXEDMODE:
            str = str[str.find('('):]
            str = str.replace('(','')
            str = str.replace(')','')
            drnum = self.getRegNum(str)
            DReg, Ad = drnum, 1
        elif destadmode == self.SYNBOLICMODE:
            DReg, Ad = 0, 1
        elif destadmode == self.ABSOLUTEMODE:
            DReg, Ad = 2, 1
        else:
            DReg, Ad = None, None
        return DReg, Ad

    def __GetDoubleOperandVal(self, sreg, dreg):
        if self.IsConstangGenerator(sreg):
            SReg, As = self.GetCGval(sreg)
        else:
            SReg, As = self._GetSource(sreg)
        DReg, Ad = self._GetDestination(dreg)
        return [SReg, As, DReg, Ad]

    def __GetSingleOperandVal(self, reg):
        DSReg, Ad = self._GetDestination(reg)
        return [DSReg, Ad]

    def __littleendian(self, num):
        tmp1 = num & 0x00ff; tmp1 <<= 8
        tmp2 = num & 0xff00; tmp2 >>= 8
        return  tmp1 | tmp2

    def __linetolist(self, source):
        listSource = []
        tmp = source.split(" ")
        for x in tmp: listSource += x.split(",")
        ret = []
        for y in listSource:
            if y != '': ret.append(y)
        return ret

    def _GetNextWord(self, src):
        admode = self.GetAddressingMode(src)
        if admode == self.IMMEDIATEMODE or \
           admode == self.SYNBOLICMODE:
            src = src.replace('#','')
        elif admode == self.INDEXEDMODE:
            src = src[0:src.find('(')]
        elif admode == self.ABSOLUTEMODE:
            src = src.replace('&','')
        elif admode == self.INDIRECTAUTOINCREMENT or \
             admode == self.INDIRECTREGISTERMODE  or \
             admode == self.REGISTERMODE or \
             admode == None:
            return None
        srcbyte = GetIntValue(src)
        return srcbyte

    def _MakeErrorMsg(self, source, pos, errmsg):
        errorstr = ''
        for x in source:
            errorstr += x + ' '
        errorstr += '\n'
        if pos == 0:
            errorstr += '^\n'
        elif pos == 1:
            num = errorstr.find(' ') + 1 
            errorstr += ' ' * num + '^\n'
        elif pos == 2:
            pass

        errorstr += errmsg
        return errorstr

    def _MakeErrorMsg(self, source, pos, errmsg):
        errorstr = ''
        for x in source:
            errorstr += x + ' '
        errorstr += '\n'

        num = 0
        for x in list(range(pos)):
            num = num + errorstr[num:].find(' ') + 1
        errorstr += ' ' * num + '^\n'
        errorstr += errmsg
        return errorstr

    def _IsSyntaxError(self, list, operand):
        if operand == self.DOUBLE:
            w = 3
        elif operand == self.SINGLE and list[0].lower() == 'reti':
            w = 1
        elif operand == self.SINGLE and list[0].lower() != 'reti':
            w = 2
        elif operand == self.JUMP:
            w = 2
        else: return False

        if len(list) != w: return True
        else: return False

    def _IsLabel(self, liststr):
        pass

    def asm(self, line):
        liststr = []
        liststr = self.__linetolist(line)
        errorstr = ''

        operand, opcode = self.GetOPcode(liststr[0])
        if operand == None and opcode == None:
            errorstr = self._MakeErrorMsg(liststr, 0, 'error')
            return [-1,errorstr]
        
        mcode    = 0
        srcbyte  = None
        destbyte = None

        if self._IsSyntaxError(liststr, operand):
            errorstr = self._MakeErrorMsg(liststr, 0, 'syntax error')
            return [-1,errorstr]

        if self._IsLabel(liststr):
            pass

        if operand == self.DOUBLE:
            SReg, As, DReg, Ad = self.__GetDoubleOperandVal(liststr[1], liststr[2])

            if SReg == None or As == None:
                errorstr = self._MakeErrorMsg(liststr, 1, 'error')
                return [-1,errorstr]
            elif DReg == None or Ad == None:
                errorstr = self._MakeErrorMsg(liststr, 2, 'error')
                return [-1,errorstr]

            SReg = SReg << 8
            As   = As   << 4
            Ad   = Ad   << 7
            for x in (opcode, SReg, Ad, As, DReg): mcode |= x

            if self.IsConstangGenerator(liststr[1]) == False:
                srcbyte  = self._GetNextWord(liststr[1])
            destbyte = self._GetNextWord(liststr[2])

        elif operand == self.SINGLE:
            if opcode != 0x1300: # not reti
                DSReg, Ad = self.__GetSingleOperandVal(liststr[1])
                if DSReg == None or Ad == None:
                    errorstr = self._MakeErrorMsg(liststr, 1, 'error')
                    return [-1,errorstr]

                Ad = Ad << 4
                for x in (opcode, Ad, DSReg): mcode |= x
                srcbyte  = self._GetNextWord(liststr[1])
            else:
                mcode = opcode

        elif operand == self.JUMP:
            srcbyte = GetIntValue('#'+liststr[1])
            bytes = []
            bytes.append(self.__littleendian(opcode | srcbyte))
            return bytes

        bytes = []
        for x in (mcode, srcbyte, destbyte):
            if x != None :bytes.append(self.__littleendian(x))

        return bytes

if __name__ == '__main__':
    unittest.main('unittest_msp430x2xx')
