import tmds

def test_big(args):

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
