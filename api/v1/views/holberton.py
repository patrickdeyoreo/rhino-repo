#!/usr/bin/env python3
"""
Provides RESTful API routes for Holberton
"""
import os
import shlex
import shutil
import subprocess
import tempfile
import flask
import requests
from rhinoscraper import create_session, get_soup, rhinoscrape
from . import app_views

AUTH_KEYS = {'hbtn_user', 'hbtn_pass', 'hbtn_api_key', 'github_pass'}


@app_views.route("/<project_id>", methods=['POST'])
def hbtn_project(project_id):
    """
    Log into holberton and retrieve a project given it's ID
    Params:
    hbtn_user
    hbtn_pass
    hbtn_api_key
    github_pass
    """
    auth = flask.request.get_json()
    if AUTH_KEYS - auth.keys():
        flask.abort(400)
    auth['hbtn_user'] = auth['hbtn_user'].split('@')[0]
    if not auth['hbtn_user'].isnumeric():
        flask.abort(400)
    auth['hbtn_user'] = '@'.join([
        auth['hbtn_user'], 'holbertonschool.com'
    ])
    auth['hbtn_token'] = hbtn_auth_token(
        auth['hbtn_user'], auth['hbtn_pass'], auth['hbtn_api_key']
    )
    user = hbtn_user(auth['hbtn_token'])
    proj = hbtn_project(project_id, auth['hbtn_token'])
    repo = proj['tasks'][0]['github_repo']
    with create_session(auth['hbtn_user'], auth['hbtn_pass']) as session:
        new_project(get_soup(session, project_id),
                    github_user=user['github_user'],
                    github_pass=auth['github_pass'],
                    github_name=user['full_name'],
                    github_repo=repo)
    return (os.path.join(repo, proj['name']), 200)


def new_project(soup, github_user, github_pass, github_repo, github_name):
    """Scrape project and perform git operations
    """
    giturl = 'https://{user}:{password}@github.com/{user}/{repo}.git'.format(
        user=github_user, password=github_pass, repo=github_repo
    )
    oldcwd = os.getcwd()
    tmpdir = tempfile.mkdtemp()
    gitdir = os.path.join(tmpdir, github_repo)
    cmd = 'git clone {} {}'.format(shlex.quote(giturl), shlex.quote(gitdir))
    subprocess.run(shlex.split(cmd), check=False)
    os.chdir(gitdir)
    rhinoscrape(soup, github_user, github_name)
    cmd = 'git add .'
    subprocess.run(shlex.split(cmd), check=False)
    msg = 'Project committed by Rhino Repo'
    cmd = 'git commit -m {}'.format(shlex.quote(msg))
    subprocess.run(shlex.split(cmd), check=False)
    cmd = 'git push {}'.format(shlex.quote(giturl))
    subprocess.run(shlex.split(cmd), check=False)
    os.chdir(oldcwd)
    shutil.rmtree(tmpdir, ignore_errors=True)


def hbtn_auth_token(hbtn_user, hbtn_pass, hbtn_api_key):
    """Get holberton auth token
    """
    url = 'https://intranet.hbtn.io/users/auth_token.json'
    params = {
        'api_key': hbtn_api_key,
        'email': hbtn_user,
        'password': hbtn_pass,
        'scope': 'checker'
    }
    resp = requests.post(url, params=params)
    return resp.json().get('auth_token')


def hbtn_user(auth_token):
    """Get holberton project info
    """
    url = 'https://intranet.hbtn.io/users/me.json'
    params = {'auth_token': auth_token}
    resp = requests.get(url, params=params)
    return resp.json()


def hbtn_project(project_id, auth_token):
    """Get holberton project info
    """
    url = 'https://intranet.hbtn.io/projects/{}.json'.format(project_id)
    params = {'auth_token': auth_token, 'id': project_id}
    resp = requests.get(url, params=params)
    return resp.json()
