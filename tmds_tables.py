# vim:set ts=4 sw=4 sts=4 expandtab:

from bit_utils import *
import tmds_tokens

def main(args):
    print("""

# Control Tokens
                 | data    ||      | q_m       | q_m           (>0=+)||         encoded         | encoded       (>0=+)|
                 | C0 | C1 ||      | 01234567  | 1s | 0s | ts | bias ||       01234567XI        | 1s | 0s | ts | bias |
                 |----|----||------|-----------|----|----|----|------||-------------------------|----|----|----|------|
""", end="")

    for token in tmds_tokens.ControlToken.tokens():
        print("""\
                 |  {c0} | {c1}  ||      | {q_m}  |  {q_m_ones} | {q_m_zeros}  |  {q_m_trans} | {q_m_bias: 4} || {encoding:^23s} |  {e_ones} | {e_zeros}  |  {e_trans} | {e_bias: 4} |
""".format(
        # Token data
        c0=token.c0,
        c1=token.c1,
        # q_m info
        q_m=bstr(token.w),
        q_m_op=token.op,
        q_m_ones=ones(token.w),
        q_m_zeros=zeros(token.w),
        q_m_trans=transitions(token.w),
        q_m_bias=bias(token.w),
        # Encoded info
        encoding=bstr(token),
        e_ones=ones(token),
        e_zeros=zeros(token),
        e_trans=transitions(token),
        e_bias=bias(token),
        ),
            end="")

    print("""
|     | dat bin  | data    ||      | q_m       | q_m           (>0=+)||         encoded         | encoded       (>0=+)|
| dat | 01234567 | 1s | 0s ||  OP  | 01234567  | 1s | 0s | ts | bias ||       01234567XI        | 1s | 0s | ts | bias |
|-----|----------|----|----||------|-----------|----|----|----|------||-------------------------|----|----|----|------|
""", end="")
    last_token = None
    for token in tmds_tokens.DataToken.tokens():
        if last_token and last_token.invert() == token:
            print("""\
|     |          |    |    ||      |           |    |    |    |      |""",
                end="")
        else:
            print("""\
| {data:02X}h | {data_bin} |  {data_ones} | {data_zeros}  || {q_m_op:4s} | {q_m}  |  {q_m_ones} | {q_m_zeros}  |  {q_m_trans} | {q_m_bias: 4} |""".format(
                    # Token data
                    data=token.data,
                    data_bin=bstr(token.bdata),
                    data_ones=ones(token.bdata),
                    data_zeros=zeros(token.bdata),
                    # q_m info
                    q_m=bstr(token.w),
                    q_m_op=token.op,
                    q_m_ones=ones(token.w),
                    q_m_zeros=zeros(token.w),
                    q_m_trans=transitions(token.w),
                    q_m_bias=bias(token.w),
                    ),
                end="")


        print("""\
| {encoding:^23s} | {e_ones:2} | {e_zeros:^2} |  {e_trans} | {e_bias: 4} |""".format(
                # Encoded info
                encoding=bstr(token),
                e_ones=ones(token),
                e_zeros=zeros(token),
                e_trans=transitions(token),
                e_bias=bias(token),
                ),
            end="")

        print()
        last_token = token


if __name__ == "__main__":
    import sys
    main(sys.argv)
