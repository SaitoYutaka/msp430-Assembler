;; sample code
.org 0xf800
	;; Initialize the SP
	MOV #0x280, SP
	;; Stop watchdog timer
	MOV #0x5a80, &WDTCTL
	MOV #0, R15
	CMP #0, R15
	JZ LABEL1
:LABEL2	
	SUB #2, R15
	MOV 0xf880(R15), 0x200(R15)
	JNZ LABEL2
:LABEL1
	MOV #0, R15
	CMP #0, R15
	JZ LABEL3
:LABEL4	
	SUB #1, R15
	MOV.B #0,0x200(R15)
	JNZ LABEL4
:LABEL3	
	MOV #0xf842, PC
:GGGG	
	MOV #0xf87e, PC
	MOV @SP+, PC
	;; Initialize the SP
	MOV #0x280, SP
	;; Stop watchdog timer
	MOV #0x5a80, &WDTCTL
	;; Initialize LED pins
	BIS.B #0x0041, &P1DIR
	BIS.B #0x0041, &P1OUT
	;; Set ACLK to use internal VLO (12 kHz clock)
	BIS.B #0x0020 ,&BCSCTL3
	;; Set TimerA to use auxiliary clock in UP mode
	;; #define TASSEL_1 (1<<8)  /* Timer A clock source select: 1 - ACLK  */
	;; #define MC_1     (1<<4)  /* Timer A mode control: 1 - Up to CCR0 */
	MOV #0x0110, &TACTL
	;; Enable the interrupt for TACCR0 match
	;; #define CCIE                0x0010  /* Capture/compare interrupt enable */
	MOV #0x0010, &TACCTL0
	MOV #11999, &TACCR0
	;; #define WRITE_SR x "amov %0, r2" : : "r" x
	;; #define GIE                 0x0008
	;; Enable global interrupts
	MOV #0x0008, R15
	MOV R15, R2
	;; Loop forever
:LOOP	
	JMP LOOP
	;; Interrupt
:TA0
	XOR.B #0x41,&P1OUT
	RETI
	RETI
.iv31 0xf800
.iv30 GGGG
.iv29 GGGG
.iv28 GGGG
.iv27 GGGG
.iv26 GGGG
.iv25 TA0
.iv24 GGGG
.iv23 GGGG
.iv22 GGGG
.iv21 GGGG
.iv20 GGGG
.iv19 GGGG
.iv18 GGGG
.iv17 GGGG
.iv16 GGGG