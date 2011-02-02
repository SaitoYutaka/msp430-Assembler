import collections
import sys

class DataTypes(object):
    def __init__(self):
        self.ELF32_ADDR    = 4 # 4 Unsignedprogramaddress
        self.ELF32_HALF    = 2 # 2 Unsignedmediuminteger
        self.ELF32_OFF     = 4 # 4 Unsignedfileoffset
        self.ELF32_SWORD   = 4 # 4 Signedlargeinteger
        self.ELF32_WORD    = 4 # 4 Unsignedlargeinteger
        self.UNSIGNEDCHAR  = 1 # 1 Unsignedsmallinteger

class IdentificationIndexes(object):
    def __init__(self):
        self.EI_MAG0       = 0
        self.EI_MAG1       = 1
        self.EI_MAG2       = 2
        self.EI_MAG3       = 3
        self.EI_CLASS      = 4
        self.EI_DATA       = 5
        self.EI_VERSION    = 6
        self.EI_OSABI      = 7
        self.EI_ABIVERSION = 8
        self.EI_PAD        = 9
        self.EI_NIDENT     = 16

class ELF_Header(DataTypes, IdentificationIndexes ,object):
    def __init__(self):
        DataTypes.__init__(self)
        IdentificationIndexes.__init__(self)
        self.htable = (
            self.UNSIGNEDCHAR * self.EI_NIDENT ,
            self.ELF32_HALF        ,
            self.ELF32_HALF        ,
            self.ELF32_WORD        ,
            self.ELF32_ADDR        ,
            self.ELF32_OFF         ,
            self.ELF32_OFF         ,
            self.ELF32_WORD        ,
            self.ELF32_HALF        ,
            self.ELF32_HALF        ,
            self.ELF32_HALF        ,
            self.ELF32_HALF        ,
            self.ELF32_HALF        ,
            self.ELF32_HALF        ,
            )
        self.q = collections.deque()
    def GetSize(self):
        s = 0
        for x in self.htable:
            s += x
        return s

    def _PrintHeadName(self, s):
        print('{:{width}}'.format(s+':',align='<',width=15),end='')

    def _PrintE_Ident(self, magicnum):
        self._PrintHeadName('Magic')
        for x in magicnum: print('{0:02x}'.format(x) + ' ', end='')
        print()

        self._PrintHeadName('Class')
        if   magicnum[self.EI_CLASS] == 1: s = 'ELF32'
        elif magicnum[self.EI_CLASS] == 2: s = 'ELF64'
        else:s = 'invalid value : {0:02x}'.format(magicnum[self.EI_CLASS])
        print(s)

        self._PrintHeadName('Data')
        if   magicnum[self.EI_DATA] == 1: s = 'little endian'
        elif magicnum[self.EI_DATA] == 2: s = 'big endian'
        else:s = 'Invalid data encoding : {0:02x}'.format(magicnum[self.EI_DATA])
        print(s)

        self._PrintHeadName('Version')
        if magicnum[self.EI_VERSION] == 1: s = 'current'
        else:s = 'Invalid verwion : {0:02x}'.format(magicnum[self.EI_DATA])
        print(s)

        self._PrintHeadName('OS/ABI')
        print('{0:02x}'.format(magicnum[self.EI_OSABI]))

        self._PrintHeadName('ABI Version')
        print('{0:02x}'.format(magicnum[self.EI_ABIVERSION]))

    def _PrintH(self, w, s):
        magicnum = []
        for x in list(range(w)):
            magicnum.append(self.q.popleft())
        self._PrintHeadName(s)
        for x in magicnum: print('{0:02x}'.format(x)+' ',end='')
        print()

    def GetHeader(self, data):
        print('ELF Header:')
        for b in data: self.q.append(b)

        magicnum = []
        for x in list(range(self.EI_NIDENT)):
            magicnum.append(self.q.popleft())
        self._PrintE_Ident(magicnum)
        magicnum = []
        for x in list(range(self.ELF32_HALF)):
            magicnum.append(self.q.popleft())
        self._PrintHeadName('Type')
        if   magicnum[0] == 0:s = 'No file type'
        elif magicnum[0] == 1:s = 'Relocatable file'
        elif magicnum[0] == 2:s = 'Executable file'
        elif magicnum[0] == 3:s = 'Shared object file'
        elif magicnum[0] == 4:s = 'Core file'
        else:                 s = 'unknown : {0:02x}'.format(magicnum[0])
        print(s)

        head = (
            (self.ELF32_HALF, 'Machine'),
            (self.ELF32_WORD, 'Version'),
            (self.ELF32_ADDR, 'Entry'),
            (self.ELF32_OFF,  'Phoff'),
            (self.ELF32_OFF,  'Shoff'),
            (self.ELF32_WORD, 'Flags'),
            (self.ELF32_HALF, 'Ehsize'),
            (self.ELF32_HALF, 'Phentsize'),
            (self.ELF32_HALF, 'Phnum'),
            (self.ELF32_HALF, 'Shentsize'),
            (self.ELF32_HALF, 'Shnum'),
            (self.ELF32_HALF, 'Shstrndx'),)
        for x in head: self._PrintH(x[0], x[1])

f = open(sys.argv[1],'rb')
bytes = f.read()
foo = ELF_Header()
h = bytes[:foo.GetSize()]
foo.GetHeader(h)


f.close()
