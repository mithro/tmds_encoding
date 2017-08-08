# vim:set ts=4 sw=4 sts=4 expandtab:



"""
# Control Tokens

| data    || q_m       |      | q_m           (>0=+)||         encoded         |
| C0 | C1 || 01234567XI|  OP  | 1s | 0s | ts | bias ||       01234567XI        |
|----|----||-----------|------|----|----|----|------||-------------------------|
|  0 | 0  || 0010101011|      |  5 | 5  |  7 |    0 ||       0010101011        |
|  0 | 1  || 0010101010|      |  4 | 6  |  8 |    2 ||       0010101010        |
|  1 | 0  || 1101010100|      |  5 | 5  |  7 |    0 ||       1101010100        |
|  1 | 1  || 1101010101|      |  6 | 4  |  8 |   -2 ||       1101010101        |


Control tokens distance:
0010101010 2 ['0000001010', '0000100010', '0000101110', '0000111010', '0010000010', '0010001110', '0010111110', '0011100010', '0011101110', '0011111010']
0010101011 2 ['0000001011', '0000100011', '0000101111', '0000111011', '0010000011', '0010001111', '0010111111', '0011100011', '0011101111', '0011111011']
1101010100 2 ['1100000100', '1100010000', '1100011100', '1101000000', '1101110000', '1101111100', '1111000100', '1111010000', '1111011100', '1111110100']
1101010101 2 ['1100000101', '1100010001', '1100011101', '1101000001', '1101110001', '1101111101', '1111000101', '1111010001', '1111011101', '1111110101']

0010101011

   /-----\
00 1010101 0
00 1010101 1
 1 1010101 00
 1 1010101 01

|0         |1         |2
|0123456789|0123456789|0123456789
|----------|----------|----------
|0010101011|0010101011|0010101011
|^         |^         |^
|__/\/\/\/_|\_/\/\/\/_|\_/\/\/\/_




Control sequence will look like this....

+++1010101+++1010101+++1010101+++1010101+++

"""

# Number of transitions ==

# xor(b0, b1) + xor(b1, b2) + xor(b2, b3) + ...


# 0010101011
# 1101010100

from litex.gen import *
from litex.gen.fhdl import verilog


def bint(x):
    """Convert a bit sequence to an int.

    >>> assert bint([0]) == 0
    >>> assert bint([1]) == 1
    >>> assert bint([0,0]) == 0
    >>> assert bint([1,0]) == 1
    >>> assert bint([0,1]) == 2
    """
    return int("0b"+"".join(str(i) for i in x)[::-1], 2)


class ControlTokenPhaseDetector(Module):
    def __init__(self):
        self.input_bits = Signal(20)

        self.phase = Signal(max=10)
        self.detected = Signal(reset=0)

        control_token_zero = [0,0,1,0,1,0,1,0,1,1]
        two_tokens = control_token_zero+control_token_zero

        cases = {'default': [self.phase.eq(0), self.detected.eq(0)]}
        for i in range(0, 10):
            rotated_two_tokens = two_tokens[i:]+two_tokens[:i]

            v = Constant(bint(rotated_two_tokens), (20, False))
            v.format = 'binary'
            cases[v] = [self.phase.eq(i), self.detected.eq(1)]

        self.comb += Case(self.input_bits, cases)


print(verilog.__file__)
print(verilog.convert(ControlTokenPhaseDetector()))
