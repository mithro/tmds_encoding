
#include <assert.h>
#include <tmds.h>
#include <ccan/tap/tap.h>

void test_rotate_10bit(void) {
	diag("Testing rotate 0: 0x%x", ROTATE_10BIT(0x001, 0));
	ok1(0x001 == ROTATE_10BIT(0x001, 0));
	diag("Testing rotate 10: 0x%x", ROTATE_10BIT(0x001, 10));
	ok1(0x001 == ROTATE_10BIT(0x001, 10));

	diag("Testing rotate 1: 0x%x", ROTATE_10BIT(0x001, 1));
	ok1(0x002 == ROTATE_10BIT(0x001, 1));

	diag("Testing rotate 1: 0x%x", ROTATE_10BIT(0x200, 1));
	ok1(0x001 == ROTATE_10BIT(0x200, 1));

	diag("Testing rotate 1: 0x%x", ROTATE_10BIT(0x201, 1));
	ok1(0x003 == ROTATE_10BIT(0x201, 1));

	diag("Testing rotate 2: 0x%x", ROTATE_10BIT(0x001, 2));
	ok1(0x004 == ROTATE_10BIT(0x001, 2));
}

void test_rotate_20bit(void) {
	diag("Testing rotate 0: 0x%lx", ROTATE_20BIT(0x001, 0));
	ok1(0x001 == ROTATE_20BIT(0x001, 0));
	diag("Testing rotate 10: 0x%lx", ROTATE_20BIT(0x001, 10));
	ok1(0x001 == ROTATE_20BIT(0x001, 10));

	diag("Testing rotate 1: 0x%lx", ROTATE_20BIT(0x001, 1));
	ok1(0x002 == ROTATE_20BIT(0x001, 1));

	diag("Testing rotate 1: 0x%lx", ROTATE_20BIT(0x400, 1));
	ok1(0x400 == ROTATE_20BIT(0x200, 1));

	diag("Testing rotate 1: 0x%lx", ROTATE_20BIT(0x400000, 1));
	ok1(0x01 == ROTATE_20BIT(0x400000, 1));

	diag("Testing rotate 1: 0x%lx", ROTATE_20BIT(0x201, 1));
	ok1(0x003 == ROTATE_20BIT(0x201, 1));

	diag("Testing rotate 2: 0x%lx", ROTATE_20BIT(0x001, 2));
	ok1(0x004 == ROTATE_20BIT(0x001, 2));
}


void test_tmds_token_encoded_structure(void) {
	struct tmds_token_encoded tokenA = { 0 };
	tokenA.A = 1;
	diag("Testing A bit (bits_all: 0x%x, bits_dat: 0x%x)", tokenA.bits_all, tokenA.bits_dat);
	ok1(tokenA.bits_dat == 0x01);
	ok1(tokenA.bits_all == 0x01);

	struct tmds_token_encoded tokenH = { 0 };
	tokenH.H = 1;
	diag("Testing H bit (bits_all: 0x%x, bits_dat: 0x%x)", tokenH.bits_all, tokenH.bits_dat);
	ok1(tokenH.bits_dat == 0x80);
	ok1(tokenH.bits_all == 0x80);

	struct tmds_token_encoded tokenX = { 0 };
	tokenX.X = 1;
	diag("Testing X bit (bits_all: 0x%x, bits_dat: 0x%x)", tokenX.bits_all, tokenX.bits_dat);
	ok1(tokenX.bits_dat == 0x00);
	ok1(tokenX.bits_all == 0x100);

	struct tmds_token_encoded tokenI = { 0 };
	tokenI.I = 1;
	diag("Testing I bit (bits_all: 0x%x, bits_dat: 0x%x)", tokenI.bits_all, tokenI.bits_dat);
	ok1(tokenI.bits_dat == 0x00);
	ok1(tokenI.bits_all == 0x200);

}

void test_tmds_ctrl_defines(void) {
	ok1(tmds_ctrl_to_encoded[0B00].bits_all == TMDS_CTRL_00);
	ok1(tmds_ctrl_to_encoded[0B01].bits_all == TMDS_CTRL_01);
	ok1(tmds_ctrl_to_encoded[0B10].bits_all == TMDS_CTRL_10);
	ok1(tmds_ctrl_to_encoded[0B11].bits_all == TMDS_CTRL_11);
}

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

struct tmds_token tmds_get_token(uint_least16_t bits, uint8_t alignment) {
	assert(alignment >= 0);
	assert(alignment < 10);
	struct tmds_token_encoded input = {.bits_all = (bits >> alignment) & MASK_10BIT};
	struct tmds_token token = tmds_encoded_to_data[input.bits_all];
	return token;
}

void test_tmds_detect_alignment(void) {
	ok1(tmds_detect_alignment(0B11010101001101010100) == 0);
	ok1(tmds_detect_alignment(0B110101010011010101001) == 1);
	ok1(tmds_detect_alignment(0B110101010011010101000) == 1);
	ok1(tmds_detect_alignment(0B1101010100110101010011) == 2);
	ok1(tmds_detect_alignment(0B1101010100110101010001) == 2);
	ok1(tmds_detect_alignment(0B11010101001101110100) == -1);

	struct tmds_token token = tmds_get_token(TMDS_CTRL_00 << 1, 1);
	ok1(token.type == TMDS_CTRL_10b2b);
	ok1(token.data.c0 == 0);
	ok1(token.data.c1 == 0);
}

int main(int argc, char *argv[]) {
	plan_tests(8);

	test_rotate_10bit();
	test_rotate_20bit();
	test_tmds_token_encoded_structure();
	test_tmds_ctrl_defines();
	test_tmds_detect_alignment();

	return exit_status();
}
