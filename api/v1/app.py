#!/usr/bin/python3
"""
Returns the status of the API
"""

from models import storage
from api.v1.views import app_views
from flask import Flask, jsonify, make_response
from flask_cors import CORS
from os import getenv

HOST = getenv('RHINO_API_HOST', '0.0.0.0')
PORT = getenv('RHINE_API_PORT', '5000')
cors = CORS(app_views, resources={r"/*": {"origins": HOST}})

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
app.register_blueprint(app_views)


@app.errorhandler(404)
def error_404(err):
    """Produce a 404 error message"""
    return make_response(jsonify(error="oops, I did it again..."), 404)


@app.teardown_appcontext
def close_storage(exe):
    """closes storage"""
    storage.close()


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, threaded=True)
