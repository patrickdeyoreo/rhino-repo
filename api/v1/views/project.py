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

AUTH_KEYS = {'hbtn_email', 'hbtn_password', 'hbtn_api_key', 'github_password'}


@app_views.route("/<project_id>", methods=['POST'])
def hbtn_project(project_id):
    """
    Log into holberton and retrieve a project given it's ID
    Params:
    hbtn_email
    hbtn_password
    hbtn_api_key
    github_password
    """
    print(flask.request)
    auth = flask.request.get_json()
    if AUTH_KEYS - auth.keys():
        flask.abort(400)
    auth['hbtn_email'] = auth['hbtn_email'].split('@')[0]
    if not auth['hbtn_email'].isnumeric():
        flask.abort(400)
    auth['hbtn_email'] = '@'.join([
        auth['hbtn_email'], 'holbertonschool.com'
    ])
    auth['hbtn_token'] = hbtn_api_auth_token(
        auth['hbtn_email'], auth['hbtn_password'], auth['hbtn_api_key']
    )
    user = hbtn_api_user(auth['hbtn_token'])
    proj = hbtn_api_project(project_id, auth['hbtn_token'])
    repo = proj['tasks'][0]['github_repo']
    with create_session(auth['hbtn_email'], auth['hbtn_password']) as session:
        git_project(get_soup(session, project_id),
                    github_user=user['github_username'],
                    github_pass=auth['github_password'],
                    github_name=user['full_name'],
                    github_repo=repo)
    return (os.path.join(repo, proj['name']), 200)


def git_project(soup, github_user, github_pass, github_repo, github_name):
    """
    Scrape project and perform git operations
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


def hbtn_api_auth_token(hbtn_email, hbtn_password, hbtn_api_key):
    """
    Get holberton auth token
    """
    url = 'https://intranet.hbtn.io/users/auth_token.json'
    params = {
        'email': hbtn_email,
        'password': hbtn_password,
        'api_key': hbtn_api_key,
        'scope': 'checker'
    }
    resp = requests.post(url, params=params)
    return resp.json().get('auth_token')


def hbtn_api_user(hbtn_auth_token):
    """
    Get holberton user info
    """
    url = 'https://intranet.hbtn.io/users/me.json'
    resp = requests.get(url, params={'auth_token': hbtn_auth_token})
    return resp.json()


def hbtn_api_project(hbtn_project_id, hbtn_auth_token):
    """
    Get holberton project info
    """
    url = 'https://intranet.hbtn.io/projects/{}.json'.format(hbtn_project_id)
    params = {'auth_token': hbtn_auth_token, 'id': hbtn_project_id}
    resp = requests.get(url, params=params)
    return resp.json()
