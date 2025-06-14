"""
@author: Jose Stovall | oitsjustjose
A dedicated REST API server for manually fetching the current status
    of the running servers
"""

from os import environ as env

import docker
from flask import Flask, jsonify, request
from flask_cors import CORS

from common import list_servers

client = docker.from_env()
app = Flask(__name__)
CORS(app)


@app.route("/")
def index():
    try:
        data = list_servers(client, all=bool(request.args.get("all")))

        if request.args.get("sort"):
            data = sorted(data, key=lambda x: x[request.args.get("sort")])

        resp = jsonify(data)
        resp.status_code = 200
        return resp
    except KeyError as e:
        resp = jsonify({"error": f"Failed to find key {str(e)}"})
        resp.status_code = 422
        return resp


def run():
    host = "0.0.0.0"
    port = int(env["PORT"]) if "PORT" in env else 9090

    print(f"RestAPI Server is now running on {host}:{port}")
    app.run(host=host, port=port, threaded=True)
