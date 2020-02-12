import visa

class InitError(Exception):
    pass

class ArgumentError(Exception):
    pass

class Query():
    def __init__(self, q, fn):
        self.q = q
        self.fn = fn
        r = fn(q)
        if isinstance(r, str):
            r = r.strip()
        else:
            r = ""
        self.r = r

    def to_dict(self):
        return {"command": self.q, "response": self.r}

class DP832():
    def __init__(self):
        self.rm = visa.ResourceManager('@py')
        self.instr = None
        self.channels = ["CH1", "CH2", "CH3"]

    def start(self):
        res = self.rm.list_resources()
        if not res:
            raise InitError("No instruments found")
        print(res)
        self.instr = self.rm.open_resource(res[0])
        self.instr.clear()

    def _q(self, s):
        return Query(s, self.instr.query)

    def _w(self, s):
        return Query(s, self.instr.write)

    def _ch(self, ch):
        if not ch:
            return None
        if isinstance(ch, int):
            ch = "CH" + str(ch)
        if "CH" not in ch:
            ch = "CH" + str(ch)
        if ch not in self.channels:
            raise ArgumentError("Channel {} not in expected values: {}".format(ch, str(self.channels)))
        return ch

    def _real(self, f):
        if not isinstance(f, float):
            f = float(f)
        f = "{:2.4f}".format(f)
        return f

    def close(self):
        self.instr.close()

    def idn(self):
        response = self._q('*IDN?')
        return response

    def power(self, channel):
        channel = self._ch(channel)
        if not channel:
            raise ArgumentError("No valid channel")
        return self._q(":OUTP? " + channel)

    def on(self, channel):
        if not channel:
            raise ArgumentError("No valid channel")
        channel = self._ch(channel)

        command = ":OUTP {},ON".format(channel)
        return self._q(command)

    def off(self, channel):
        if not channel:
            raise ArgumentError("No valid channel")
        channel = self._ch(channel)

        command = ":OUTP {},OFF".format(channel)
        return self._q(command)

    def apply(self, channel, voltage=None, current=None):
        if not channel:
            raise ArgumentError("No valid channel")
        channel = self._ch(channel)
        if not voltage:
            command = ":APPL? " + channel
            return self._q(command)
        else:
            voltage = self._real(voltage)
            if not current:
                command = ":APPL {},{}".format(channel, voltage)
            else:
                current = self._real(current)
                command = ":APPL {},{},{}".format(channel, voltage, current)
            return self._w(command)

    def select(self, channel):
        channel = self._ch(channel)
        if not channel:
            command = ":INST?"
            response = self._q(command)
        else:
            command = "INST " + channel
            response = self._q(command)
        return response