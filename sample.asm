	;; sample asm source
	;; 
	MOV #0x280,SP
	MOV #0x5a80,&0x0120
	MOV 0xf880(R15),0x200(R15)
	BIS.B #0x41,&0x0022
	BIS.B #0x41,&0x0021
	MOV #0x280,SP
	MOV #0x5a80,&0x0120
	BIS.B #0x41,&0x0022
	BIS.B #0x41,&0x0021
	BIS.B #0x20,&0x0053
	MOV #0x110,&0x0160
	MOV #0x10,&0x0162
	MOV #0x2edf,&0x0172
	MOV #0x8,R15
	MOV R15,SR
	JMP 0xf874
	XOR.B #0x41,&0x0021
	RETI
	RETI
	rrc R6  
        swpb 0x1234 
        rra R15  
        sxt R15     
        push R15    
        call R15    
        reti  
        jne 123  
        jeq 123     
        jnc 123     
        jc 123      
        jn 123      
        jge 123     
        jl 123      
        jmp 123     
        mov   
        add   
        addc  
        subc  
        sub   
        cmp   
        dadd  
        bit   
        bic   
        bis   
        xor   
        and   