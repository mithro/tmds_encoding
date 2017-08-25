# vim:set ts=4 sw=4 sts=4 expandtab:
"""
Utils for doing operations with bit sequences in Python.
"""

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
    blist = tuple(blist)
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
    assert isinstance(x, (tuple, list))
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
    return tuple(int(not b) for b in bits)


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


def ones(a):
    """
    Return the number of set bits in the sequence.

    >>> assert ones([0, 0]) == 0
    >>> assert ones([0, 1]) == 1
    >>> assert ones([1, 0]) == 1
    >>> assert ones([1, 1]) == 2
    >>> assert ones([1, 1, 1, 0, 1]) == 4
    >>> assert ones([0, 1, 0, 0, 0]) == 1
    """
    return sum(a)


def zeros(a):
    """
    Return the number of cleared bits in the sequence.

    >>> assert zeros([0, 0]) == 2
    >>> assert zeros([0, 1]) == 1
    >>> assert zeros([1, 0]) == 1
    >>> assert zeros([1, 1]) == 0
    >>> assert zeros([1, 1, 1, 0, 1]) == 1
    >>> assert zeros([0, 1, 0, 0, 0]) == 4
    """
    return sum(inv(a))


def bias(a):
    """
    Return the bias of a bit sequence.

    >>> assert bias([0, 1]) == 0
    >>> assert bias([1, 1]) == 2
    >>> assert bias([0, 0]) == 2
    >>> assert bias([0, 1, 1]) == 2
    >>> assert bias([1, 1, 0]) == 2
    >>> assert bias([0, 0, 1]) == 2
    >>> assert bias([1, 1, 1]) == 3
    >>> assert bias([0, 0, 0]) == 2
    >>> assert bias([0, 0, 1]) == 2
    """
    return ones(a) - zeros(a)

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

if __name__ == "__main__":
    import doctest
    results = doctest.testmod()
    assert results.failed == 0
    assert results.attempted > 0
