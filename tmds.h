
#include <stdbool.h>
#include <stdint.h>

#include <ccan/build_assert/build_assert.h>

#define MASK_10BIT ((uint_least16_t)0x3ff)
#define MASK_20BIT ((uint_least32_t)0xfffff)

#define ROTATE_10BIT(a, n) \
	(((((uint_least32_t)a) << n) & MASK_10BIT) | ((((uint_least32_t)a) << n) >> 10))

#define ROTATE_20BIT(a, n) \
	(((((uint_least64_t)a) << n) & MASK_20BIT) | ((((uint_least64_t)a) << n) >> 20))


enum tmds_token_type {
	TMDS_ERROR = 0,

	// Pixel data in 10b8b TMDS encoding
	TMDS_PIXEL_10b8b = 1,

	// Control data in 10b2b TMDS encoding
	TMDS_CTRL_10b2b = 2,

	// Auxiliary HDMI data in 10b4b TERC4 encoding
	TMDS_AUX_10b4b = 3,
};

union tmds_token_data {
	// Pixel data
	uint8_t pixel;
	// Control data
	struct {
		uint8_t c0 : 1;
		uint8_t c1 : 1;
                uint8_t    : 6;  // Fill
	};
	// Aux data
	struct {
		uint8_t aux: 4;
                uint8_t    : 4;  // Fill
	};
};


// Ordering of the bits matters in the encoded 
struct tmds_token_encoded {
	union {
		struct {
			union {
				struct {
					uint8_t A : 1; // LSB
					uint8_t B : 1;
					uint8_t C : 1;
					uint8_t D : 1;
					uint8_t E : 1;
					uint8_t F : 1;
					uint8_t G : 1;
					uint8_t H : 1;
				};
				uint8_t bits_dat;
			};
			uint8_t X : 1;	// XOR or XNOR encoding
			uint8_t I : 1;  // Inverted (MSB)
                        uint8_t   : 6;  // Fill
		};
		uint16_t bits_all;
	};
};


struct tmds_token {
	enum tmds_token_type type;
	union tmds_token_data data;
};


// Table which maps from 10bit encoded values to TMDS tokens
extern struct tmds_token tmds_encoded_to_data[MASK_10BIT];


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

//                10   IX76543210
#define TMDS_CTRL_00 ((uint_least16_t)0B1101010100)
#define TMDS_CTRL_01 ((uint_least16_t)0B0010101011)
#define TMDS_CTRL_10 ((uint_least16_t)0B0101010100)
#define TMDS_CTRL_11 ((uint_least16_t)0B1010101011)

/*
 Pixel Tokens
 */
struct tmds_token_encoded_choice {
	struct tmds_token_encoded direct;
	struct tmds_token_encoded inverse;
};

extern struct tmds_token_encoded_choice tmds_pixel_to_encoded[0xff];

