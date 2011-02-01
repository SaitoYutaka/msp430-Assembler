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
        self.EI_MAG0    = 0 
        self.EI_MAG1    = 1 
        self.EI_MAG2    = 2 
        self.EI_MAG3    = 3 
        self.EI_CLASS   = 4
        self.EI_DATA    = 5 
        self.EI_VERSION = 6 
        self.EI_OSABI   = 7
        self.EI_ABIVERSION = 8
        self.EI_PAD     = 9
        self.EI_NIDENT  = 16 

class ELF_Header(DataTypes, IdentificationIndexes ,object):
    def __init__(self):
        DataTypes.__init__(self)
        IdentificationIndexes.__init__(self)
        self.htable = (
            (self.UNSIGNEDCHAR * self.EI_NIDENT ," e_ident"   ),
            (self.ELF32_HALF        ," etype"     ),
            (self.ELF32_HALF        ," emachine"  ),
            (self.ELF32_WORD        ," eversion"  ),
            (self.ELF32_ADDR        ," eentry"    ),
            (self.ELF32_OFF         ," ephoff"    ),
            (self.ELF32_OFF         ," eshoff"    ),
            (self.ELF32_WORD        ," eflags"    ),
            (self.ELF32_HALF        ," eehsize"   ),
            (self.ELF32_HALF        ," ephentsize"),
            (self.ELF32_HALF        ," ephnum"    ),
            (self.ELF32_HALF        ," eshentsize"),
            (self.ELF32_HALF        ," eshnum"    ),
            (self.ELF32_HALF        ," eshstrndx" ),
            )
        
    def GetSize(self):
        s = 0
        for x in self.htable:
            s += x[0]
        return s

    def _PrintE_Ident(self, magicnum):
        print('{:<15}'.format('Magic:'),end='')
        for x in magicnum:
            print('{0:02x}'.format(x) + ' ', end='')
        print()

        print('{:<15}'.format('Class:'),end='')
        if magicnum[self.EI_CLASS] == 1:print('ELF32')
        elif  magicnum[self.EI_CLASS] == 2:print('ELF64')
        else:print('Invalid class')
        
        print('{:<15}'.format('Data:'),end='')
        if magicnum[self.EI_DATA] == 1:print('little endian')
        elif magicnum[self.EI_DATA] == 2:print('big endian')
        else:print('Invalid data encoding')

        print('{:<15}'.format('Version:'),end='')
        if magicnum[self.EI_VERSION] == 1:print('current')
        else:print('Invalid verwion')

        print('{:<15}'.format('OS/ABI:'),end='')
        print('{0:02x}'.format(magicnum[self.EI_OSABI]))

        print('{:<15}'.format('ABI Version:'),end='')
        print('{0:02x}'.format(magicnum[self.EI_ABIVERSION]))

    def GetHeader(self, data):
        print('ELF Header:')
        q = collections.deque()
        for b in data: q.append(b)

        magicnum = []
        for x in list(range(self.EI_NIDENT)):
            magicnum.append(q.popleft())
        self._PrintE_Ident(magicnum)
        
        magicnum = []
        for x in list(range(self.ELF32_HALF)):
            magicnum.append(q.popleft())
        print('{:<15}'.format('Type:'),end='')
        if magicnum[0] == 0:print('No file type')
        elif magicnum[0] == 1:print('Relocatable file')
        elif magicnum[0] == 2:print('Executable file')
        elif magicnum[0] == 3:print('Shared object file')
        elif magicnum[0] == 4:print('Core file')

        magicnum = []
        for x in list(range(self.ELF32_HALF)):
            magicnum.append(q.popleft())
        print('{:<15}'.format('Machine:'),end='')
        for x in magicnum: print('{0:02x}'.format(x)+' ',end='')
        print()

        sys.exit()

        for x in self.htable:
            print('{:<15}'.format(x[1]), end='')
            for b in list(range(x[0])):
                print('{0:02x}'.format(q.popleft()) + ' ', end='')
            print()


f = open(sys.argv[1],'rb')
bytes = f.read()
foo = ELF_Header()
h = bytes[:foo.GetSize()]
foo.GetHeader(h)


#f = open('ELF_Format.pdf','rb')
#bytes = f.read()
#
#dump = ''
#dc   = ''
#cnt = 0
#for x in bytes:
#
#
#    dump += '{0:02x}'.format(x) + ' '
#    if x >= 33 and x <= 126: dc += chr(x)
#    else: dc += '.'
#    #    cnt += 1
#    if cnt >= 16:
#        print(dump, dc)
#        cnt = 0
#        dump = ''
#        dc   = ''
#
#
#f.close()
