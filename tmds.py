# vim:set ts=4 sw=4 sts=4 expandtab:
"""
This module provides functions for transcoding data using the tmds schema.

The most-used parts of this module are:
  - generate_encodings(int) fetching encoded tokens in the tmds schema of pixel values.

"""

from collections import namedtuple

from bit_utils import bits
from bit_utils import bint
from bit_utils import rotate
from bit_utils import xor
from bit_utils import xnor
from bit_utils import inv
from bit_utils import bstr
from bit_utils import transitions
from bit_utils import hamming

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
    """
    TMDS Token.

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
        return "01234567XI\n{}" % bstr(self)


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

    tpl = ("| {data_int:02X}h | {data} |  {data_ones} | {data_zeros} "
           " || {q_m}  | {op} |  {q_m_ones} | {q_m_zeros}  |  {q_m_trans} "
           "| {bias: 4} || {full_encoding} |")

    print(tpl.format(
        data_int=data_int, data=bstr(data), data_ones=data_ones,
        data_zeros=data_zeros,
        op=op,
        q_m=bstr(encoding_base_normal), q_m_ones=encoding_base_ones,
        q_m_zeros=encoding_base_zeros, q_m_trans=encoding_base_normal_trans,
        bias=encoding_base_bias,
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
