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

json_header = {'Content-Type': 'application/json'}

def response(q):
    return jsonify(q.to_dict())

@app.route("/")
def index():
    return jsonify(device.idn()), 200, json_header

@app.route("/<channel_name>")
def state(channel_name):
    channel = device[channel_name]
    if not channel:
        return jsonify(error="No such channel: " + channel_name), 404, json_header
    return jsonify(response=channel.state), 200, json_header

@app.route("/<channel_name>/on")
def on(channel_name):
    channel = device[channel_name]
    if not channel:
        return jsonify(error="No such channel: " + channel_name), 404, json_header
    channel.state = "ON"
    return jsonify(response=channel.state), 200, json_header

@app.route("/<channel_name>/off")
def off(channel_name):
    channel = device[channel_name]
    if not channel:
        return jsonify(error="No such channel: " + channel_name), 404, json_header
    channel.state = "OFF"
    return jsonify(response=channel.state), 200, json_header

@app.route("/<channel_name>/voltage")
def voltage(channel_name):
    channel = device[channel_name]
    if not channel:
        return jsonify(error="No such channel: " + channel_name), 404, json_header
    value = request.args.get("set")
    if value:
        channel.voltage = value
    return jsonify(response=channel.voltage), 200, json_header

@app.route("/<channel_name>/current_limit")
def current_limit(channel_name):
    channel = device[channel_name]
    if not channel:
        return jsonify(error="No such channel: " + channel_name), 404, json_header
    value = request.args.get("set")
    if value:
        channel.current_limit = value
    return jsonify(response=channel.current_limit), 200, json_header


@app.route("/<channel_name>/current")
def current(channel_name):
    channel = device[channel_name]
    if not channel:
        return jsonify(error="No such channel: " + channel_name), 404, json_header
    value = request.args.get("set")
    if value:
        channel.current = value
    return jsonify(response=channel.current), 200, json_header

@app.route("/<channel_name>/u")
def u(channel_name):
    channel = device[channel_name]
    if not channel:
        return jsonify(error="No such channel: " + channel_name), 404, json_header
    return jsonify(response=channel.u), 200, json_header

@app.route("/<channel_name>/i")
def i(channel_name):
    channel = device[channel_name]
    if not channel:
        return jsonify(error="No such channel: " + channel_name), 404, json_header
    return jsonify(response=channel.i), 200, json_header

@app.route("/<channel_name>/p")
def p(channel_name):
    channel = device[channel_name]
    if not channel:
        return jsonify(error="No such channel: " + channel_name), 404, json_header
    return jsonify(response=channel.p), 200, json_header


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
