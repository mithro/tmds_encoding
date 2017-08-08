# vim:set ts=4 sw=4 sts=4 expandtab:
"""

TMDS 8b/10b Encoding
==========================================================================

Transition-minimized differential signaling (TMDS), a technology for
transmitting high-speed serial data, is used by the DVI and HDMI video
interfaces, as well as by other digital communication interfaces.

The 10-bit TMDS symbol can represent either an 8-bit data value during normal
data transmission, or 2 bits of control signals during screen blanking.

The method is a form of 8b/10b encoding but using a code-set that **differs**
from the original IBM form. The TMDS is optimised for reducing the number of
transitions in the signal during video data to decrease interference between
the 3 data channels.

Difference between TMDS and IBM 8b/10b encoding schemes.

 * TMDS selects between 3 different encoding schemes depending on
   audio/video/control data content in a particular time. There are also
   differences in encoding between TMDS data channels.

 * IBM 8b10b uses 5b6b and 3b4b subblocks while TMDS has a dedicated algorithm
   during the video data period.

 * TMDS has special coding for q_out[8] and q_out[9].

 * IBM 8b10b has much tighter control over the DC balance, while TMDS
   introduces the concept of a counter that tracks the disparity.

---

01234567XI
abcdefghxi

bit - 0..7 
a..h == encoded data

bit - 8 - X
x == 1 - Used XOR
x == 0 - Used XNOR

bit - 9 - I
i == 0 - Not inverted
i == 1 - Inverted

--

## Stage 1

This stage chooses either the XOR or XNOR encoding to minimize transitions.

 * XNOR if input byte has *more* 1s than zeros
 * XOR  if input byte has *less* 1s than zeros

Bit 8 (bit x) is then set to indicate which encoding was chosen.

This output only depends on the input data.

---

## Stage 2

Second stage chooses to invert the output data or not.

Inversion decision is based on a running DC bias.

----




|         input                ||                output                      |
| disparity // ones | q_m(8)   || q_out(0..7) | q_out(8..10) | disparity_out |
|-------------------|----------||-------------|--------------|---------------|
|    0  OR  4       |   0 XNOR ||  ~q_m  INV  |   01         | -diff_q_m     |
|    0  OR  4       |   1 XOR  ||   q_m       |   10         | +diff_q_m     |

|   >0 AND >4       |   0 XNOR ||  ~q_m  INV  |   01         | -diff_q_m     |
|   >0 AND >4       |   1 XOR  ||  ~q_m  INV  |   11         | -diff_q_m + 2 |

|   <0 AND <4       |   0 XNOR ||   q_m       |   00         | +diff_q_m - 2 |
|   <0 AND <4       |   1 XOR  ||   q_m       |   10         | +diff_q_m     |


  -2 * (~q_m[8]) + (ones - zeros) # inverted
   2 * ( q_m[8]) + (zeros - ones) # not inverted

                   (ones - zeros) # inverted 
                   (zeros - ones) # not inverted

more zeros == +DC
more  ones == -DC



 q_out(0..8) | q_out(9..11) || disparity // ones                               |
-------------|--------------||-------------------------------------------------|
   q_m       |   00         || (d<0 AND o<4 AND q=0)                           | ? AND (A XXX B)
   q_m       |   01         || (d<0 AND o<4 AND q=1) OR ((d=0 OR o=4) AND q=1) | ? AND (A XXX B) OR (? OR (A XXX B))
  ~q_m       |   10         || (d>0 AND o>4 AND q=0) OR ((d=0 OR o=4) AND q=0) | ? AND (A XXX B) OR (? OR (A XXX B))
  ~q_m       |   11         || (d>0 AND o>4 AND q=1)                           | ? AND (A XXX B)


----
----

The TMDS symbol encoding scheme is described in "3.2.2 Encode Algorithm" of the
DVI Revision 1.0 specification;


D == Eight bit pixel data
C0, C1 = Control data
DE == Data Enable

N1{x} == Number of "1" in x
N0{x} == Number of "0" in x

cnt ==
q_out = 10 bits encoded output value



if N1{D} > 4 or (N1{D} == 4 AND D[0] == 0)

 q_m[0] = D[0]
 q_m[1] = q_m[0] XNOR D[1]
 q_m[2] = q_m[0] XNOR D[2]
 ...
 q_m[7] = q_m[0] XNOR D[7]
 q_m[8] = 0

else

 q_m[0] = D[0]
 q_m[1] = q_m[0] XOR D[1]
 q_m[2] = q_m[0] XOR D[2]
 ...
 q_m[7] = q_m[0] XOR D[7]
 q_m[8] = 1

if DE != HIGH
 Cnt(t) == 0
 control tokens
else
 if (Cnt(t-1) == 0) OR (N1{q_m[0:7]} == N0{q_m[0:7]})
   q_out[9] = ~q_m[8]
   q_out[8] = q_m[8]
   q_out[0:7] = (q_m[8] ? q_m[0:7] : ~q_m[0:7])

   if q_m[8] == 0
      Cnt(t) = Cnt(t-1) + (N0{q_m[0:7]} - N1{q_m[0:7]})
   else
      Cnt(t) = Cnt(t-1) + (N1{q_m[0:7]} - N0{q_m[0:7]})
 else
   if ((Cnt(t-1) > 0) AND (N1{q_m[0:7]} > N0{q_m[0:7]})) OR (Cnt(t-1)<0 AND (N0{q_m[0:7]} > N1{q_m[0:7]}))
     q_out[9] = 1
     q_out[8] = q_m[8]
     q_out[0:7] = ~q_m[0:7]
     Cnt(t) = Cnt(t-1) + 2 * q_m[8] + (N0{q_m[0:7]} - N1{q_m[0:7]})
   else
     q_out[9] = 0
     q_out[8] = q_m[8]
     q_out[0:7] = q_m[0:7]
     Cnt(t) = Cnt(t-1) - 2 * ~q_m[8] + (N1{q_m[0:7]} - N0{q_m[0:7]})


"""






