import sys
from collections import deque
from optparse import OptionParser

def MakeIntelHex(record, address, data):
    datacnt = len(data)
    datacnt = str('{0:02x}'.format(datacnt))
    reco    = str('{0:02x}'.format(record))
    address = str('{0:04x}'.format(address))
    dstr = ''
    for x in data:
        dstr += str('{0:02x}'.format(x))
    l = list(reco + datacnt + address + dstr)
    q = deque(l)
    s = []
    tmp = ''
    while len(q) != 0:
        try:
            tmp += q.popleft()
            tmp += q.popleft()
        except:        
            s.append(int(tmp,16))
        s.append(int(tmp,16))

    chsum = MakeCheckSum(s)
    chsum = '{0:02x}'.format(chsum)

    return ':' + datacnt + address + reco + dstr + chsum

def MakeCheckSum(data):
    s = 0
    for x in data: s += x
    st = str('{0:b}'.format(s))
    chsum = ''
    for x in st:
        if x == '1': chsum += '0'
        else:        chsum += '1'
    chsum = int(chsum,2)
    chsum += 1
    chsum = chsum & 0xff
    return chsum

def InitUsage():
    usage = "usage: %prog -d DEVICE [-i file] [-c file] [-v file] > output"
    parser = OptionParser(usage=usage)
    parser.add_option("-d", "--device",default=False,
                      help="Select device name"
                      "[ MSP430G2021,"
                      " MSP430G2031,"
                      " MSP430G2121,"
                      " MSP430G2131,"
                      " MSP430G2221,"
                      " MSP430G2231 ]"
                      )
    parser.add_option("-i", "--info",
                      help="binary file to write information memory")
    parser.add_option("-c", "--code",
                      help="binary file to write main memory(code)")
    parser.add_option("-v", "--vector",
                      help="binary file to write main memory(interrupt vector)")
    return parser

def GetDeviceInfo(options):
    MSP430G2x21_31 = (
        # http://www.ti.com/lit/gpn/msp430g2231
        # name        , info  , code  , vector
        ('MSP430G2021', 0x1000, 0xFE00, 0xFFE0),
        ('MSP430G2031', 0x1000, 0xFE00, 0xFFE0),
        ('MSP430G2121', 0x1000, 0xFC00, 0xFFE0),
        ('MSP430G2131', 0x1000, 0xFC00, 0xFFE0),
        ('MSP430G2221', 0x1000, 0xF800, 0xFFE0),
        ('MSP430G2231', 0x1000, 0xF800, 0xFFE0),
        )
    addr_vect = addr_code = addr_info = None

    for info in MSP430G2x21_31:
        if info[0] == options.device:
            if options.info:   addr_info = info[1]
            if options.code:   addr_code = info[2]
            if options.vector: addr_vect = info[3]

    return addr_vect, addr_code, addr_info

def GetList(l):
    ret = []
    for x in l: 
        if x: ret.append(x)
    return ret

def MakeIntelHexLines(addr, data):
    offset = 0;cnt = 0; h = []
    intelh = ''
    for x in data:
        h.append(x)
        if cnt == 15:
            intelh = MakeIntelHex(0, addr + offset, h)
            print(intelh)
            h = []; cnt = 0; 
            offset += 16
            continue
        cnt += 1
    if cnt != 0:
        intelh = MakeIntelHex(0, addr + offset, h)
        print(intelh)

if __name__ == "__main__":
    parser = InitUsage()
    options, args = parser.parse_args()
 
    if not options.device:
        print('unknown device')
        parser.print_usage()
        sys.exit()

    addr_vect, addr_code, addr_info = GetDeviceInfo(options)

    if addr_vect == None and \
       addr_code == None and \
       addr_info == None:
        print(options.device + ': unknown device')
        parser.print_usage()
        sys.exit()

    addrs = GetList([addr_info, addr_code, addr_vect])
    files = GetList([options.info, options.code, options.vector])

    for file, addr in zip(files, addrs):
        try:
            f = open(file,'rb')
        except:
            print(file + ': No such file')
            sys.exit()

        try:
            data = f.read()
        except:
            print(file + ': Could not read')
            f.close()
            sys.exit()

        f.close()

        MakeIntelHexLines(addr, data)

    print(':00000001FF')
