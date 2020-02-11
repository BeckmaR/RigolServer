from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify, request

import time
import sys
import visa

app = Flask(__name__)

class DP832():
    def __init__(self):
        self.rm = visa.ResourceManager('@py')
        self.instr = None
        self.channels = ["CH1", "CH2", "CH3"]

    def start(self):
        res = self.rm.list_resources()
        if not res:
            print("No instruments found")
            sys.exit(-1)
        print(res)
        self.instr = self.rm.open_resource(res[0])
        self.instr.clear()
        print("done")

        print(self.instr.query('*IDN?'))

    def _q(self, s):
        return self.instr.query(s).strip()

    def _w(self, s):
        self.instr.write(s)

    def _ch(self, ch):
        if not ch:
            return None
        if isinstance(ch, int):
            ch = "CH" + str(ch)
        if "CH" not in ch:
            ch = "CH" + str(ch)
        if ch not in self.channels:
            return None
        return ch

    def close(self):
        self.instr.close()

    def idn(self):
        response = self._q('*IDN?')
        return jsonify(response=response)

    def power(self, channel=None):
        channel = self._ch(channel)
        if not channel:
            response = {ch:self._q(":OUTP? " + ch) for ch in self.channels}
        else:
            response = self._q(":OUTP? " + channel)
        return jsonify(response=response)

    def on(self, channel):
        channel = self._ch(channel)
        if not channel:
            return jsonify(error="No valid channel")

        command = ":OUTP {},ON".format(channel)
        self._w(command)
        return jsonify(response="OK", command=command)

    def off(self, channel):
        channel = self._ch(channel)
        if not channel:
            return jsonify(error="No valid channel")

        command = ":OUTP {},OFF".format(channel)
        self._w(command)
        return jsonify(response="OK", command=command)

    def select(self, channel):
        channel = self._ch(channel)
        if not channel:
            command = ":INST?"
            response = self._q(command)
        else:
            command = "INST " + channel
            self._w(command)
            response = "OK"
        return jsonify(response=response, command=command)


device = DP832()

@app.route("/")
def index():
    return jsonify(user="lala")

@app.route("/idn")
def idn():
    return device.idn()

@app.route("/power")
def power():
    return device.power(request.args.get("channel"))

@app.route("/on")
def on():
    return device.on(request.args.get("channel"))

@app.route("/off")
def off():
    return device.off(request.args.get("channel"))

@app.route("/select")
def select():
    return device.select(request.args.get("channel"))

if __name__ == "__main__":
    device.start()
    app.run(debug=False)
    device.close()
