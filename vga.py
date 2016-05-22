# vim:set ts=4 sw=4 sts=4 expandtab:

from collections import namedtuple

_PulseBase = namedtuple("Pulse", ["start", "end", "polarity"])

class Pulse(_PulseBase):
    """
    >>> p = Pulse(20, 30)
    >>> p
    Pulse(start=20, end=30, polarity=1)
    >>> p.length
    10
    >>> Pulse(30, 20)
    Traceback (most recent call last):
        ...
    AssertionError
    """

    POSITIVE = 1
    NEGATIVE = 0

    def __new__(cls, start, end, polarity=POSITIVE):
        assert end > start
        return _PulseBase.__new__(cls, start, end, polarity)

    @property
    def length(self):
        return self.end - self.start


_ScanSignalBase = namedtuple("ScanSignal", ["active", "total", "pulse"])

class ScanSignal(_ScanSignalBase):

    def __new__(cls, active, total, pulse):
        (pulse_start, pulse_end, pulse_polarity) = pulse
        if pulse_polarity is None:
            pulse_polarity = Pulse.POSITIVE

        assert active < total

        # Check that the sync pulse is between the active and end
        assert pulse_start > active
        assert pulse_end < total

        obj = _ScanSignalBase.__new__(cls, active, total, Pulse(pulse_start, pulse_end, pulse_polarity))
        return obj

    @property
    def blanking(self):
        return self.total - self.active

    @property
    def sync(self):
        return self.pulse.length


_VGATimingBase = namedtuple("VGATiming", ["dotclock", "horizontal", "vertical", "description"])

class VGATiming(_VGATimingBase):
    """
    >>> t1 = VGATiming(
    ...     31500000,
    ...     ScanSignal(640, 840, (656, 720, Pulse.POSITIVE)),
    ...     ScanSignal(480, 500, (481, 484, Pulse.POSITIVE)),
    ...     description="640x480")
    >>> t1
    VGATiming(dotclock=31500000, horizontal=ScanSignal(active=640, total=840, pulse=Pulse(start=656, end=720, polarity=1)), vertical=ScanSignal(active=480, total=500, pulse=Pulse(start=481, end=484, polarity=1)), description='640x480')
    >>> t1.modeline()
    'Modeline "640x480" 31.50 640 656 720 840 480 481 484 500 +HSync +VSync'
    >>> t2 = VGATiming.from_modeline(t1.modeline())
    >>> t2
    VGATiming(dotclock=31500000, horizontal=ScanSignal(active=640, total=840, pulse=Pulse(start=656, end=720, polarity=1)), vertical=ScanSignal(active=480, total=500, pulse=Pulse(start=481, end=484, polarity=1)), description='640x480')
    >>> assert t1 == t2
    >>> t3 = VGATiming(
    ...     31500000,
    ...     ScanSignal(640, 840, (656, 720, Pulse.POSITIVE)),
    ...     ScanSignal(480, 500, (481, 484, Pulse.POSITIVE)),
    ...     )
    >>> t3.description
    '640x480@31.5MHz'
    """

    def __new__(cls, dotclock, horizontal, vertical, description=None):
        assert isinstance(horizontal, ScanSignal)
        assert isinstance(vertical, ScanSignal)

        if not description:
            description = "{hactive}x{vactive}@{dotclock:.1f}MHz".format(
            hactive=horizontal.active, vactive=vertical.active,
            dotclock=dotclock/1e6,
            )

        obj = _VGATimingBase.__new__(cls, dotclock, horizontal, vertical, description)
        obj._description = description
        return obj

    @property
    def h(self):
        return self.horizontal

    @property
    def v(self):
        return self.vertical


    @property
    def options(self):
        options = []
        if self.h.pulse.polarity == 1:
            options.append("+HSync")
        else:
            options.append("-HSync")

        if self.v.pulse.polarity == 1:
            options.append("+VSync")
        else:
            options.append("-VSync")
        
        return " ".join(options)

    def modeline(self):
        # 640x480 @ 75Hz (VESA) hsync: 37.5kHz
	    # Modeline "String des" Dot-Clock HDisp HSyncStart HSyncEnd HTotal VDisp VSyncStart VSyncEnd VTotal [options]
        # ModeLine "640x480"    31.5  640  656  720  840    480  481  484  500
        #                                16   64  <200         1    3   <20
	    return """\
Modeline "{description}" {dotclock:.2f} {hdisp} {hsyncstart} {hsyncend} {htotal} {vdisp} {vsyncstart} {vsyncend} {vtotal} {options}""".format(
            description=self.description,
            dotclock=self.dotclock/1e6,
            hdisp=self.h.active,
            hsyncstart=self.h.pulse.start,
            hsyncend=self.h.pulse.end,
            htotal=self.h.total,
            vdisp=self.v.active,
            vsyncstart=self.v.pulse.start,
            vsyncend=self.v.pulse.end,
            vtotal=self.v.total,
            options=self.options,
            )

    @classmethod
    def from_modeline(self, line):
        line = line.strip().lower()
        assert line.startswith("modeline "), line

        bits = line.split()
        assert bits.pop(0) == "modeline"

        description = bits.pop(0) # FIXME: This assume no spaces in description...
        if description.startswith('"'):
            assert description.endswith('"'), description
            description = description[1:-1]
 
        dotclock = int(float(bits.pop(0)) * 1e6)

        h_active = int(bits.pop(0))
        h_pulse_start = int(bits.pop(0))
        h_pulse_end = int(bits.pop(0))
        h_pulse_polarity = None
        h_total = int(bits.pop(0))

        v_active = int(bits.pop(0))
        v_pulse_start = int(bits.pop(0))
        v_pulse_end = int(bits.pop(0))
        v_pulse_polarity = None
        v_total = int(bits.pop(0))

        options = bits
        if "+hsync" in options:
            h_pulse_polarity=Pulse.POSITIVE
        if "-hsync" in options:
            h_pulse_polarity=Pulse.NEGATIVE

        if "+vsync" in options:
            v_pulse_polarity=Pulse.POSITIVE
        if "-HSync" in options:
            v_pulse_polarity=Pulse.NEGATIVE

        return VGATiming(
            dotclock,
            ScanSignal(
                h_active, h_total, 
                (h_pulse_start, h_pulse_end, h_pulse_polarity),
                ),
            ScanSignal(
                v_active, v_total,
                (v_pulse_start, v_pulse_end, v_pulse_polarity),
                ),
            description=description,
            )


if __name__ == "__main__":
    import doctest
    doctest.testmod()