from collections import namedtuple


# The control tokens are hard coded to be the following;
_ControlTokenBase = namedtuple("ControlTokens", ["c0", "c1"])

class ControlTokens(_ControlTokenBase):
    """
    Control tokens are designed to have a large number (7) of transitions to
    help the receiver synchronize its clock with the transmitter clock.
    """
    @classmethod
    def tokens(cls):
        return {
            # Control tokens are encoded using the values in the table below.
            #   C0 C1    9........0     C1  C0
            cls(0, 0): 0b1101010100,  #  0   0
            cls(1, 0): 0b0010101011,  #  0   1
            cls(0, 1): 0b0101010100,  #  1   0
            cls(1, 1): 0b1010101011,  #  1   1
        }

    @property
    def token(self):
        return self.tokens()[self]


class BitSequence(tuple):
    # FIXME: Finish this...
    def __new__(cls, *args, n=8):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        else:
            i = args[0]
            assert isinstance(i, int)
            assert i > 0
            assert i < 2**n

            args = bits(i, n)

        assert len(args) == n

        o = tuple.__new__(cls, args)
        o.value = bint(args)
        o.n = n
        return o

    def __int__(self):
        return self.value

    def __bin__(self):
        return "0b"+"".join(reversed(str(b) in self))


class TMDSToken(BitSequence):
    """TMDS Token.

    >>> t1 = TMDSToken([0,0,0,0,0,0,0,0,0,0])
    >>> assert t1.w == (0,0,0,0,0,0,0,0)
    >>> assert t1.x == 0
    >>> assert t1.i == 0
    >>> t2 = TMDSToken([0,0,0,0,0,0,0,0,0,1])
    >>> assert t2.w == (0,0,0,0,0,0,0,0)
    >>> assert t2.x == 0
    >>> assert t2.i == 1
    >>> assert t2 != t1
    >>> t3 = TMDSToken([0,0,0,0,0,0,0,0,1,0])
    >>> assert t3.w == (0,0,0,0,0,0,0,0)
    >>> assert t3.x == 1
    >>> assert t3.i == 0
    >>> assert t3 != t1
    >>> t4 = TMDSToken([0,0,0,0,0,0,0,1,0,0])
    >>> assert t4.w == (0,0,0,0,0,0,0,1)
    >>> assert t4.x == 0
    >>> assert t4.i == 0
    >>> assert t4 != t1
    >>> t5 = TMDSToken([1,1,1,1,1,1,1,0,0,0])
    >>> assert t5.w == (1,1,1,1,1,1,1,0)
    >>> assert t5.x == 0
    >>> assert t5.i == 0
    >>> assert t5 != t1
    >>> t6 = TMDSToken(0,0,0,0,0,0,0,0,0,0)
    >>> assert t1 == t6
    """

    def __new__(cls, b0, b1=None, b2=None, b3=None, b4=None, b5=None, b6=None, b7=None, x=None, i=None):
        if b1 is None:
            assert b0 is not None
            assert b1 is None
            assert b2 is None
            assert b3 is None
            assert b4 is None
            assert b5 is None
            assert b6 is None
            assert b7 is None
            assert x is None
            assert i is None

            b0, b1, b2, b3, b4, b5, b6, b7, x, i = b0

        return BitSequence.__new__(cls, [b0, b1, b2, b3, b4, b5, b6, b7, x, i], n=10)

    @property
    def w(self):
        return self[:-2]

    @property
    def x(self):
        return self[-2]

    @property
    def i(self):
        return self[-1]

    @property
    def op(self):
        if self.x == 0:
            return 'XNOR'
        elif self.x == 1:
            return 'XOR'
        else:
            assert False

    @property
    def inverted(self):
        return self.i == 0
    
    def __str__(self):
        return """\
01234567XI
{}
""" % bstr(self)


    def invert(self):
        """Invert the TMDS Token to the alternative.

        >>> t1 = TMDSToken(1,1,1,1,1,1,1,1,x=1,i=1)
        >>> assert t1.w == (1,1,1,1,1,1,1,1)
        >>> assert t1.x == 1
        >>> assert t1.i == 1
        >>> t2 = t1.invert()
        >>> assert t2.w == (0,0,0,0,0,0,0,0)
        >>> assert t2.x == 1
        >>> assert t2.i == 0
        """
        return TMDSToken(inv(self[:-2])+[self.x]+inv([self.i]))


