// vim:set ts=4 sw=4 sts=4 expandtab:

struct vga_timing {
    int pixel_clock;

    int h_display;
    int h_sync_start;
    int h_sync_end;
    int h_total;

    int v_display;
    int v_sync_start;
    int v_sync_end;
    int v_total;

    bool h_sync_positive;
    bool v_sync_positive;
};

struct frame_data_head {
    int bits;
    size_t length;
};

struct frame_data {
    struct frame_data_head;
 
    int clock[];    // Clock channel
    int blue[];     // Channel 0
    int green[];    // Channel 1
    int red[];      // Channel 2
};

#define CLOCK_10BIT 0B1111100000


data* get_bits(struct vga_timing timing, struct pixel image[][]) {
    // Check the timing info
    assert(timing.h_display < timing.h_sync_start);
    assert(timing.h_sync_start < timing.h_sync_end);
    assert(timing.h_sync_end < timing.h_total);
    assert(timing.v_display < timing.v_sync_start);
    assert(timing.v_sync_start < timing.v_sync_end);
    assert(timing.v_sync_end < timing.v_total);

    //assert(h_display == image.width);
    //assert(v_display == image.height);

    unsigned length_in_bits = timing.h_total * timing.v_total * 10; /* bits per pixel */;
    size_t length_in_ints = (bitlength / (sizeof(int) * 8)) + 1;

    size_t data_size = sizeof(struct frame_data_head) + (4 * sizeof(int)) * length_in_ints;
    void data* = malloc(data_size);
    data->bits = length_in_bits;
    data->size = data_size;

    for (int v = 0; v < timing.v_total; v++) {
        for (int h = 0; h < timing.h_total; h++) {
            push_token(data->clock, CLOCK_10BIT);

            // Send pixel data
            if (v < timing.v_display && h < timing.h_display) {
                struct pixel p = image[h][v];

                struct tmds_token_encoded_choice blue_possible_tokens = tmds_pixel_to_encoded[p.blue];
                if (blue_bias > 0) {
                    push_token(data->blue, possible_token.negative.bits_all);
                    blue_bias += possible_token.negative.bias;
                } else if (blue_bias <= 0) {
                    push_token(data->blue, possible_token.positive.bits_all);
                    blue_bias += possible_token.positive.bias;
                }
            } else {
                // Work out the hsync/vsync signals
                /*
                 -------------------> Time ------------->
                
                                  +-------------------+
                   Video          |  Blanking         |  Video
                                     |                   |
                 ----(a)--------->|<-------(b)------->|
                                  |                   |
                                  |       +-------+   |
                                  |       | Sync  |   |
                                  |       |       |   |
                                  |<-(c)->|<-(d)->|   |
                                  |       |       |   |
                 ----(1)--------->|       |       |   |
                 ----(2)----------------->|       |   |
                 ----(3)------------------------->|   |
                 ----(4)----------------------------->|
                                  |       |       |   |
                                  
                 -----------------\                   /--------
                                  |                   |
                                  \-------\       /---/
                                          |       |
                                          \-------/
                 (a) - h_active
                 (b) - h_blanking
                 (c) - h_sync_offset
                 (d) - h_sync_width
                 (1) - HDisp / width
                 (2) - HSyncStart
                 (3) - HSyncEnd
                 (4) - HTotal
                */
                int hsync = -1;
                if (h < timing.h_sync_start) {
                    hsync = timing.h_sync_polarity;
                } else if (h < timing.h_sync_end) {
                    hsync = !timing.h_sync_polarity;
                } else if (h < timing.h_total-1) {
                    hsync = timing.h_sync_polarity;
                } else if (h == timing.h_total-1) {
                    hsync = !timing.h_sync_polarity;
                } else {
                    assert(false);
                }
                assert(hsync == 0 || hsync == 1);

                int vsync = -1;
                assert(vsync == 0 || vsync == 1);

                // Send the hsync/vsync via the control tokens on the blue channel
                // C0 == HSYNC signal
                // C1 == VSYNC signal
                struct tmds_token_data blue_ctrl_data = { .c0=hsync, .c1=vsync };
                push_token(data->blue, tmds_ctrl_to_encoded[blue_ctrl_data]);

                // The green and red channel just get c0==0, c1==0 all the time
                push_token(data->green, TMDS_CTRL_00);
                push_token(data->red, TMDS_CTRL_00);

                // Clear the DC bias...
                blue_bias = 0;
                green_bias = 0;
                red_bias = 0;
            }
        }
    }
    
    return data;
}
