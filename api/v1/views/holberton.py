#!/usr/bin/env python3
"""
Provides RESTful API routes for Holberton
"""
from os import chdir, getcwd, path
from requests import get, post
from shlex import quote, split
from shutil import rmtree
from subprocess import run
from tempfile import mkdtemp
from flask import abort, jsonify, make_response, request
from rhinoscraper import create_session, get_soup, rhinoscrape
from . import app_views

AUTH_KEYS = {
    'holberton_user',
    'holberton_pass',
    'holberton_api_key',
    'github_pass'
}


@app_views.route("/<project_id>", methods=['POST'])
def holberton_project(project_id):
    """Log into holberton and retrieve a project given it's ID
    Params:
    holberton_user
    holberton_pass
    holberton_api_key
    github_pass
    """
    data = request.get_json()
    print(data.keys())
    if AUTH_KEYS < data.keys():
        abort(400)
    auth_token = holberton_auth_token(
        data['holberton_user'],
        data['holberton_pass'],
        data['holberton_api_key'])
    user_info = holberton_user_info(auth_token)
    project_info = holberton_project_info(project_id, auth_token)
    project_name = project_info['name']
    project_repo = project_info['tasks'][0]['github_repo']

    with create_session(data['holberton_user'], data['holberton_pass']) as ses:
        soup = get_soup(ses, project_id)
    rhinocreate(soup,
                git_user=user_info['github_username'],
                git_pass=data['github_pass'],
                git_repo=project_info['tasks'][0]['github_repo'],
                git_name=user_info['full_name'])
    return make_response(jsonify(path.join(project_repo, project_name)), 200)


def rhinocreate(soup, git_user, git_pass, git_repo, git_name):
    """Scrape project and perform git operations
    """
    oldcwd = getcwd()
    tmpdir = mkdtemp()
    chdir(tmpdir)

    git_url = 'https://{user}:{password}@github.com/{user}/{repo}.git'.format(
        user=git_user, password=git_pass, repo=git_repo)
    git_dir = path.join(getcwd(), git_repo)
    run(split('git clone {} {}'.format(quote(git_url), quote(git_dir))))
    chdir(git_dir)

    rhinoscrape(soup, git_user, git_name)
    commit_msg = 'Project committed by Rhino Repo'
    run(split('git add *'))
    run(split('git commit -m {}'.format(quote(commit_msg))))
    run(split('git push {}'.format(quote(git_url))))

    chdir(oldcwd)
    rmtree(tmpdir, ignore_errors=True)


def holberton_auth_token(holberton_user, holberton_pass, holberton_api_key):
    """Get holberton auth token
    """
    url = 'https://intranet.hbtn.io/users/auth_token.json'
    params = {
        'api_key': holberton_api_key,
        'email': holberton_user,
        'password': holberton_pass,
        'scope': 'checker'
    }
    resp = post(url, params=params)
    return resp.json().get('auth_token')


def holberton_user_info(auth_token):
    """Get holberton project info
    """
    url = 'https://intranet.hbtn.io/users/me.json'
    params = {'auth_token': auth_token}
    resp = get(url, params=params)
    return resp.json()


def holberton_project_info(project_id, auth_token):
    """Get holberton project info
    """
    url = 'https://intranet.hbtn.io/projects/{}.json'.format(project_id)
    params = {'auth_token': auth_token, 'id': project_id}
    resp = get(url, params=params)
    return resp.json()
