import visa

class InitError(Exception):
    pass

class ArgumentError(Exception):
    pass

class ArgumentMissingError(ArgumentError):
    def __init__(self, arg):
        message = "Argument missing: " + arg
        super().__init__(message)

class CommandFormatter():
    def __init__(self, channels):
        self.channels = channels

    def format_channel_str(self, ch):
        if not ch:
            return None
        if isinstance(ch, int):
            ch = "CH" + str(ch)
        if isinstance(ch, str):
            ch = ch.upper()
        if "CH" not in ch:
            ch = "CH" + str(ch)
        if ch not in self.channels:
            raise ArgumentError("Channel {} not in expected values: {}".format(ch, str(self.channels)))
        return ch

    def format_bool_str(self, b):
        if isinstance(b, str):
            b = b.upper()
            if b in ["ON", "OFF"]:
                return b
        return b and "ON" or "OFF"

    def format_channel_int(self, ch):
        if not ch:
            return None
        if isinstance(ch, int):
            if ch <= 0 or ch > len(self.channels):
                raise ArgumentError("Invalid channel index: {}".format(ch))
            return ch
        ch = self.format_channel_str(ch)
        return self.channels.index(ch) + 1

    def format_real(self, f):
        if not isinstance(f, float):
            f = float(f)
        f = "{:2.4f}".format(f)
        return f

    def query_output_state(self, channel):
        if channel is None:
            command = ":OUTP?"
        else:
            channel = self.format_channel_str(channel)
            command = ":OUTP? " + channel
        return command

    def output_state(self, channel, mode):
        if mode is None:
            raise ArgumentError("Argument missing: mode")
        mode = self.format_bool_str(mode)
        if channel is None:
            command = ":OUTP " + mode
        else:
            channel = self.format_channel_str(channel)
            command = ":OUTP {},{}".format(channel, mode)
        return command

    def query_source_voltage(self, channel):
        if channel is None:
            command = ":VOLT?"
        else:
            channel = self.format_channel_int(channel)
            command = ":SOUR{}:VOLT?".format(channel)
        return command

    def source_voltage(self, channel, voltage):
        if voltage is None:
            raise ArgumentMissingError("voltage")
        if channel is None:
            command_format = ":VOLT {voltage}"
        else:
            command_format = ":SOUR{channel}:VOLT {voltage}"

        channel = self.format_channel_int(channel)
        voltage = self.format_real(voltage)
        return command_format.format(channel=channel, voltage=voltage)

    def query_source_current(self, channel):
        if channel is None:
            command = ":CURR?"
        else:
            channel = self.format_channel_int(channel)
            command = ":SOUR{}:CURR?".format(channel)
        return command

    def source_current(self, channel, current):
        if current is None:
            raise ArgumentMissingError("current")
        if channel is None:
            command_format = ":CURR {current}"
        else:
            command_format = ":SOUR{channel}:CURR {current}"

        channel = self.format_channel_int(channel)
        current = self.format_real(current)
        return command_format.format(channel=channel, current=current)

    def query_source_current_ocp(self, channel):
        if channel is None:
            command = ":CURR:PROT?"
        else:
            channel = self.format_channel_int(channel)
            command = ":SOUR{}:CURR:PROT?".format(channel)
        return command

    def source_current_ocp(self, channel, current):
        if current is None:
            raise ArgumentMissingError("current")
        if channel is None:
            command_format = ":CURR:PROT {current}"
        else:
            command_format = ":SOUR{channel}:CURR:PROT {current}"

        channel = self.format_channel_int(channel)
        current = self.format_real(current)
        return command_format.format(channel=channel, current=current)

    def query_measured_current(self, channel):
        if channel is None:
            command = ":MEAS:CURR?"
        else:
            channel = self.format_channel_str(channel)
            command = ":MEAS:CURR? " + channel
        return command

    def query_measured_voltage(self, channel):
        if channel is None:
            command = ":MEAS:VOLT?"
        else:
            channel = self.format_channel_str(channel)
            command = ":MEAS:VOLT? " + channel
        return command

    def query_measured_power(self, channel):
        if channel is None:
            command = ":MEAS:POWE?"
        else:
            channel = self.format_channel_str(channel)
            command = ":MEAS:POWE? " + channel
        return command


class DP832():
    class Resource():
        def __init__(self):
            self.instr = None

        def write(self, w):
            print(w)
            self.instr.write(w)

        def query(self, q):
            print(q)
            r = self.instr.query(q).strip()
            print(r)
            return r

    class Channel():
        def __init__(self, name, resource, command_formatter):
            self.name = name
            self.instr = resource
            self.command_formatter = command_formatter

        @property
        def voltage(self):
            cmd = self.command_formatter.query_source_voltage(self.name)
            r = self.instr.query(cmd)
            return r

        @voltage.setter
        def voltage(self, value):
            cmd = self.command_formatter.source_voltage(self.name, value)
            self.instr.write(cmd)

        @property
        def current(self):
            cmd = self.command_formatter.query_source_current(self.name)
            r = self.instr.query(cmd)
            return r

        @current.setter
        def current(self, value):
            cmd = self.command_formatter.source_current(self.name, value)
            self.instr.write(cmd)

        @property
        def current_limit(self):
            cmd = self.command_formatter.query_source_current_ocp(self.name)
            r = self.instr.query(cmd)
            return r

        @current_limit.setter
        def current_limit(self, value):
            cmd = self.command_formatter.source_current_ocp(self.name, value)
            self.instr.write(cmd)

        @property
        def state(self):
            cmd = self.command_formatter.query_output_state(self.name)
            r = self.instr.query(cmd)
            return r

        @state.setter
        def state(self, mode):
            cmd = self.command_formatter.output_state(self.name, mode)
            self.instr.write(cmd)

        @property
        def u(self):
            cmd = self.command_formatter.query_measured_voltage(self.name)
            return self.instr.query(cmd)

        @property
        def i(self):
            cmd = self.command_formatter.query_measured_current(self.name)
            return self.instr.query(cmd)

        @property
        def p(self):
            cmd = self.command_formatter.query_measured_power(self.name)
            return self.instr.query(cmd)

    def __init__(self):
        self.rm = visa.ResourceManager('@py')
        self.instr = None
        self.resource = DP832.Resource()
        self._channel_names = ["CH1", "CH2", "CH3"]
        self.formatter = CommandFormatter(self._channel_names)
        self._channels = {name : DP832.Channel(name, self.resource, self.formatter) for name in self._channel_names}

    def __getitem__(self, item):
        try:
            item = self.formatter.format_channel_str(item)
            return self._channels[item]
        except:
            return None


    def start(self):
        res = self.rm.list_resources()
        if not res:
            raise InitError("No instruments found")
        print(res)
        self.instr = self.rm.open_resource(res[0], read_termination='\n')
        self.resource.instr = self.instr
        self.instr.clear()

    def idn(self):
        return self.resource.query('*IDN?')