class ControlToken(TMDSToken):
    pass


class DataToken(TMDSToken):
    pass


class ForbiddenToken(TMDSToken):
    pass





def bits(x, n=8):
    """Convert an int into a bit sequence.

                              0  1  2  3  4  5  6  7
    >>> assert bits(0x00) == [0, 0, 0, 0, 0, 0, 0, 0]
    >>> assert bits(0x01) == [1, 0, 0, 0, 0, 0, 0, 0]
    >>> assert bits(0x10) == [0, 0, 0, 0, 1, 0, 0, 0]
    >>> assert bits(0xff) == [1, 1, 1, 1, 1, 1, 1, 1]

    The 0bXXXXXXXX format is reverse of the bit sequence
    >>> assert bits(0b00000000) == [0, 0, 0, 0, 0, 0, 0, 0]
    >>> assert bits(0b00000001) == [1, 0, 0, 0, 0, 0, 0, 0]
    >>> assert bits(0b00010000) == [0, 0, 0, 0, 1, 0, 0, 0]
    >>> assert bits(0b11111111) == [1, 1, 1, 1, 1, 1, 1, 1]

    If the number doesn't fit, raise an error
    >>> bits(0x100)
    Traceback (most recent call last):
        ...
    AssertionError
    """
    assert isinstance(x, int)
    blist = [int(bit) for bit in reversed("{0:0{n}b}".format(x, n=n))]
    assert len(blist) == n
    return blist


def bint(x):
    """Convert a bit sequence to an int.

    >>> assert bint([0]) == 0
    >>> assert bint([1]) == 1
    >>> assert bint([0,0]) == 0
    >>> assert bint([1,0]) == 1
    >>> assert bint([0,1]) == 2
    """
    return int("0b"+bstr(x)[::-1], 2)


def rotate(b,dir="left"):
    """Rotate a bit sequence.

    Rotate left
    >>> b1 = [0,1,0]
    >>> assert rotate(b1, "left") == [1,0,0]
    >>> assert b1 == [0,1,0]
    >>> assert rotate([0,0,1], "left") == [0,1,0]
    >>> assert rotate([1,0,0], "left") == [0,0,1]
    
    Rotate right
    >>> assert rotate(b1, "right") == [0,0,1]
    >>> assert b1 == [0,1,0]
    >>> assert rotate([0,0,1], "right") == [1,0,0]
    >>> assert rotate([1,0,0], "right") == [0,1,0]
    """
    b_out = list(b)
    if dir in ("left", "<"):
        b_out.append(b_out.pop(0))
    elif dir in ("right", ">"):
        b_out.insert(0, b_out.pop(-1))
    return b_out


