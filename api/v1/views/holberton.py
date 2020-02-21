#!/usr/bin/env python3
"""
Provides RESTful API routes for Holberton
"""
from os import chdir, getcwd, path
from shutil import rmtree
from tempfile import mkdtemp
from flask import abort, jsonify, make_response, request
from rhinoscraper import create_session, get_soup
from rhinoscraper.rhinoproject import rhinoproject
from rhinoscraper.rhinoread import rhinoread
from subprocess import run
from shlex import quote, split
from . import app_views

AUTH_KEYS = {'hbtn_user', 'hbtn_pass', 'hbtn_api_key', 'github_pass'}


@app_views.route("/holberton/<project_id>", methods=['POST'])
def holberton_project(project_id):
    """Log into holberton and retrieve a project given it's ID
    Params:
    hbtn user
    hbtn pass
    hbtn api key
    github pass
    """
    data = request.get_json()
    if AUTH_KEYS <= data.keys():
        abort(400)
    auth_token = get_hbtn_auth_token(
        data['hbtn_user'], data['hbtn_pass'], data['hbtn_api_key']
    )
    user_info = get_hbtn_user_info(auth_token)
    git_info = {
        'user': user_info['github_username'],
        'pass': data['github_pass'],
        'name': data['full_name'],
        'repo': user_info['github_username'],
    }
    project_info = get_hbtn_project_info(project_id, auth_token)

    with create_session(data['hbtn_user'], data['hbtn_pass']) as sess:
        resp = sess.get('https://intranet.hbtn.io/auth/sign_in')
        soup = get_soup(resp.content, project_id)
        # Get info from checker API
        oldcwd = getcwd()
        tmpdir = mkdtemp()
        chdir(tmpdir)
        rhinoscrape(soup, project_id,
                    git_info['user'], git_info['pass'],
                    git_info['repo'], git_info['name'])
        chdir(oldcwd)
        rmtree(tmpdir, ignore_errors=True)

    return {}, 200


def rhinoscrape(soup, project_id, git_user, git_pass, git_repo, git_name):
    """Scrape project and perform git operations
    """
    # Do git stuff
    rhinoproject(soup)
    rhinoread(soup, git_user, git_name)
    git_url = 'https://{user}:{passwd}@github.com/{user}/{repo}.git'.format(
        user=git_user, passwd=git_pass, repo=git_repo)
    git_dir = path.join(getcwd(), git_repo)
    cmd = 'git clone {} {}'.format(quote(git_url), quote(git_dir))
    run(split(cmd))
    cmd = 'cp -nr {} {}'.format(quote(project_dir), quote(git_dir))
    run(split(cmd))
    cmd = 'git add {}'.format(quote(path.basename(git_dir)))
    run(split(cmd))
    cmd = 'git commit -m {}'.format(
        quote('Project {id} committed by RhinoRepo'.format(project_id)))
    run(split(cmd))
    cmd = 'git push {}'.format(quote(git_url))
    run(split(cmd))


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
    resp = request.get(url, params={'auth_token': auth_token})
    return resp.json()


def get_hbtn_project_info(project_id, auth_token):
    """Get holberton project info
    """
    url = 'https://intranet.hbtn.io/users/projects/{}.json'.format(project_id)
    resp = request.get(url, params={'auth_token': auth_token, 'id': project_id})
    return resp.json()
