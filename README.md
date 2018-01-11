# TMDS Encoding

Code for understanding TMDS encoding used in DVI and HDMI.

TMDS description is found here - https://docs.google.com/document/d/1v7AJK4cVG3uDJo_rn0X9vxMvBwXKBSL1VaJgiXgFo5A/edit


TMDS 8b/10b Encoding
==========================================================================

Transition-minimized differential signaling (TMDS), a technology for
transmitting high-speed serial data, is used by the DVI and HDMI video
interfaces, as well as by other digital communication interfaces.

The 10-bit TMDS symbol can represent either an 8-bit data value during normal
data transmission, or 2 bits of control signals during screen blanking.

The method is a form of 8b/10b encoding but using a code-set that **differs**
from the original IBM form. The TMDS is optimised for reducing the number of
transitions in the signal during video data to decrease interference between
the 3 data channels.

Difference between TMDS and IBM 8b/10b encoding schemes.

 * TMDS selects between 3 different encoding schemes depending on
   audio/video/control data content in a particular time. There are also
   differences in encoding between TMDS data channels.

 * IBM 8b10b uses 5b6b and 3b4b subblocks while TMDS has a dedicated algorithm
   during the video data period.

 * TMDS has special coding for q_out[8] and q_out[9].

 * IBM 8b10b has much tighter control over the DC balance, while TMDS
   introduces the concept of a counter that tracks the disparity.

---

01234567XI
abcdefghxi

bit - 0..7
a..h == encoded data

bit - 8 - X
x == 1 - Used XOR
x == 0 - Used XNOR

bit - 9 - I
i == 0 - Not inverted
i == 1 - Inverted

--

## Stage 1

This stage chooses either the XOR or XNOR encoding to minimize transitions.

 * XNOR if input byte has *more* 1s than zeros
 * XOR  if input byte has *less* 1s than zeros

Bit 8 (bit x) is then set to indicate which encoding was chosen.

This output only depends on the input data.

---

## Stage 2

Second stage chooses to invert the output data or not.

Inversion decision is based on a running DC bias.

----



|         input     |          |             |  output      |               |
| ----------------- | -------- | ----------- | ------------ | ------------- |
| disparity // ones | q_m(8)   | q_out(0..7) | q_out(8..10) | disparity_out |
|    0  OR  4       |   0 XNOR |  ~q_m  INV  |   01         | -diff_q_m     |
|    0  OR  4       |   1 XOR  |   q_m       |   10         | +diff_q_m     |
|   >0 AND >4       |   0 XNOR |  ~q_m  INV  |   01         | -diff_q_m     |
|   >0 AND >4       |   1 XOR  |  ~q_m  INV  |   11         | -diff_q_m + 2 |
|   <0 AND <4       |   0 XNOR |   q_m       |   00         | +diff_q_m - 2 |
|   <0 AND <4       |   1 XOR  |   q_m       |   10         | +diff_q_m     |


  -2 * (~q_m[8]) + (ones - zeros) # inverted
   2 * ( q_m[8]) + (zeros - ones) # not inverted

                   (ones - zeros) # inverted
                   (zeros - ones) # not inverted

more zeros == +DC
more  ones == -DC


| q_out(0..8) | q_out(9..11) | disparity // ones                               |                                     |
| ----------- | ------------ | ----------------------------------------------- | ----------------------------------- |
|   q_m       |   00         | (d<0 AND o<4 AND q=0)                           | ? AND (A XXX B)                     |
|   q_m       |   01         | (d<0 AND o<4 AND q=1) OR ((d=0 OR o=4) AND q=1) | ? AND (A XXX B) OR (? OR (A XXX B)) |
|  ~q_m       |   10         | (d>0 AND o>4 AND q=0) OR ((d=0 OR o=4) AND q=0) | ? AND (A XXX B) OR (? OR (A XXX B)) |
|  ~q_m       |   11         | (d>0 AND o>4 AND q=1)                           | ? AND (A XXX B)                     |


----
----

The TMDS symbol encoding scheme is described in "3.2.2 Encode Algorithm" of the
DVI Revision 1.0 specification;

```
D == Eight bit pixel data
C0, C1 = Control data
DE == Data Enable

N1{x} == Number of "1" in x
N0{x} == Number of "0" in x

cnt ==
q_out = 10 bits encoded output value



if N1{D} > 4 or (N1{D} == 4 AND D[0] == 0)

 q_m[0] = D[0]
 q_m[1] = q_m[0] XNOR D[1]
 q_m[2] = q_m[0] XNOR D[2]
 ...
 q_m[7] = q_m[0] XNOR D[7]
 q_m[8] = 0

else

 q_m[0] = D[0]
 q_m[1] = q_m[0] XOR D[1]
 q_m[2] = q_m[0] XOR D[2]
 ...
 q_m[7] = q_m[0] XOR D[7]
 q_m[8] = 1

if DE != HIGH
 Cnt(t) == 0
 control tokens
else
 if (Cnt(t-1) == 0) OR (N1{q_m[0:7]} == N0{q_m[0:7]})
   q_out[9] = ~q_m[8]
   q_out[8] = q_m[8]
   q_out[0:7] = (q_m[8] ? q_m[0:7] : ~q_m[0:7])

   if q_m[8] == 0
      Cnt(t) = Cnt(t-1) + (N0{q_m[0:7]} - N1{q_m[0:7]})
   else
      Cnt(t) = Cnt(t-1) + (N1{q_m[0:7]} - N0{q_m[0:7]})
 else
   if ((Cnt(t-1) > 0) AND (N1{q_m[0:7]} > N0{q_m[0:7]})) OR (Cnt(t-1)<0 AND (N0{q_m[0:7]} > N1{q_m[0:7]}))
     q_out[9] = 1
     q_out[8] = q_m[8]
     q_out[0:7] = ~q_m[0:7]
     Cnt(t) = Cnt(t-1) + 2 * q_m[8] + (N0{q_m[0:7]} - N1{q_m[0:7]})
   else
     q_out[9] = 0
     q_out[8] = q_m[8]
     q_out[0:7] = q_m[0:7]
     Cnt(t) = Cnt(t-1) - 2 * ~q_m[8] + (N1{q_m[0:7]} - N0{q_m[0:7]})
```
