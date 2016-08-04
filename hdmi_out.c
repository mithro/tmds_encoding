
#include <stdbool.h>
#include <stdint.h>

#define TWO_TOKENS(a, b) \
	(((uint_least32_t)a) << 10 & b)

#define 10BIT_ROTATE(a, n) \
	((((uint_least32_t)a) << n) & 0x3ff) //| ((((uint_least32_t)a) << n) >> 10)

#define CASE_ALIGN(n) \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl00, ctrl00), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl00, ctrl01), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl00, ctrl10), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl00, ctrl11), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl01, ctrl00), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl01, ctrl01), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl01, ctrl10), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl01, ctrl11), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl10, ctrl00), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl10, ctrl01), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl10, ctrl10), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl10, ctrl11), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl11, ctrl00), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl11, ctrl01), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl11, ctrl10), n): \
	case 10BIT_ROTATE(TWO_TOKENS(ctrl11, ctrl11), n): \
		return n;

int8_t detect_alignment(uint_least32_t bits) {
	// Mask out the bottom 20 bits
	bits &= 0x000fffff;
	switch(bits) {
	CASE_ALIGN(0)
	CASE_ALIGN(1)
	CASE_ALIGN(2)
	CASE_ALIGN(3)
	CASE_ALIGN(4)
	CASE_ALIGN(5)
	CASE_ALIGN(6)
	CASE_ALIGN(7)
	CASE_ALIGN(8)
	CASE_ALIGN(9)
	default:
		return -1;
	}
	assert(false);
}

struct token {
	enum {
		ERROR = -1,
		CONTROL = 0,
		DATA = 1,
	} type;
	union {
		struct {
			bool c0;
			bool c1;
		};
		uint8_t data;
	};
	uint16_t raw_data;
};

extern struct token lookup_table[0x3ff];


void print_token(struct token t) {
	switch(t.type) {
	case ERROR:
		printf("ERROR(%x)", t.raw_data);
		break;
	case CONTROL:
		printf("CTRL(%d, %d)", t.c0, t.c1);
		break;
	case DATA:
		printf("DATA(%d)", t.data);
		break;
	}
	assert(false);
}

bool decode_token(uint_least32_t bits, int8_t *alignment, struct token *out) {
	if (*alignment == -1) {
		*alignment = detect_alignment(bits);
	}
	if (*alignment == -1) {
		return false;
	}

	uint16_t raw_data = (bits >> alignment) & 0x3ff;
	out = lookup_table[raw_data];
	return true;
}