def xor(a, b):
    """xor bits together.

    >>> assert xor(0, 0) == 0
    >>> assert xor(0, 1) == 1
    >>> assert xor(1, 0) == 1
    >>> assert xor(1, 1) == 0
    """
    assert a in (0, 1)
    assert b in (0, 1)
    if a == b:
        return 0
    else:
        return 1


def xnor(a, b):
    """xnor bits together.

    >>> assert xnor(0, 0) == 1
    >>> assert xnor(0, 1) == 0
    >>> assert xnor(1, 0) == 0
    >>> assert xnor(1, 1) == 1
    """
    assert a in (0, 1)
    assert b in (0, 1)
    if a == b:
        return 1
    else:
        return 0


def inv(bits):
    """invert a bit sequence.

    >>> assert inv([0, 0]) == [1, 1]
    >>> assert inv([1, 0]) == [0, 1]
    >>> assert inv([0, 1]) == [1, 0]
    >>> assert inv([1, 1]) == [0, 0]
    """
    return [int(not b) for b in bits]


def bstr(bits):
    """Convert a bit sequence to a string.

    >>> assert bstr([0, 0]) == "00"
    >>> assert bstr([0, 1]) == "01"
    >>> assert bstr([1, 0]) == "10"
    >>> assert bstr([1, 1]) == "11"
    """
    return "".join(str(x) for x in bits)


def transitions(bits):
    """Count the number of transitions in a bit sequence.

    >>> assert transitions([0, 0]) == 0
    >>> assert transitions([0, 1]) == 1
    >>> assert transitions([1, 1]) == 0
    >>> assert transitions([1, 0]) == 1
    >>> assert transitions([0, 0, 0]) == 0
    >>> assert transitions([0, 1, 0]) == 2
    >>> assert transitions([1, 1, 0]) == 1
    >>> assert transitions([1, 0, 0]) == 1
    >>> assert transitions([0, 0, 1]) == 1
    >>> assert transitions([0, 1, 1]) == 1
    >>> assert transitions([1, 1, 1]) == 0
    >>> assert transitions([1, 0, 1]) == 2
    """
    transitions = 0
    for i in range(0, len(bits)-1):
        if bits[i] != bits[i+1]:
            transitions += 1
    return transitions


def hamming(a, b):
    """
    Return the hamming distance between to bit sequences.

    >>> assert hamming((0, 0), (1, 1)) == 2
    >>> assert hamming((0, 0), (1, 0)) == 1
    >>> assert hamming((0, 0), (0, 1)) == 1
    >>> assert hamming((0, 0), (0, 0)) == 0
    """
    return sum(xor(b1, b2) for b1, b2 in zip(a, b))


def generate_encodings(data_int):
    data = bits(data_int)
    assert len(data) == 8

    # Count the number of data_ones
    data_ones = sum(data)
    data_zeros = sum(inv(data))
    assert data_ones + data_zeros == 8

    # Decide on which encoding to use based on the number of ones in original data
    if data_ones > 4 or (data_ones == 4 and data[0] == 0):
        op = 'XNOR'
        op_encoding = 0

        xnored_data = [data[0]]
        for bit in data[1:8]:
            xnored_data.append(xnor(bit, xnored_data[-1]))

        encoding_base_normal = xnored_data
    else:
        op = ' XOR'
        op_encoding = 1

        xored_data = [data[0]]
        for bit in data[1:8]:
            xored_data.append(xor(bit, xored_data[-1]))

        encoding_base_normal = xored_data

    encoding_base_invert = inv(encoding_base_normal)
    assert len(encoding_base_normal) == 8
    assert len(encoding_base_invert) == 8

    encoding_base_ones = sum(encoding_base_normal)
    encoding_base_zeros = sum(encoding_base_invert)
    assert encoding_base_ones+encoding_base_zeros == 8

    # The encoded data should have 4 or less transitions in it
    encoding_base_normal_trans = transitions(encoding_base_normal)
    encoding_base_invert_trans = transitions(encoding_base_invert)
    assert encoding_base_normal_trans <= 4
    assert encoding_base_invert_trans <= 4
    assert encoding_base_normal_trans == encoding_base_invert_trans
 
    # Work out the DC bias of the data word
    encoding_base_bias = encoding_base_zeros - encoding_base_ones

    encodings = set()
    if op == 'XNOR':
        encodings.add(tuple(encoding_base_invert + [op_encoding, 1]))
    elif op == ' XOR':
        encodings.add(tuple(encoding_base_normal + [op_encoding, 0]))
    else:
        assert False

    if encoding_base_bias == 0:
        # If the encoding doesn't have a DC bias, there will be only one
        # version.
        assert len(encodings) == 1
    else:
        encodings.add(tuple(encoding_base_normal + [op_encoding, 0])) # Straight encoding
        encodings.add(tuple(encoding_base_invert + [op_encoding, 1])) # Inverted encoding

        assert len(encodings) == 2

    encodings = list(encodings)

    # Check the encodings are the right length
    for encoding in encodings:
        assert len(encoding) == 10
        #assert encoding[-1] != encoding[-2], (data, encodings)

    # Print the table....
    #---------------------------------------
    if len(encodings) == 1:
        full_encoding = "{:^23s}".format(bstr(encodings[0]))
    elif len(encodings) == 2:
        if encodings[0][-1] == 1:
            encodings.reverse()

        full_encoding = "{} | {}".format(bstr(encodings[0]), bstr(encodings[1]))
    else:
        assert False

    print("""\
| {data_int:02X}h | {data} |  {data_ones} | {data_zeros}  || {q_m}  | {op} |  {q_m_ones} | {q_m_zeros}  |  {q_m_trans} | {bias: 4} || {full_encoding} |
""".format(
        data_int=data_int, data=bstr(data), data_ones=data_ones, data_zeros=data_zeros,
        op=op,
        q_m=bstr(encoding_base_normal), q_m_ones=encoding_base_ones, q_m_zeros=encoding_base_zeros, q_m_trans=encoding_base_normal_trans, bias=encoding_base_bias,
        full_encoding=full_encoding,
        ), end="")
    #---------------------------------------

    return list(encodings)


