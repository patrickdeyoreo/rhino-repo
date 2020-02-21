#!/usr/bin/env python3
"""
Provides the rhinoscraper module
"""
import requests
from bs4 import BeautifulSoup
from . rhinoproject import rhinoproject
from . rhinoread import rhinoread


def create_session(username, password):
    """Log in and return a session
    """
    auth_url = 'https://intranet.hbtn.io/auth/sign_in'
    with requests.Session() as session:
        resp = session.get(auth_url)
        soup = BeautifulSoup(resp.content, features='html.parser')
        token = soup.find('input', {'name': 'authenticity_token'})
        commit = soup.find('input', {'name': 'commit'})
        if token and commit:
            auth_data = {
                'user[login]': username,
                'user[password]': password,
                'authenticity_token': token.get('value'),
                'commit': commit.get('value'),
            }
            resp = session.post(auth_url, data=auth_data)
            if 200 <= resp.status_code < 300:
                return session
    return None


def get_soup(session, project_id):
    """Method that parses the `hbtn_link` with BeautifulSoup

    Initially logs in the intranet using mechanize and cookiejar.
    Then requests for the html of the link, and sets it into `soup`.

    Returns:
        soup (obj): BeautifulSoup parsed html object
    """
    try:
        resp = session.get(
            'https://intranet.hbtn.io/projects/{}'.format(project_id))
        soup = BeautifulSoup(resp.content, features='html.parser')
        return soup
    except AttributeError:
        print("[ERROR] Login failed (are your credentials correct?")
        return None


def rhinoscrape(soup, username, author):
    """Run the rhino project and rhino read
    """
    rhinoproject(soup)
    rhinoread(soup, username, author)
