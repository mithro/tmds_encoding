# vim:set ts=4 sw=4 sts=4 expandtab:
"""
TMDS Tokens

 * Control Tokens (10b2b)
 * Data Tokens (10b8b)
 * (TODO) TEARC Tokens (10b4b)

"""

from bit_utils import *

def grouper(iterable, n, fill=None):
    """
    >>> list(grouper([1,2,3,4,5], 2))
    [(1, 2), (3, 4), (5,)]
    >>> list(grouper([1,2,3,4,5], 2, 'x'))
    [(1, 2), (3, 4), (5, 'x')]
    >>> list(grouper([1,2,3,4,5], 3))
    [(1, 2, 3), (4, 5)]
    >>> list(grouper([1,2,3,4,5], 3, 'x'))
    [(1, 2, 3), (4, 5, 'x')]
    >>> list(grouper([1,2,3,4], 3, 'x'))
    [(1, 2, 3), (4, 'x', 'x')]
    >>> list(grouper([1,2,3,4], 3, 0))
    [(1, 2, 3), (4, 0, 0)]
    """
    out = []
    for i in iterable:
        out.append(i)
        if len(out) == n:
            yield tuple(out)
            out = []

    if out:
        if fill is not None:
            while len(out) < n:
                out.append(fill)
        yield tuple(out)


class BitSequence(tuple):
    """
    >>> a8 = BitSequence(0)
    >>> a8
    (0, 0, 0, 0, 0, 0, 0, 0)
    >>> int(a8)
    0
    >>> a8.__bin__()
    '0b00000000'
    >>> a8.__hex__()
    '0x00'

    >>> a10 = BitSequence(0, n=10)
    >>> a10
    (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    >>> int(a10)
    0
    >>> a10.__bin__()
    '0b0000000000'
    >>> a10.__hex__()
    '0x000'

    >>> b8 = BitSequence(1)
    >>> b8
    (1, 0, 0, 0, 0, 0, 0, 0)
    >>> int(b8)
    1
    >>> b8.__bin__()
    '0b00000001'
    >>> b8.__hex__()
    '0x01'

    >>> b10 = BitSequence(1, n=10)
    >>> b10
    (1, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    >>> int(b10)
    1
    >>> b10.__bin__()
    '0b0000000001'
    >>> b10.__hex__()
    '0x001'

    >>> c8 = BitSequence(128)
    >>> c8
    (0, 0, 0, 0, 0, 0, 0, 1)
    >>> int(c8)
    128
    >>> c8.__bin__()
    '0b10000000'
    >>> c8.__hex__()
    '0x80'

    >>> c10 = BitSequence(256, n=10)
    >>> c10
    (0, 0, 0, 0, 0, 0, 0, 0, 1, 0)
    >>> int(c10)
    256
    >>> c10.__bin__()
    '0b0100000000'
    >>> c10.__hex__()
    '0x100'
    """
    # FIXME: Finish this...
    def __new__(cls, *args, n=8):
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            args = args[0]
        else:
            i = args[0]
            assert isinstance(i, int)
            assert i >= 0
            assert i < 2**n

            args = bits(i, n)

        assert len(args) == n, (len(args), n)

        o = tuple.__new__(cls, args)
        o.value = bint(args)
        o.n = n
        return o

    def __int__(self):
        return self.value

    def __bin__(self):
        return "0b"+"".join(str(b) for b in reversed(self))

    def __hex__(self):
        nibbles = [BitSequence(g, n=4) for g in list(grouper(self, 4, fill=0))]
        return "0x"+"".join(hex(int(n))[2:] for n in reversed(nibbles))

# --

