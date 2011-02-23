;; sample code
.org 0xf800
	;; Initialize the SP
	MOV #0x200, SP
	;; Stop watchdog timer
	MOV #0x5a80, &WDTCTL
	;; Initialize LED pins
	BIS #0x0041, &P1DIR
	BIS #0x0041, &P1OUT
	;; Set ACLK to use internal VLO (12 kHz clock)
	BIS #0x0020 ,&BCSCTL3
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
	MOV #0x0008, R2
	;; Loop forever
:LOOP
	JMP LOOP
	;; Interrupt
:TA0
	XOR.B #0x41,&P1OUT
	RETI
.iv31 0xf800
.iv25 TA0
