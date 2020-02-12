from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify, request

from rigol import DP832, ArgumentError, InitError, Query

import time
import sys
import visa

app = Flask(__name__)

device = DP832()

def response(q):
    return jsonify(q.to_dict())

@app.route("/")
def index():
    return jsonify(user="lala")

@app.route("/idn")
def idn():
    return response(device.idn())

@app.route("/power")
def power():
    return response(device.power(request.args.get("channel")))

@app.route("/on")
def on():
    return response(device.on(request.args.get("channel")))

@app.route("/off")
def off():
    return response(device.off(request.args.get("channel")))

@app.route("/select")
def select():
    return response(device.select(request.args.get("channel")))

@app.route("/apply")
def apply():
    return response(device.apply(request.args.get("channel"), request.args.get("u"), request.args.get("i")))

if __name__ == "__main__":
    device.start()
    app.run(debug=False)
    device.close()