class TMDSToken(BitSequence):
    """TMDS Token.

    >>> t1 = TMDSToken([0,0,0,0,0,0,0,0,0,0])
    >>> assert t1.w == (0,0,0,0,0,0,0,0)
    >>> assert t1.x == 0
    >>> assert t1.i == 0
    >>> t1a = TMDSToken([0,0,0,0,0,0,0,0,0,0])
    >>> assert t1 is t1a
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
    >>> # Testing Invert
    >>> t1 = TMDSToken(1,1,1,1,1,1,1,1,x=1,i=1)
    >>> assert t1.w == (1,1,1,1,1,1,1,1)
    >>> assert t1.x == 1
    >>> assert t1.i == 1
    >>> t2 = t1.invert()
    >>> assert t2.w == (0,0,0,0,0,0,0,0)
    >>> assert t2.x == 1
    >>> assert t2.i == 0

    >>> TMDSToken._encoding_mapping.clear()
    >>> TMDSToken._encoding_mapping
    {}
    """

    _encoding_mapping = {}

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
            assert len(b0) == 10, len(b0)
            b0, b1, b2, b3, b4, b5, b6, b7, x, i = b0

        seq = (b0, b1, b2, b3, b4, b5, b6, b7, x, i)
        if seq not in cls._encoding_mapping:
            cls._encoding_mapping[seq] = BitSequence.__new__(cls, seq, n=10)

        obj = cls._encoding_mapping[seq]
        assert isinstance(obj, cls), (cls, seq, obj, cls._encoding_mapping)
        return obj

    def extra(self):
        return {}

    @classmethod
    def rmapping(cls, bits):
        assert len(bits) == 10
        obj = TMDSToken(bits)
        assert isinstance(obj, cls)
        return obj

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

    def __repr__(self):
        return "{}({}, {})".format(self.__class__.__name__, tuple(self), ", ".join("{}={}".format(k, v) for k,v in self.extra().items()))
 
    def __str__(self):
        n = self.__class__.__name__
        return """\
{} 01234567XI
{}({})
""".format(" "*len(n), n, bstr(self))

    def invert(self):
        """Invert the TMDS Token to the alternative.

        """
        return self.__class__(inv(self[:-2])+[self.x]+inv([self.i]), **self.extra())

# --

class ControlToken(TMDSToken):
    """
    >>> gen = ControlToken.tokens()
    >>> token1 = next(gen)
    >>> assert ControlToken([0,0,1,0,1,0,1,0,1,1], c0=0, c1=0) is token1
    >>> assert ControlToken.mapping(token1.c0, token1.c1) is token1
    >>> assert ControlToken.rmapping((0,0,1,0,1,0,1,0,1,1)) is token1
    >>> token2 = next(gen)
    >>> assert token1 != token2
    """

    _control_mapping = {}

    def __new__(cls, *args, c0=None, c1=None):
        t = TMDSToken.__new__(cls, *args)

        assert c0 in (0, 1)
        assert c1 in (0, 1)
        t.c0 = c0
        t.c1 = c1

        cls._control_mapping[(c0, c1)] = t
        return t

    def extra(self):
        return dict(c0=self.c0, c1=self.c1)

    @classmethod
    def mapping(cls, c0, c1):
        return cls._control_mapping[(c0, c1)]

    @classmethod
    def tokens(cls):
        yield ControlToken([0,0,1,0,1,0,1,0,1,1], c0=0, c1=0)
        yield ControlToken([1,1,0,1,0,1,0,1,0,0], c0=1, c1=0)
        yield ControlToken([0,0,1,0,1,0,1,0,1,0], c0=0, c1=1)
        yield ControlToken([1,1,0,1,0,1,0,1,0,1], c0=1, c1=1)

# --

