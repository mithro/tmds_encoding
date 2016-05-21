
#include <assert.h>
#include <tmds.h>

/*
Control Tokens

 | data    || q_m       |      | q_m           (>0=+)||         encoded         |
 | C0 | C1 || 01234567XI|  OP  | 1s | 0s | ts | bias ||       01234567XI        |
 |----|----||-----------|------|----|----|----|------||-------------------------|
 |  0 | 0  || 0010101011|      |  5 | 5  |  7 |    0 ||       0010101011        |
 |  1 | 0  || 1101010100|      |  5 | 5  |  7 |    0 ||       1101010100        |
 |  0 | 1  || 0010101010|      |  4 | 6  |  8 |    2 ||       0010101010        |
 |  1 | 1  || 1101010101|      |  6 | 4  |  8 |   -2 ||       1101010101        |
*/

struct tmds_token_encoded tmds_ctrl_to_encoded[0x4] = {
	{ .A=0, .B=0, .C=1, .D=0, .E=1, .F=0, .G=1, .H=0, .X=1, .I=1}, // c1=0 c0=0
	{ .A=1, .B=1, .C=0, .D=1, .E=0, .F=1, .G=0, .H=1, .X=0, .I=0}, // c1=0 c0=1
	{ .A=0, .B=0, .C=1, .D=0, .E=1, .F=0, .G=1, .H=0, .X=1, .I=0}, // c1=1 c0=0
	{ .A=1, .B=1, .C=0, .D=1, .E=0, .F=1, .G=0, .H=1, .X=0, .I=1}, // c1=1 c0=1
};

#define TWO_TOKENS(a, b) \
	((((uint_least32_t)a) << 10) | b)

#define CASE_CONTROL_TOKENS() \
	TWO_TOKENS(TMDS_CTRL_00, TMDS_CTRL_00): \
	case TWO_TOKENS(TMDS_CTRL_00, TMDS_CTRL_01): \
	case TWO_TOKENS(TMDS_CTRL_00, TMDS_CTRL_10): \
	case TWO_TOKENS(TMDS_CTRL_00, TMDS_CTRL_11): \
	case TWO_TOKENS(TMDS_CTRL_01, TMDS_CTRL_00): \
	case TWO_TOKENS(TMDS_CTRL_01, TMDS_CTRL_01): \
	case TWO_TOKENS(TMDS_CTRL_01, TMDS_CTRL_10): \
	case TWO_TOKENS(TMDS_CTRL_01, TMDS_CTRL_11): \
	case TWO_TOKENS(TMDS_CTRL_10, TMDS_CTRL_00): \
	case TWO_TOKENS(TMDS_CTRL_10, TMDS_CTRL_01): \
	case TWO_TOKENS(TMDS_CTRL_10, TMDS_CTRL_10): \
	case TWO_TOKENS(TMDS_CTRL_10, TMDS_CTRL_11): \
	case TWO_TOKENS(TMDS_CTRL_11, TMDS_CTRL_00): \
	case TWO_TOKENS(TMDS_CTRL_11, TMDS_CTRL_01): \
	case TWO_TOKENS(TMDS_CTRL_11, TMDS_CTRL_10): \
	case TWO_TOKENS(TMDS_CTRL_11, TMDS_CTRL_11) \

#define FIND_ALIGNMENT(n) \
	switch((bits >> n) & MASK_20BIT) { \
	case CASE_CONTROL_TOKENS(): \
		return n; \
	}


int8_t tmds_detect_alignment(uint_least32_t bits);
int8_t tmds_detect_alignment(uint_least32_t bits) {
	FIND_ALIGNMENT(0);
	FIND_ALIGNMENT(1);
	FIND_ALIGNMENT(2);
	FIND_ALIGNMENT(3);
	FIND_ALIGNMENT(4);
	FIND_ALIGNMENT(5);
	FIND_ALIGNMENT(6);
	FIND_ALIGNMENT(7);
	FIND_ALIGNMENT(8);
	FIND_ALIGNMENT(9);
	return -1;
}

struct tmds_token tmds_get_token(uint_least16_t bits, uint8_t alignment);
struct tmds_token tmds_get_token(uint_least16_t bits, uint8_t alignment) {
	assert(alignment >= 0);
	assert(alignment < 10);
	struct tmds_token_encoded input = {.bits_all = (bits >> alignment) & MASK_10BIT};
	struct tmds_token token = tmds_encoded_to_token[input.bits_all];
	return token;
}

