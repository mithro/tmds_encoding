// vim:set ts=4 sw=4 sts=4 expandtab:

#include <assert.h>
#include <tmds.h>
#include <ccan/tap/tap.h>

void test_rotate_10bit(void);
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

void test_tmds_token_encoded_structure(void);
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

void test_tmds_ctrl_defines(void);
void test_tmds_ctrl_defines(void) {
    ok1(tmds_ctrl_to_encoded[0B00].bits_all == TMDS_CTRL_00);
    ok1(tmds_ctrl_to_encoded[0B01].bits_all == TMDS_CTRL_01);
    ok1(tmds_ctrl_to_encoded[0B10].bits_all == TMDS_CTRL_10);
    ok1(tmds_ctrl_to_encoded[0B11].bits_all == TMDS_CTRL_11);
}


void test_tmds_detect_alignment(void);
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

void test_tmds_get_token(void);
void test_tmds_get_token(void) {
    
    diag("Testing tmds_get_token(control, 00)");
    struct tmds_token token_c00 = tmds_get_token(TMDS_CTRL_00, 0);
    ok1(token_c00.type == TMDS_CTRL_10b2b);
    ok1(token_c00.data.c0 == 0);
    ok1(token_c00.data.c1 == 0);

    diag("Testing tmds_get_token(control, 01)");
    struct tmds_token token_c01 = tmds_get_token(TMDS_CTRL_01, 0);
    ok1(token_c01.type == TMDS_CTRL_10b2b);
    ok1(token_c01.data.c0 == 1);
    ok1(token_c01.data.c1 == 0);

    diag("Testing tmds_get_token(control, 10)");
    struct tmds_token token_c10 = tmds_get_token(TMDS_CTRL_10, 0);
    ok1(token_c10.type == TMDS_CTRL_10b2b);
    ok1(token_c10.data.c0 == 0);
    ok1(token_c10.data.c1 == 1);

    diag("Testing tmds_get_token(control, 11)");
    struct tmds_token token_c11 = tmds_get_token(TMDS_CTRL_11, 0);
    ok1(token_c11.type == TMDS_CTRL_10b2b);
    ok1(token_c11.data.c0 == 1);
    ok1(token_c11.data.c1 == 1);

    diag("Testing tmds_get_token(pixel 10h)");
    struct tmds_token_encoded pixel_10h = {
        .A=0, .B=0, .C=0, .D=0, .E=1, .F=1, .G=1, .H=1, .X=1, .I=0
    };
    struct tmds_token token_pixel_10h = tmds_get_token(pixel_10h.bits_all, 0);
    ok1(token_pixel_10h.type == TMDS_PIXEL_10b8b);
    ok1(token_pixel_10h.data.pixel = 0x10);
}

int main(int argc, char *argv[]) {
    plan_tests(8);

    test_rotate_10bit();
    test_tmds_token_encoded_structure();
    test_tmds_ctrl_defines();
    test_tmds_detect_alignment();

    test_tmds_get_token();
    return exit_status();
}
