from collections import deque

def MakeIntelHex(record, address, data):
    # if record == '00'
    datacnt = len(data)
    datacnt = datacnt * 2
    datacnt = str('{0:02x}'.format(datacnt))
    address = str('{0:04x}'.format(address))
    dstr = ''
    for x in data:
        dstr += str('{0:04x}'.format(x))
    l = list(record + datacnt + address + dstr)
    q = deque(l)
    chsum = []
    tmp = ''
    while len(q) != 0:
        tmp  = q.popleft()
        tmp += q.popleft()
        chsum.append(int(tmp,16))

    bbbb = MakeCheckSum(chsum)
    bbbb = '{0:02x}'.format(bbbb)

    return ':'+datacnt + address + record + dstr + bbbb

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



