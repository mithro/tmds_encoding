# vim:set ts=4 sw=4 sts=4 expandtab:
"""
This module provides functions for transcoding data using the tmds schema.

The most-used parts of this module are:
  - generate_encodings(int) fetching encoded tokens in the tmds schema of pixel values.

"""

from collections import namedtuple

from bit_utils import bias
from bit_utils import bits
from bit_utils import bint
from bit_utils import rotate
from bit_utils import xor
from bit_utils import xnor
from bit_utils import inv
from bit_utils import bstr
from bit_utils import transitions
from bit_utils import hamming
from bit_utils import ones
from bit_utils import zeros

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


def basic_encode(data_int):

    data = bits(data_int)
    data_ones = ones(data)
    data_zeroes = zeros(data)

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

    return tuple(encoding_base_normal), op, op_encoding


def generate_encodings(data_int):


    encoded, op, op_encoding = basic_encode(data_int)
    inverted = inv(encoded)

    encoded_transitions = transitions(encoded)
    inverted_transition = transitions(inverted)

    # Work out the DC bias of the data word
    # encoding_base_bias = encoding_base_zeros - encoding_base_ones
    encoding_bias = bias(encoded)

    # Build up the set of valid encodings
    encodings = set()
    encodings.add(encoded + (op_encoding, 0))

    # If there is DC bias, add the inverted value also
    if encoding_bias > 0:
        encodings.add(inverted + (op_encoding, 1))

    encodings = list(encodings)

    return list(encodings)


def generate_data_mappings():
    '''
    For the integer range 0 to 255 (valid pixel data), generate the
    mapping tables to and from the token values
    '''

    seen_encodings = set()

    data_encoding_map = {}
    data_encoding_rmap = {}
    for i in range(0, 0xff):
        encodings = generate_encodings(i)
        data_encoding_map[i] = encodings
        for encoding in encodings:
            assert len(encoding) == 10, repr(encoding)
            assert encoding not in seen_encodings
            seen_encodings.add(encoding)
            data_encoding_rmap[tuple(encoding)] = i

    return (data_encoding_map, data_encoding_rmap)


def generate_control_mappings():
    '''
    @return (encoding map, decoding map)

    Generate and return the bit-to-token maps and vice versa
    '''

    seen_encodings = set()
    ctrl_encoding_map = {}
    ctrl_encoding_rmap = {}


    for token, i in sorted(ControlTokens.tokens().items()):
        encoding = bits(i, 10)

        encoding_ones = sum(encoding)
        encoding_zeros = sum(inv(encoding))
        encoding_trans = transitions(encoding)
        assert encoding_ones+encoding_zeros == 10
        assert encoding_trans >= 7


        seen_encodings.add(tuple(encoding))
        ctrl_encoding_map[token] = encoding
        ctrl_encoding_rmap[tuple(encoding)] = token

    return (ctrl_encoding_map, ctrl_encoding_rmap)
