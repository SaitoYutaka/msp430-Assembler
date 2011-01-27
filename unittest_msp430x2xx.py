import unittest
import msp430x2xx

class TestFunctions(unittest.TestCase):
    def setUp(self):
        pass

    def test_getcode(self):
        self.mnemonic = ( 
            ("rrc",   (1, 0x1000 )) ,
            ("rrc.b", (1, 0x1040 )) ,
            ("swpb",  (1, 0x1080 )) ,
            ("rra",   (1, 0x1100 )) ,
            ("rra.b", (1, 0x1140 )) ,
            ("sxt",   (1, 0x1180 )) ,
            ("push",  (1, 0x1200 )) ,
            ("push.b",(1, 0x1240 )) ,
            ("call",  (1, 0x1280 )) ,
            ("reti",  (1, 0x1300 )) ,
            ("jne",   (2, 0x2000 )) ,
            ("jeq",   (2, 0x2400 )) ,
            ("jnc",   (2, 0x2800 )) ,
            ("jc",    (2, 0x2C00 )) ,
            ("jn",    (2, 0x3000 )) ,
            ("jge",   (2, 0x3400 )) ,
            ("jl",    (2, 0x3800 )) ,
            ("jmp",   (2, 0x3C00 )) ,
            ("mov",   (0, 0x4000 )) , 
            ("add",   (0, 0x5000 )) , 
            ("addc",  (0, 0x6000 )) , 
            ("subc",  (0, 0x7000 )) , 
            ("sub",   (0, 0x8000 )) , 
            ("cmp",   (0, 0x9000 )) , 
            ("dadd",  (0, 0xA000 )) , 
            ("bit",   (0, 0xB000 )) , 
            ("bic",   (0, 0xC000 )) , 
            ("bis",   (0, 0xD000 )) , 
            ("xor",   (0, 0xE000 )) , 
            ("and",   (0, 0xF000 )) ,
            ("xxx",  (None,None)))
        
        self.op = msp430x2xx.OPcode()
        for x in self.mnemonic:
            self.assertEqual(self.op.GetOPcode(x[0]), x[1])
        for x in self.mnemonic:
            self.assertEqual(self.op.GetOPcode(x[0].upper()), x[1])

    def test_getRegNum(self):
        self.dicReg = (
            # (val, return)
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
            ("XX", None),
            )
        self.reg = msp430x2xx.Register()
        for x in self.dicReg:
            self.assertEqual(self.reg.getRegNum(x[0]), x[1])

    def test_GetAddressingMode(self):
        testdata = (
            # (val, return)
            ('R6',0),         # Register mode
            ('0x1234(R6)',2), # Indexed mode
            ('0x1234',6),     # Synbolic mode
            ('&0x1234',3),    # Absolute mode
            ('@R6',5),        # Indirect register mode
            ('@R6+',4),       # Indirect autoincrement
            ('#0x1234',1),    # Immediate mode
            ('xxxxxx',None)
            )
        self.admode = msp430x2xx.AddressingMode()
        for x in testdata:
            self.assertEqual(self.admode.GetAddressingMode(x[0]), x[1])

    def test_GetSource(self):
        testdata = (
            # (val, return)
            ('R6',(6,0)),         # Register mode
            ('0x1234(R6)',(6,1)), # Indexed mode
            ('0x1234',(0,1)),     # Synbolic mode
            ('&0x1234',(2,1)),    # Absolute mode
            ('@R6',(6,2)),        # Indirect register mode
            ('@R6+',(6,3)),       # Indirect autoincrement
            ('#0x1234',(0,3)),    # Immediate mode
            ('xxxxxx',(None,None))
            )
        self.msp = msp430x2xx.MSP430x2xx()
        for x in testdata:
            self.assertEqual(self.msp._GetSource(x[0]),x[1])

    def test_GetDestination(self):
        testdata = (
            # (val, return)
            ('R6',(6,0)),         # Register mode
            ('0x1234(R6)',(6,1)), # Indexed mode
            ('0x1234',(0,1)),     # Synbolic mode
            ('&0x1234',(2,1)),    # Absolute mode
            ('@R6',(None,None)),         # Indirect register mode
            ('@R6+',(None,None)),        # Indirect autoincrement
            ('#0x1234',(None,None)),     # Immediate mode
            ('xxxxxx',(None,None))
            )
        self.msp = msp430x2xx.MSP430x2xx()
        for x in testdata:
            self.assertEqual(self.msp._GetDestination(x[0]),x[1])

    def test_GetNextWord(self):
        testdata = (
            # (val, return)
            ('R6',None),           # Register mode
            ('0x1234(R6)',0x1234), # Indexed mode
            ('0x1234',0x1234),     # Synbolic mode
            ('&0x1234',0x1234),    # Absolute mode
            ('@R6',None),          # Indirect register mode
            ('@R6+',None),         # Indirect autoincrement
            ('#0x1234',0x1234),    # Immediate mode
            ('xxxxxx',None)
            )
        self.msp = msp430x2xx.MSP430x2xx()
        for x in testdata:
            self.assertEqual(self.msp._GetNextWord(x[0]),x[1])

    def test_IsConstangGenerator(self):
        testdata = (
            # (val, return)
            ('#4',True),           
            ('#8',True),           
            ('#0',True),           
            ('#1',True),           
            ('#2',True),           
            ('#-1',True),           
            )
        self.msp = msp430x2xx.ConstantGeneratorRegister()
        for x in testdata:
            self.assertEqual(self.msp.IsConstangGenerator(x[0]),x[1])

    def test_GetCGval(self):
        testdata = (
            # (val, return)
            ('#4',(2,2)),
            ('#8',(2,3)),
            ('#0',(3,0)),
            ('#1',(3,1)),
            ('#2',(3,2)),
            ('#-1',(3,3)),
            )
        self.msp = msp430x2xx.ConstantGeneratorRegister()
        for x in testdata:
            self.assertEqual(self.msp.GetCGval(x[0]),x[1])

    def test_GetIntValue(self):
        testdata = (
            # (val, return)
            ('0xf',0xf),
            ('0xff',0xff),
            ('0xfff',0xfff),
            ('0xffff',0xffff),
            ('#0xf',0xf),
            ('#0xff',0xff),
            ('#0xfff',0xfff),
            ('#0xffff',0xffff),
            ('#0xfffff',0xfffff)
            )
        for x in testdata:
            self.assertEqual(msp430x2xx.GetIntValue(x[0]),x[1])

    def test_asm(self):
        testdata = [
            # (val, return)
            ["MOV #0x280,SP             ",    [0x3140 ,0x8002 ]],
            ["MOV #0x5a80,&0x0120       ",    [0xb240 ,0x805a ,0x2001 ]],
            ["MOV 0xf880(R15),0x200(R15)",    [0x9f4f ,0x80f8 ,0x0002 ]],
            ["BIS.B #0x41,&0x0022       ",    [0xf2d0 ,0x4100 ,0x2200 ]],
            ["BIS.B #0x41,&0x0021       ",    [0xf2d0 ,0x4100 ,0x2100 ]],
            ["MOV #0x280,SP             ",    [0x3140 ,0x8002 ]],
            ["MOV #0x5a80,&0x0120       ",    [0xb240 ,0x805a ,0x2001 ]],
            ["BIS.B #0x41,&0x0022       ",    [0xf2d0 ,0x4100 ,0x2200 ]],
            ["BIS.B #0x41,&0x0021       ",    [0xf2d0 ,0x4100 ,0x2100 ]],
            ["BIS.B #0x20,&0x0053       ",    [0xf2d0 ,0x2000 ,0x5300 ]],
            ["MOV #0x110,&0x0160        ",    [0xb240 ,0x1001 ,0x6001 ]],
            ["MOV #0x10,&0x0162         ",    [0xb240 ,0x1000 ,0x6201 ]],
            ["MOV #0x2edf,&0x0172       ",    [0xb240 ,0xdf2e ,0x7201 ]],
            ["MOV #0x8,R15              ",    [0x3f42 ]],
            ["MOV R15,SR                ",    [0x024f ]],
            ["JMP 0xf874                ",    [0xfc74 ]],
            ["XOR.B #0x41,&0x0021       ",    [0xf2e0 ,0x4100 ,0x2100 ]],
            ["RETI                      ",    [0x0013 ]],
            ]

        self.msp = msp430x2xx.MSP430x2xx()
        for x in testdata:
            self.assertEqual(self.msp.asm(x[0]),x[1])

    def test_MakeErrorMsg(self):
        testdata = (
            # (val, return)
            (['xxx'],'xxx \n^\nerror'),
            (['xxx','xxx'],'xxx xxx \n^\nerror'),
            (['xxx','xxx','xxx'],'xxx xxx xxx \n^\nerror'),
            (['xxx','xxx','xxx','xxx'],'xxx xxx xxx xxx \n^\nerror'),
            )
        self.msp = msp430x2xx.MSP430x2xx()
        for x in testdata:
            self.assertEqual(self.msp._MakeErrorMsg(x[0], 0 ,'error'),x[1])
