#all: libccan.a

include Makefile-ccan
tools/configurator/configurator: tools/configurator/configurator.c

config.h: tools/configurator/configurator Makefile Makefile-ccan
	tools/configurator/configurator $(CC) $(CCAN_CFLAGS) > $@ \
		|| rm -f $@

objs = $(patsubst %.c, %.o, $(wildcard ccan/*/*.c))
$(objs): config.h


CFLAGS+=-std=c11

all:    $(MAIN)

tmds_tests: tmds_tests.o tmds.o tmds_pixel_to_encoded.o tmds_encoded_to_token.o libccan.a
	$(CC) $(CFLAGS) $(INCLUDES) -o tmds_tests $^

tmds_pixel_to_encoded.c: tmds_c.py tmds_tokens.py
	python3 tmds_c.py $@ > $@

tmds_encoded_to_token.c: tmds_c.py tmds_tokens.py
	python3 tmds_c.py $@ > $@

%.o: %.c tmds.h
	$(CC) $(CFLAGS) $(INCLUDES) -c $<  -o $@

clean:
	$(RM) *.o *~ $(MAIN)