def token_min_distance(token, other_tokens):
    min_distance = len(token)+1

    close_tokens = None
    for otoken in other_tokens:
        distance = hamming(token, otoken)
        if distance < min_distance:
            min_distance = distance
            close_tokens = [otoken]
        elif distance == min_distance:
            close_tokens.append(otoken)

    return min_distance, close_tokens


def main(args):

    seen_encodings = set()

    # --------------------------------------------------------------------
    # --------------------------------------------------------------------

    ctrl_encoding_map = {}
    ctrl_encoding_rmap = {}

    print("""

# Control Tokens
                 | data    || q_m       |      | q_m           (>0=+)||         encoded         |
                 | C0 | C1 || 01234567XI|  OP  | 1s | 0s | ts | bias ||       01234567XI        |
                 |----|----||-----------|------|----|----|----|------||-------------------------|
""", end="")
    for token, i in sorted(ControlTokens.tokens().items()):
        encoding = bits(i, 10)

        encoding_ones = sum(encoding)
        encoding_zeros = sum(inv(encoding))
        encoding_trans = transitions(encoding)
        assert encoding_ones+encoding_zeros == 10
        assert encoding_trans >= 7

        print("""\
                 |  {c0} | {c1}  || {q_m}| {op} |  {q_m_ones} | {q_m_zeros}  |  {q_m_trans} | {bias: 4} || {full_encoding:^23s} |
""".format(
            c0=token.c0, c1=token.c1,
            q_m=bstr(encoding),
            op='    ',
            q_m_ones=encoding_ones,
            q_m_zeros=encoding_zeros,
            q_m_trans=encoding_trans,
            bias=encoding_zeros-encoding_ones,
            full_encoding=bstr(encoding),
            ), end="")

        seen_encodings.add(tuple(encoding))
        ctrl_encoding_map[token] = encoding
        ctrl_encoding_rmap[tuple(encoding)] = token

    # --------------------------------------------------------------------
    # --------------------------------------------------------------------

    print("""

# Data tokens
                                                                     ||         encoded         |
|     | dat bin  | data    || q_m       |      | q_m           (>0=+)||       01234567XI        |
| dat | 01234567 | 1s | 0s || 01234567  |  OP  | 1s | 0s | ts | bias || 01234567Xi | 01234567XI |
|-----|----------|----|----||-----------|------|----|----|----|------||------------|------------|
""", end="")
    data_encoding_map = {}
    data_encoding_rmap = {}
    for i in range(0, 0xff):
        encodings = generate_encodings(i)
        data_encoding_map[i] = encodings
        for encoding in (tuple(x) for x in encodings):
            assert len(encoding) == 10
            assert encoding not in seen_encodings
            seen_encodings.add(encoding)
            data_encoding_rmap[tuple(encoding)] = i

    # Test a couple of hand coded sequences
    #               0  1  2  3  4  5  6  7  X  I
    encoding_10h = (0, 0, 0, 0, 1, 1, 1, 1, 1, 0)
    encoding_EFh = (0, 0, 0, 0, 1, 1, 1, 1, 0, 1)
    assert encoding_10h in seen_encodings, "Didn't find valid encoding for 0x10"
    assert encoding_EFh in seen_encodings, "Didn't find valid encoding for 0xEF"
    assert data_encoding_map[0x10] == [encoding_10h,], (data_encoding_map[0x10], hex(data_encoding_rmap[encoding_10h]))
    assert data_encoding_map[0xEF] == [encoding_EFh,], (data_encoding_map[0xEF], hex(data_encoding_rmap[encoding_EFh]))

    # Work out the "forbidden sequences"
    forbidden = []

    invalid_count = 0
    valid_count = 0
    print("""

# All encodings

| encoding               ||   |data
| hex  | bin        | ts || v?|ctrl |
|------|------------|----||---|-----|""")
    for i in range(0, 2**10):
        encoding = tuple(bits(i, n=10))
        assert len(encoding) == 10

        encoding_trans = transitions(encoding)

        data_token = data_encoding_rmap.get(encoding, None)
        ctrl_token = ctrl_encoding_rmap.get(encoding, None)
        valid = data_token is not None or ctrl_token is not None
        assert (not valid) or (encoding in seen_encodings)
        if valid:
            valid_count += 1
        else:
            assert encoding not in forbidden
            forbidden.append(encoding)
            invalid_count += 1

        if ctrl_token:
            assert not data_token
            token_str = bstr(ctrl_token)+'c'
        elif data_token:
            assert not ctrl_token
            token_str = "{:02X}h".format(data_token)
        else:
            token_str = "   "
        print("| {:03X}h | {} | {:2} || {:d} | {:3s} |".format(i, bstr(encoding), encoding_trans, valid, token_str))

    assert len(seen_encodings) == valid_count
    assert len(forbidden) == invalid_count

    print()
    print(" {} valid encodings ({} control), {} forbidden, out of {}".format(len(seen_encodings), len(ControlTokens.tokens()), len(forbidden), 2**10))
    assert (len(seen_encodings)+len(forbidden)) == (2**10)
    print()

    # --------------------------------------------------------------------
    # --------------------------------------------------------------------

    print()
    print("Forbidden tokens distance:")

    forbidden_really = []
    forbidden_correctable = []

    # See how many valid tokens are equally distant away from the forbidden token
    for encoding in sorted(forbidden):
        min_distance, encodings = token_min_distance(encoding, seen_encodings)

        if True:
            extra = "           "
        if min_distance > 1:
            forbidden_really.append(encoding)
            extra = "REALLY FORB"
        if len(encodings) == 1:
            forbidden_correctable.append(encoding)
            extra = "CORRECTABLE"

        assert encodings
        print(bstr(encoding), min_distance, extra, [bstr(e) for e in sorted(encodings)])

    print()
    print(" {} correctable (out of {} - {}%), {} very forbidden".format(
        len(forbidden_correctable), len(forbidden), int(len(forbidden_correctable)/len(forbidden)*100.0),
        len(forbidden_really)))

    print()
    print()

    # --------------------------------------------------------------------
    # --------------------------------------------------------------------

    print("Control tokens distance:")
    # See how far away the ctrl tokens are from other valid tokens
    for encoding in sorted(ctrl_encoding_rmap):
        min_distance, encodings = token_min_distance(encoding, data_encoding_rmap)

        assert encodings
        print(bstr(encoding), min_distance, [bstr(e) for e in sorted(encodings)])


    print()
    print("Rotated control tokens:")
    for encoding in sorted(ctrl_encoding_rmap):
        print(bstr(encoding))
        for i in range(1, len(encoding)):
            encoding = rotate(encoding)
            min_distance, encodings = token_min_distance(encoding, data_encoding_rmap)
            assert encodings
            print(bstr(encoding), min_distance, [bstr(e) for e in sorted(encodings)])
        print()
    print()
    print()


if __name__ == "__main__":
    import doctest
    results = doctest.testmod()
    assert results.failed == 0
    assert results.attempted > 0
    import sys
    main(sys.argv)
