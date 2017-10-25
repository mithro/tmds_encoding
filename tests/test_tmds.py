from bit_utils import bits
from bit_utils import inv
from bit_utils import transitions
from bit_utils import bstr

from tmds import ControlTokens
from tmds import generate_encodings

import tmds

ctrl_tokens_to_code, ctrl_codes_to_tokens = tmds.generate_control_mappings()
data_tokens_to_codes, data_codes_to_tokens = tmds.generate_data_mappings()


def test_encoding():
    '''
    Loop through all possible integers and check the 
    encodings appear sound
    '''

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
            assert is_valid_encoding(encoding)


def is_valid_encoding(coding):
    '''
    Check that the encodings are present in the valid coding tables
    '''

    if coding is None:
        return False

    if coding in ctrl_codes_to_tokens:
        return True

    if coding in data_codes_to_tokens:
        return True

    return False

def test_ctrl():
    '''
    Basic checks that the control tokens are the right size
    '''

    assert len(ctrl_tokens_to_code) == 4
    assert len(ctrl_codes_to_tokens) == 4


def test_examples():

    # Text 0x10 encoding
    assert bits(0x10) == (0, 0, 0, 0, 1, 0, 0, 0)

    # Bits have no major bias, so will be XOR'd
    coding_0x10, op_label, op_encoding = tmds.basic_encode(0x10)
    expected_coding_0x10 = (0, 0, 0, 0, 1, 1, 1, 1)  # 0 bias

    assert op_label == 'XOR'
    assert op_encoding == 1
    assert coding_0x10 == expected_coding_0x10 

    #                              0  1  2  3  4  5  6  7  X  I
    expected_full_encoding_0x10 = (0, 0, 0, 0, 1, 1, 1, 1, 1, 0)
    full_encoding_0x10 = tmds.generate_encodings(0x10)
    assert full_encoding_0x10 == [expected_full_encoding_0x10]
    assert is_valid_encoding(expected_full_encoding_0x10), "Didn't find valid encoding for 0x10"
   

    # # Test 0xEF encoding
    assert bits(0xEF) == (1, 1, 1, 1, 0, 1, 1, 1)

    coding_0xEF, op_label, op_encoding = tmds.basic_encode(0xEF)
    expected_coding_0xEF = (1, 1, 1, 1, 0, 0, 0, 0)  # 0 bias

    assert op_label == 'XNOR'
    assert op_encoding == 0
    assert coding_0xEF == expected_coding_0xEF

    #                              0  1  2  3  4  5  6  7  X  I
    expected_full_encoding_0xEF = (0, 0, 0, 0, 1, 1, 1, 1, 0, 1)

    full_encoding_0xEF = tmds.generate_encodings(0xEF)
    assert full_encoding_0xEF == [expected_full_encoding_0xEF]
    assert is_valid_encoding(expected_full_encoding_0xEF), "Didn't find valid encoding for 0xEF"    
    

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

    assert len(seen_encodings) == valid_count
    assert len(forbidden) == invalid_count
    
    assert (len(seen_encodings)+len(forbidden)) == (2**10)

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
