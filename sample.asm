;; LED blink
.org 0xf800
	;; Initialize the SP
	MOV #0x280, SP
	;; Stop watchdog timer
	MOV #0x5a80, &WDTCTL
	MOV MAIN, PC
MAIN:
	;; Initialize LED pins
	BIS.B #0x0041, &P1DIR
	BIS.B #0x0041, &P1OUT
	;; Set ACLK to use internal VLO (12 kHz clock)
	BIS.B #0x0020, &BCSCTL3
	;; Set TimerA to use auxiliary clock in UP mode
	MOV #0x0110, &TACTL
	;; Enable the interrupt for TACCR0 match
	MOV #0x0010, &TACCTL0
	MOV #11999, &TACCR0
	;; Enable global interrupts
	MOV #0x0008, R15
	MOV R15, R2
	;; Loop forever
LOOP:
	JMP LOOP
	;; Interrupt
TA0:
	XOR.B #0x41,&P1OUT
	RETI
	
;; Power-Up
.iv31 0xf800
;; Timer_A2
.iv25 TA0

