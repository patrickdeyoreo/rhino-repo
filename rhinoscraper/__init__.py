#!/usr/bin/env python3
"""
Provides the rhinoscraper module
"""
import requests
from bs4 import BeautifulSoup
from . rhinoproject import RhinoProject
from . rhinoread import RhinoRead


def rhinoscrape(soup, github_username, author):
    """
    Run the rhinoproject and rhinoreadme scrapers
    """
    rhinoproject = RhinoProject(soup)
    rhinoread = RhinoRead(soup, github_username, author)
    rhinoproject.run()
    rhinoread.run()


def get_soup(session, project):
    """
    Request project data and parse it with BeautifulSoup
    Return parsed HTML as a BeautifulSoup object
    """
    resp = session.get('https://intranet.hbtn.io/projects/{}'.format(project))
    if 200 <= resp.status_code < 300:
        return BeautifulSoup(resp.content, features='html.parser')
    return None


def create_session(hbtn_username, hbtn_password):
    """
    Log in to intranet.hbtn.io
    Return the login session
    """
    auth_url = 'https://intranet.hbtn.io/auth/sign_in'
    with requests.Session() as session:
        resp = session.get(auth_url)
        soup = BeautifulSoup(resp.content, features='html.parser')
        try:
            auth_data = {
                'user[login]': hbtn_username,
                'user[password]': hbtn_password,
                'authenticity_token': soup.find(
                    'input', {'name': 'authenticity_token'}
                ).get('value'),
                'commit': soup.find(
                    'input', {'name': 'commit'}
                ).get('value'),
            }
        except AttributeError:
            pass
        else:
            resp = session.post(auth_url, data=auth_data)
            if 200 <= resp.status_code < 300:
                return session
    return None
