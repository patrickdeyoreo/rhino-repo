#!/usr/bin/python3
"""
Provides RESTful API routes for Holberton
"""
from os import getcwd, chdir
from shutil import rmtree
from tempfile import mkdtemp
from flask import abort, jsonify, make_response, request
from . import app_views
from rhinoscraper.rhinoscrape import create_session, get_soup
from rhinoscraper.rhinoproject import rhinoproject
from rhinoscraper.rhinoread import rhinoread

AUTH = {'holberton_user', 'holberton_pass', 'holberton_api_key', 'github_pass'}


@app_views.route("/holberton/<project_id>", methods=['POST'])
def holberton_task(project_id):
    """Log into holberton and retrieve a project given their ID"""
    data = request.get_json()
    for key in AUTH:
        if key not in data:
            abort(400)
    sess = create_session(data['holberton_user'], data['holberton_pass'])
    soup = get_soup(sess, project_id)
    olddir = getcwd()
    tmpdir = mkdtemp()
    chdir(tmpdir)
    rhinoproject(soup)
    rhinoread(soup, sys.argv[4], sys.argv[5])
    # Push to github
    chdir(olddir)
    rmtree(path, ignore_errors=True)
    return {}, 200
