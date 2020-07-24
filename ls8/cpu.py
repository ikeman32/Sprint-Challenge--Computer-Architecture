"""CPU functionality."""

import sys
# ALU ops
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
DIV = 0b10100011  # divide
MOD = 0b10100100

INC = 0b01100101  # increment
DEC = 0b01100110  # decrement

CMP = 0b10100111  # compare regA with regB

AND = 0b10101000
NOT = 0b01101001
OR = 0b10101010
XOR = 0b10101011
SHL = 0b10101100  # shift left
SHR = 0b10101101  # shift right

# PC mutators
CALL = 0b01010000  # call subroutine
RET = 0b00010001  # return

INT = 0b01010010  # interupt
IRET = 0b00010011  # interupt return

JMP = 0b01010100  # jump
JEQ = 0b01010101  # jump if equal
JNE = 0b01010110  # jump if false
JGT = 0b01010111  # jump greater-than
JLT = 0b01011000  # jump less-than
JLE = 0b01011001  # jump less-than or equal
JGE = 0b01011010  # jump greater-than or equal

# others
NOP = 0b00000000  # no operation, do nothing

HLT = 0b00000001  # halt

LDI = 0b10000010  # set reg value to integer

LD = 0b10000011  # load regA with regB
ST = 0b10000100  # store regB in regA

PUSH = 0b01000101  # push to stack
POP = 0b01000110  # pop from stack

PRN = 0b01000111  # print number
PRA = 0b01001000  # print alpha character

ALU = {ADD, SUB, MUL, DIV, MOD, INC, DEC, CMP, AND, NOT, OR, XOR, SHL, SHR}


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0
        self.reg[8-1] = 0xF4

    def load(self, file_name):
        """Load a program into memory."""
        # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     LDI,  # LDI R0,8
        #     NOP,
        #     0b00001000,
        #     PRN,  # PRN R0
        #     NOP,
        #     HLT,  # HLT
        # ]
        address = 0
        try:
            
            with open('examples/' + file_name) as file:
                for line in file.readlines():
                    l = line.split('#')[0]
                    inst = l.strip()
                    if inst == '':
                        continue
                    self.ram[address] = int(inst, 2)
                    address += 1
        except:
            # print('Load Exception')
            pass
        

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        elif op == SUB:
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == DIV:
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == MOD:
            self.reg[reg_a] %= self.reg[reg_b]
        elif op == INC:
            if reg_a:
                reg_a += 1
            else:
                reg_b += 1
        elif op == DEC:
            if reg_a:
                reg_a -= 1
            else:
                reg_b -= 1
        elif op == CMP:
            if self.reg[reg_a] == self.reg[reg_b]:
                self.JEQ = 1
            else:
                self.JEQ = 0

            if self.reg[reg_a] < self.reg[reg_b]:
                self.JLT = 1
            else:
                self.JLT = 0

            if self.reg[reg_a] > self.reg[reg_b]:
                self.JGT = 1
            else:
                self.JGT = 0

        elif op == AND:
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == OR:
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == XOR:
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == SHL:
            self.reg[reg_a] <<= self.reg[reg_b]
        elif op == SHR:
            self.reg[reg_a] >>= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, mem):
        return self.ram[mem]

    def ram_write(self, mem, value):
        self.ram[mem] = value
        return self.ram[mem]

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        
        while True:
            pc = self.pc
            inst = self.ram_read(pc)
            # print('inst',inst)
            if inst in ALU:
                # self.trace()
                reg_a = self.ram_read(pc + 1)
                reg_b = self.ram_read(pc + 2)
                self.alu(inst, reg_a, reg_b)
                self.pc += 3
            elif inst is HLT:
                print('Halted')
                sys.exit()
            elif inst is PRN:
                self.handle_prn(pc)
                self.pc += 2          
            elif inst is LDI:
                # print('yes')
                self.handle_ldi(pc)
                self.pc += 3
            elif inst is PUSH:
                # print('push')
                self.handle_push(pc)

                self.pc += 2
            elif inst is POP:
                # print('pop')
                self.handle_pop(pc)

                self.pc +=2
            elif inst is CALL:
                # print('call')
                self.handle_call(pc)
            elif inst is RET:
                # print('ret')
                self.handle_ret()
            elif inst is NOP:
                self.pc += 1
            else:
                self.trace() 
                 

            # pc += 1
            # print(pc)

    def handle_prn(self, pc):
        prn = self.ram_read(pc + 1)
        print(self.reg[prn])

    def handle_ldi(self, pc):
        # print(pc)
        index = self.ram[pc + 1]
        # print(index)
        value = self.ram[pc + 2]
        # print(value)
        self.reg[index] = int(value)

    def handle_push(self, pc):
        # decrement the Stack Pointer
        self.reg[7] -= 1
        # register index
        reg = self.ram[pc + 1]
        # value to place in the register
        value = self.reg[reg]
        # get the Stack Pointer
        sp = self.reg[7]
        # Place value in to ram
        self.ram[sp] = value

    def handle_pop(self, pc):
        # get Stack Pointer
        sp = self.reg[7]
        #register index
        reg = self.ram[pc + 1]
        # Value to place in register
        value = self.ram[sp]
        #place value into register
        self.reg[reg] = value
        #increment the register Stack Pointer
        self.reg[7] += 1

    def handle_call(self, pc):
        # register index
        reg = self.ram[pc + 1]
        # get address to function
        address = self.reg[reg]

        ret_address = pc + 2
        # decrement the Stack Pointer
        self.reg[7] -= 1
        # get the Stack Pointer
        sp = self.reg[7]
        #set return address in memory
        self.ram[sp] = ret_address
        self.pc = address
        # self.trace()

    def handle_ret(self):
        sp = self.reg[7]
        ret_address = self.ram[sp] 
        self.reg[7] += 1
        self.pc = ret_address
