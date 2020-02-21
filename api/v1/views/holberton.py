#!/usr/bin/python3
"""
Provides RESTful API routes for Holberton
"""

from flask.json import jsonify
from flask import abort
from flask import make_response
from flask import request
from . import app_views


@app_views.route("/holberton", methods=['POST'])
def create_session():
    """Log into """


@app_views.route("/holberton/<project>", methods=['GET'])
def scrape_project():
    """Retrieves a project given it's ID"""
    try:
        pass
    except AttributeError:
        abort(404)
