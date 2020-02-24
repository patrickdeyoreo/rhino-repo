#!/usr/bin/env python3
"""
Provides RESTful API routes for Holberton
"""
from os import chdir, getcwd, path
from re import match
from shlex import quote, split
from shutil import rmtree
from subprocess import run
from tempfile import mkdtemp
from flask import abort, jsonify, make_response, request
from requests import get, post
from rhinoscraper import create_session, get_soup, rhinoscrape
from . import app_views

AUTH_KEYS = {
    'hbtn_user',
    'hbtn_pass',
    'hbtn_api_key',
    'github_pass'
}


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
    auth = request.get_json()
    if AUTH_KEYS - auth.keys():
        abort(400)
    auth['hbtn_user'] = auth['hbtn_user'].split('@')[0]
    if not auth['hbtn_user'].isnumeric():
        abort(400)
    auth['hbtn_user'] = '@'.join([
        auth['hbtn_user'], 'holbertonschool.com'
    ])
    auth_token = hbtn_auth_token(
        auth['hbtn_user'],
        auth['hbtn_pass'],
        auth['hbtn_api_key']
    )
    user = hbtn_user_info(auth_token)
    project = hbtn_project_info(project_id, auth_token)
    project_name = project['name']
    project_repo = project['tasks'][0]['github_repo']
    with create_session(auth['hbtn_user'], auth['hbtn_pass']) as session:
        create_project(
            get_soup(session, project_id),
            github_user=user['github_user'],
            github_pass=auth['github_pass'],
            github_name=user['full_name'],
            github_repo=project_repo,
        )
    return make_response(path.join(project_repo, project_name), 200)


def create_project(soup, github_user, github_pass, github_repo, github_name):
    """Scrape project and perform git operations
    """
    oldcwd = getcwd()
    tmpdir = mkdtemp()
    gitdir = path.join(tmpdir, github_repo)
    giturl = 'https://{user}:{password}@github.com/{user}/{repo}.git'.format(
        user=github_user, password=github_pass, repo=github_repo
    )
    run(split('git clone {} {}'.format(quote(giturl), quote(gitdir))))
    chdir(gitdir)
    rhinoscrape(soup, github_user, github_name)
    run(split('git add *'), check=False)
    message = 'Project committed by Rhino Repo'
    run(split('git commit -m {}'.format(quote(message))))
    run(split('git push {}'.format(quote(giturl))))
    chdir(oldcwd)
    rmtree(tmpdir, ignore_errors=True)


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
    resp = post(url, params=params)
    return resp.json().get('auth_token')


def hbtn_user_info(auth_token):
    """Get holberton project info
    """
    url = 'https://intranet.hbtn.io/users/me.json'
    params = {'auth_token': auth_token}
    resp = get(url, params=params)
    return resp.json()


def hbtn_project_info(project_id, auth_token):
    """Get holberton project info
    """
    url = 'https://intranet.hbtn.io/projects/{}.json'.format(project_id)
    params = {'auth_token': auth_token, 'id': project_id}
    resp = get(url, params=params)
    return resp.json()