class DataToken(TMDSToken):
    """
    >>> # Register all the tokens
    >>> for t in DataToken.tokens():
    ...     pass
    >>> # Get them from the mappings
    >>> DataToken.mapping(0x10)
    {DataToken((0, 0, 0, 0, 1, 1, 1, 1, 1, 0), data=0x10)}
    >>> DataToken.mapping(0x00)
    {DataToken((1, 1, 1, 1, 1, 1, 1, 1, 1, 1), data=0x0), DataToken((0, 0, 0, 0, 0, 0, 0, 0, 1, 0), data=0x0)}
    >>> DataToken.rmapping((0, 0, 0, 0, 1, 1, 1, 1, 1, 0))
    DataToken((0, 0, 0, 0, 1, 1, 1, 1, 1, 0), data=0x10)
    >>> DataToken.rmapping((1, 1, 1, 1, 1, 1, 1, 1, 1, 1))
    DataToken((1, 1, 1, 1, 1, 1, 1, 1, 1, 1), data=0x0)
    """

    _data_mapping = {}

    def __new__(cls, *args, data=None):
        t = TMDSToken.__new__(cls, *args)

        assert isinstance(data, int)
        assert data >= 0
        assert data < 256
        t.data = data

        if data not in cls._data_mapping:
            cls._data_mapping[data] = set()

        cls._data_mapping[data].add(t)
        return t

    def extra(self):
        return dict(data=self.data)

    def __repr__(self):
        return "{}({}, data={})".format(self.__class__.__name__, tuple(self), hex(self.data))

    @classmethod
    def tokens(cls):
        """
        """
        for i in range(0, 256):
            for token in cls.generate_tokens(i):
                yield token

    @classmethod
    def mapping(cls, data):
        return cls._data_mapping[data]

    # --------------------------------------------------------------------

    @property
    def bdata(self):
        return bits(self.data)

    @classmethod
    def generate_tokens(cls, data_int):
        """Generate tokens for a given byte.

        Will return either 1 or 2 tokens.

        >>> hex10_tokens = DataToken.generate_tokens(0x10)
        >>> len(hex10_tokens)
        1
        >>> tuple(hex10_tokens[0])
        (0, 0, 0, 0, 1, 1, 1, 1, 1, 0)

        >>> hexEF_tokens = DataToken.generate_tokens(0xEF)
        >>> len(hexEF_tokens)
        1
        >>> tuple(hexEF_tokens[0])
        (0, 0, 0, 0, 1, 1, 1, 1, 0, 1)

        # FIXME: Add a token which encodes too two different tokens.
        """

        data = bits(data_int)
        assert len(data) == 8

        # Count the number of data_ones
        data_ones = ones(data)
        data_zeros = zeros(data)
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
            encodings.add(cls(encoding_base_invert + [op_encoding, 1], data=data_int))
        elif op == ' XOR':
            encodings.add(cls(encoding_base_normal + [op_encoding, 0], data=data_int))
        else:
            assert False

        if encoding_base_bias == 0:
            # If the encoding doesn't have a DC bias, there will be only one
            # version.
            assert len(encodings) == 1
        else:
            encodings.add(cls(encoding_base_normal + [op_encoding, 0], data=data_int)) # Straight encoding
            encodings.add(cls(encoding_base_invert + [op_encoding, 1], data=data_int)) # Inverted encoding

            assert len(encodings) == 2

        encodings = list(encodings)

        assert len(encodings) in (1, 2)

        # Check the encodings are the right length
        for encoding in encodings:
            assert len(encoding) == 10
            #assert encoding[-1] != encoding[-2], (data, encodings)

        return list(encodings)

# --

class ErrorToken(TMDSToken):
    pass

# --

if __name__ == "__main__":
    import doctest
    results = doctest.testmod()
    assert results.failed == 0
    assert results.attempted > 0

    # Check all control tokens have 7 or more transitions
    for ctrl_token in ControlToken.tokens():
        assert transitions(ctrl_token.w) >= 6, (transitions(ctrl_token.w), ctrl_token)

    # Check all data tokens have 4 or less transitions
    for data_token in DataToken.tokens():
        assert transitions(data_token.w) <= 4, data_token

    # Check there are no duplicate tokens
    tokens = list(ControlToken.tokens())+list(DataToken.tokens())
    for t1 in tokens:
        for t2 in tokens:
            if t1 is t2:
                continue
            assert t1 != t2, "%s == %s" % (t1, t2)
