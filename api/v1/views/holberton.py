#!/usr/bin/env python3
"""
Provides RESTful API routes for Holberton
"""
from os import chdir, getcwd, path
from shlex import quote, split
from shutil import rmtree
from subprocess import run
from tempfile import mkdtemp
from flask import abort, jsonify, make_response, request
from rhinoscraper import create_session, get_soup, rhinoscrape
from . import app_views

AUTH_KEYS = {'hbtn_user', 'hbtn_pass', 'hbtn_api_key', 'github_pass'}


@app_views.route("/holberton/<project_id>", methods=['POST'])
def holberton_project(project_id):
    """Log into holberton and retrieve a project given it's ID
    Params:
    hbtn_user
    hbtn_pass
    hbtn_api key
    github_pass
    """
    data = request.get_json()
    if AUTH_KEYS <= data.keys():
        abort(400)
    auth_token = get_hbtn_auth_token(
        data['hbtn_user'], data['hbtn_pass'], data['hbtn_api_key']
    )
    user_info = get_hbtn_user_info(auth_token)
    project_info = get_hbtn_project_info(project_id, auth_token)

    with create_session(data['hbtn_user'], data['hbtn_pass']) as sess:
        resp = sess.get('https://intranet.hbtn.io/auth/sign_in')
        soup = get_soup(resp.content, project_id)
        # Get info from checker API
    oldcwd = getcwd()
    tmpdir = mkdtemp()
    chdir(tmpdir)
    rhinocreate(soup,
                git_user=user_info['github_username'],
                git_pass=data['github_pass'],
                git_repo=project_info['tasks'][0]['github_repo'],
                git_name=user_info['full_name'])
    chdir(oldcwd)
    rmtree(tmpdir, ignore_errors=True)
    return make_response(jsonify({}), 200)


def rhinocreate(soup, git_user, git_pass, git_repo, git_name):
    """Scrape project and perform git operations
    """
    # Do git stuff
    git_url = 'https://{user}:{password}@github.com/{user}/{repo}.git'.format(
        user=git_user, password=git_pass, repo=git_repo)

    git_dir = path.join(getcwd(), git_repo)
    run(split('git clone {} {}'.format(quote(git_url), quote(git_dir))))
    chdir(git_dir)
    rhinoscrape(soup, git_user, git_name)

    commit_msg = 'Project committed by RhinoRepo'
    run(split('git add *'))
    run(split('git commit -m {}'.format(quote(commit_msg))))
    run(split('git push {}'.format(quote(git_url))))


def get_hbtn_auth_token(hbtn_user, hbtn_pass, hbtn_api_key):
    """Get holberton auth token
    """
    url = 'https://intranet.hbtn.io/users/auth_token.json'
    params = {
        'api_key': hbtn_api_key,
        'email': hbtn_user,
        'password': hbtn_pass,
        'scope': 'checker'
    }
    resp = request.post(url, params=params)
    return resp.json().get('auth_token')


def get_hbtn_user_info(auth_token):
    """Get holberton project info
    """
    url = 'https://intranet.hbtn.io/users/users/me.json'
    params = {'auth_token': auth_token}
    resp = request.get(url, params=params)
    return resp.json()


def get_hbtn_project_info(project_id, auth_token):
    """Get holberton project info
    """
    url = 'https://intranet.hbtn.io/users/projects/{}.json'.format(project_id)
    params = {'auth_token': auth_token, 'id': project_id}
    resp = request.get(url, params=params)
    return resp.json()
