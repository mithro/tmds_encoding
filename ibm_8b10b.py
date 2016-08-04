"""

IBM 8b/10b encoding -- NOT USED in TMDS
==========================================================================

The 8 input bits of the 8B/10B code are conventionally identified by upper-case
letters A through H, with A the low-order bit and H the high-order bit.

Thus, in standard binary notation, the byte is HGFEDCBA.
The output is 10 bits, "abcdei fghj", where a is transmitted first.

Coding is done in alternate 5-bit and 3-bit sub-blocks. As coding proceeds, the
encoder maintains a "running disparity", the difference between the number of 1
bits and 0 bits transmitted. At the end of sub-block, this disparity is ±1, and
can be represented by a single state bit.

The input and the running disparity bit are used to select the coded bits as
follows:

+-----------------------------------+
|           5b/6b code              |
|--------+-------++--------+--------|
|        |       ||   RD=- | RD=+   |
| input  | EDCBA || abcdei | abcdei |
|--------|-------||--------|--------|
| D.00   | 00000 || 100111 | 011000 |
| D.01   | 00001 || 011101 | 100010 |
| D.02   | 00010 || 101101 | 010010 |
| D.03   | 00011 ||      110001     |
| D.04   | 00100 || 110101 | 001010 |
| D.05   | 00101 ||      101001     |
| D.06   | 00110 ||      011001     |
| D.07   | 00111 || 111000 | 000111 |
| D.08   | 01000 || 111001 | 000110 |
| D.09   | 01001 ||      100101     |
| D.10   | 01010 ||      010101     |
| D.11   | 01011 ||      110100     |
| D.12   | 01100 ||      001101     |
| D.13   | 01101 ||      101100     |
| D.14   | 01110 ||      011100     |
| D.15   | 01111 || 010111 | 101000 |
| D.16   | 10000 || 011011 | 100100 |
| D.17   | 10001 ||      100011     |
| D.18   | 10010 ||      010011     |
| D.19   | 10011 ||      110010     |
| D.20   | 10100 ||      001011     |
| D.21   | 10101 ||      101010     |
| D.22   | 10110 ||      011010     |
| D.23*  | 10111 || 111010 | 000101 |
| D.24   | 11000 || 110011 | 001100 |
| D.25   | 11001 ||      100110     |
| D.26   | 11010 ||      010110     |
| D.27*  | 11011 || 110110 | 001001 |
| D.28   | 11100 ||      001110     |
| D.29*  | 11101 || 101110 | 010001 |
| D.30*  | 11110 || 011110 | 100001 |
| D.31   | 11111 || 101011 | 010100 |
| K.28   |       || 001111 | 110000 |
+--------+-------++--------+--------+

 * - Same code is used for K.x.7


+-----------------------------------+
|           3b/4b code              |
|--------+-------++--------+--------|
|        |       ||   RD=- | RD=+   |
| input  | HGF   ||   fghj | fghj   |
|--------|-------||--------|--------|
| D.x.0  | 000   ||   1011 | 0100   |
| D.x.1  | 001   ||      1001       |
| D.x.2  | 010   ||   0101 |        |
| D.x.3  | 011   ||   1100 | 0011   |
| D.x.4  | 100   ||   1101 | 0010   |
| D.x.5  | 101   ||      1010       |
| D.x.6  | 110   ||      0110       |
| D.x.P7 | 111   ||   1110 | 0001   |
| D.x.A7 | 111   ||   0111 | 1000   |
|--------|-------||--------|--------|
| K.x.0  | 000   ||   1011 | 0100   |
| K.x.1* | 001   ||   0110 | 1001   |
| K.x.2* | 010   ||   1010 | 0101   |
| K.x.3* | 011   ||   1100 | 0011   |
| K.x.4  | 100   ||   1101 | 0010   |
| K.x.5* | 101   ||   0101 | 1010   |
| K.x.6* | 110   ||   1001 | 0110   |
| K.x.7  | 111   ||   0111 | 1000   |
+--------+-------++---------+-------+

There are two encodings for D.x.7, "primary" and "alternate".

The alternate code is used whenever using the primary code would result in bits
eifgh being all the same.

After D.11, D.13 and D.14 when RD=−1, and after D.17, D.18 and D.20 when RD=+1.

This ensures that five consecutive identical bits never appear in a normal
output symbol.


* The alternate encoding for the K.x.y codes with disparity 0 make it possible
  for only K.28.1, K.28.5, and K.28.7 to be "comma" codes that contain a bit
  sequence which can't be found elsewhere in the data stream.
 

---

Using an additional 6B output value, called K.28, and/or the alternate D.x.A7
output in contexts where it would not be otherwise required, an additional 12
non-data "control symbols" can be formed.

Some of these contain a "comma sequence" abcdeifg = 00111110 or 11000001, which
never appears anywhere else in the bit stream, and can be used to establish the
byte boundaries in the data stream.


+--------------------------------------+
|         Control symbols              |
|---------++-------------+-------------|
|         ||     RD = -1 | RD = +1     |
| input   || abcdei fghj | abcdei fghj |
|---------||-------------|-------------|
| K.28.0  || 001111 0100 | 110000 1011 |
| K.28.1* || 001111 1001 | 110000 0110 |
| K.28.2  || 001111 0101 | 110000 1010 |
| K.28.3  || 001111 0011 | 110000 1100 |
| K.28.4  || 001111 0010 | 110000 1101 |
| K.28.5* || 001111 1010 | 110000 0101 |
| K.28.6  || 001111 0110 | 110000 1001 |
| K.28.7* || 001111 1000 | 110000 0111 |
| K.23.7  || 111010 1000 | 000101 0111 |
| K.27.7  || 110110 1000 | 001001 0111 |
| K.29.7  || 101110 1000 | 010001 0111 |
| K.30.7  || 011110 1000 | 100001 0111 |
+---------++-------------+-------------+

[*] --

K28.1, K28.5, and K28.7 are comma symbols, containing the comma sequence
abcdeifg = 00111110 or 11000001. 

K28.7 must not appear after another K.28.7, or it would form a second false
comma sequence.



          Rules for Running Disparity
| Previous RD | RD of 6 or 4 Bit Code | Next RD |
|    -        |        -              | Error   |
|    -        |        0              |   -     |
|    -        |        +              |   +     |
|    +        |        -              |   -     |
|    +        |        0              |   +     |
|    +        |        +              |  Error  |

=================================================================================

"""
