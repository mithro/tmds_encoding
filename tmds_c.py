# vim:set ts=4 sw=4 sts=4 expandtab:

from bit_utils import *
import tmds_tokens

# FIXME: Use something like jinja

def tmds_pixel_to_encoded():
    s = []

    s.append("""\
#include "tmds.h"

struct tmds_token_encoded_choice tmds_pixel_to_encoded[0xff+1] = {
""")

    for i in range(0, 256):
        tokens = list(tmds_tokens.DataToken.mapping(i))

        if len(tokens) == 1:
            negative = tokens[0]
            positive = tokens[0]
        else:
            if bias(tokens[0]) > bias(tokens[1]):
                positive, negative = tokens
            else:
                negative, positive = tokens

        s.append("""\
    [0x{:02x}] = {{
        /* {!r} */
        .positive = {{
            .A={}, .B={}, .C={}, .D={}, .E={}, .F={}, .G={}, .H={}, .X={}, .I={}, .bias={bias}
        }},
""".format(i, positive, *positive, bias=bias(positive)))

        if len(tokens) == 1:
            tokens.append(tokens[0])

        s.append("""\
        /* {!r} */
        .negative = {{
            .A={}, .B={}, .C={}, .D={}, .E={}, .F={}, .G={}, .H={}, .X={}, .I={}, .bias={bias}
        }}
    }},
""".format(i, negative, *negative, bias=bias(negative)))


    s.append("""\
};
""")
    return "".join(s)


def tmds_encoded_to_token():

    s = []
    s.append("""
#include "tmds.h"

struct tmds_token tmds_encoded_to_token[MASK_10BIT+1] = {
""")

    for i in range(0, 2**10):
        bi = bits(i, n=10)
        try:
            token = tmds_tokens.DataToken.rmapping(bi)
            s.append("""\
    [0x{:03x}] = {{ 
        /* {!r} */
        .type = TMDS_PIXEL_10b8b,
        .data = {{
            .pixel = 0x{:02x},
        }},
    }},
""".format(i, token, token.data))
            continue
        except AssertionError:
            pass

        try:
            token = tmds_tokens.ControlToken.rmapping(bi)
            s.append("""\
    [0x{:x}] = {{ 
        /* {!r} */
        .type = TMDS_CTRL_10b2b,
        .data = {{
            .c0 = {c0},
            .c1 = {c1},
        }},
    }},
""".format(i, token, c0=token.c0, c1=token.c1))
            continue
        except AssertionError:
            pass

        s.append("""\
    [0x{:x}] = {{
        .type = TMDS_ERROR,
        .data = {{
            0
        }},
    }},
""".format(i))

    s.append("""\
};
""")
    return "".join(s)


if __name__ == "__main__":

    import sys
    import os
    func = os.path.splitext(sys.argv[1])[0]
    print("""\
/**
 * {} is a generated file!
 * DO NOT MODIFY!
 */
""".format(func))
    exec("s = {}()".format(func))
    print(s)
