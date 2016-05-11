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

tmds_tests: tmds_tests.o libccan.a
	$(CC) $(CFLAGS) $(INCLUDES) -o tmds_tests tmds_tests.o libccan.a

tmds_tests.o: tmds_tests.c tmds.h
	$(CC) $(CFLAGS) $(INCLUDES) -c $<  -o $@

clean:
	$(RM) *.o *~ $(MAIN)
