from bit_utils import bits
from bit_utils import inv
from bit_utils import transitions
from bit_utils import bstr

from tmds import ControlTokens
from tmds import generate_encodings

import tmds

ctrl_encode_map, ctrl_decode_map = tmds.generate_control_mappings()
data_encode_map, data_decode_map = tmds.generate_data_mappings()


def test_encoding():

    for i in range(256):

        encoded, op, encoding = tmds.basic_encode(i)
        inverted = tmds.inv(encoded)

        assert len(encoded) == 8
        assert len(inverted) == 8
        assert sum(encoded) + sum(inverted) == 8

        encoded_transitions = transitions(encoded)
        inverted_transition = transitions(inverted)
        assert encoded_transitions <= 4
        assert inverted_transition <= 4
        assert encoded_transitions == inverted_transition

        full_encodings = tmds.generate_encodings(i)

        for encoding in full_encodings:
            assert len(encoding)  == 10
            # assert encoding[-1] != encoding[-2], encoding #, (data, encodings)  # FIXME


def is_valid(token):

    if token is None:
        return False

    if token in ctrl_decode_map:
        return True

    if token in data_decode_map:
        return True

    return False

def test_ctrl():

    assert len(ctrl_encode_map) == 4
    assert len(ctrl_decode_map) == 4



def test_examples():

    # Test a couple of hand coded sequences
    #               0  1  2  3  4  5  6  7  X  I
    encoding_10h = (0, 0, 0, 0, 1, 1, 1, 1, 1, 0)
    encoding_EFh = (0, 0, 0, 0, 1, 1, 1, 1, 0, 1)
    assert is_valid(encoding_10h), "Didn't find valid encoding for 0x10"
    assert is_valid(encoding_EFh), "Didn't find valid encoding for 0xEF"
    # assert data_encode_map[0x10] == (
    #                                   [encoding_10h,],
    #                                   (data_encoding_map[0x10],
    #                                   hex(data_encoding_rmap[encoding_10h]))
    #                                   )

    # assert data_encoding_map[0xEF] == (
    #                                   [encoding_EFh,],
    #                                   (data_encoding_map[0xEF],
    #                                   hex(data_encoding_rmap[encoding_EFh]))
    #                                   )

def test_bits_length():
    for i in range(0, 2**10):
        encoding = tuple(bits(i, n=10))
        assert len(encoding) == 10

def check_forbidden():
    # Work out the "forbidden sequences"
    forbidden = []

    invalid_count = 0
    valid_count = 0

    for i in range(0, 2**10):
        encoding = tuple(bits(i, n=10))
        encoding_trans = transitions(encoding)

        data_token = data_decode_map.get(encoding, None)
        ctrl_token = ctrl_decode_map.get(encoding, None)

        valid_data = is_token_valid(data_token)
        valid_ctrl = is_token_valid(ctrl_token)
        valid = valid_data or valid_ctrl

        if valid:
            valid_count += 1
        else:
            forbidden.append(encoding)
            invalid_count += 1

        if ctrl_token:
            assert not data_token

        elif data_token:
            assert not ctrl_token

    # assert len(seen_encodings) == valid_count
    # assert len(forbidden) == invalid_count
    #
    # assert (len(seen_encodings)+len(forbidden)) == (2**10)

def foo():

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


    # --------------------------------------------------------------------
    # --------------------------------------------------------------------
    # See how far away the ctrl tokens are from other valid tokens
    for encoding in sorted(ctrl_encoding_rmap):
        min_distance, encodings = token_min_distance(encoding, data_encoding_rmap)

        assert encodings


    for encoding in sorted(ctrl_encoding_rmap):
        for i in range(1, len(encoding)):
            encoding = rotate(encoding)
            min_distance, encodings = token_min_distance(encoding, data_encoding_rmap)
            assert encodings