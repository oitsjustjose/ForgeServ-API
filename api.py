"""
Author: Jose Stovall
Description: A Flask API service for the running Minecraft server statuses
"""

from flask import jsonify, request, Flask
from flask_cors import CORS
from common import get_server_info

app = Flask(__name__)
CORS(app)

@app.route("/")
def index():
    try:
        data = get_server_info(all=request.args.get('all'))

        if request.args.get('sortedOnKey'):
            data = sorted(data, key=lambda x: x[request.args.get('sortedOnKey')])

        resp = jsonify(data)
        resp.status_code = 200
        return resp
    except KeyError as e:
        resp = jsonify({ "error": f"Failed to find key {str(e)}" })
        resp.status_code = 422
        return resp

if __name__ == "__main__":
    app.run(host='0.0.0.0')
