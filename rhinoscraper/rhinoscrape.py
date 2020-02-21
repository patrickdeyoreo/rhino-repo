#!/usr/bin/env python3
"""
Run the project and README scrapers
"""
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from scrapers.high_scraper import HighScraper
from scrapers.low_scraper import LowScraper
from scrapers.read_scraper import ReadScraper
from scrapers.sys_scraper import SysScraper
from scrapers.test_file_scraper import TestFileScraper


def create_session(username, password):
    """Log in and return a session
    """
    with requests.Session() as session:
        auth_url = 'https://intranet.hbtn.io/auth/sign_in'
        resp = session.get(auth_url)
        soup = BeautifulSoup(resp.content, features='html.parser')
        try:
            token = soup.find('input', {'name': 'authenticity_token'})
            if token is None:
                return None
            commit = soup.find('input', {'name': 'commit'})
            if commit is None:
                return None
            auth_data = {
                'user[login]': username,
                'user[password]': password,
                'authenticity_token': token.get('value'),
                'commit': commit.get('value')
            }
            session.post(auth_url, data=auth_data)
            return session
        except AttributeError:
            print("[ERROR] Login failed (are your credentials correct?")
            return None


def hippoproject(soup):
    """Run the scrapers

    Scrapes project type (low level, high level, or system engineer),
    then it checks project type to execute appropriate scrapes.
    """
    find_directory(soup)
    create_directory(soup)

    project_type = project_type_check(soup)
    if "high" in project_type:
        # Creating scraping objects
        high_scraper = HighScraper(soup)
        test_scraper = TestFileScraper(soup)

        # Writing to files with scraped data
        high_scraper.write_files()

        # Creating test (main) files
        test_scraper.write_test_files()

    elif "low" in project_type:
        # Creating scraping objects
        low_scraper = LowScraper(soup)
        test_scraper = TestFileScraper(soup)

        # Writing to files with scraped data
        low_scraper.write_putchar()
        low_scraper.write_header()
        low_scraper.write_files()

        # Creating test (main) files
        test_scraper.write_test_files()

    elif "system" in project_type:
        # Creating scraping objects
        sys_scraper = SysScraper(soup)
        test_scraper = TestFileScraper(soup)

        # Creating test (main) files
        test_scraper.write_test_files()

        # Writing to files with scraped data
        sys_scraper.write_files()

    else:
        print("[ERROR]: Could not determine project type")

    set_permissions()


def hipporead(soup, author, username):
    """Entry point for hipporeader

    Scrapes for specific text to create a README automatically.
    """

    # Creating scraping object
    r_scraper = ReadScraper(soup)

    # Writing to README.md with scraped data
    r_scraper.open_readme()
    r_scraper.write_title()
    r_scraper.write_info()
    r_scraper.write_tasks()

    r_scraper.write_footer(author, username, f'https://github.com/{username}')


def get_soup(session, project):
    """Method that parses the `hbtn_link` with BeautifulSoup

    Initially logs in the intranet using mechanize and cookiejar.
    Then requests for the html of the link, and sets it into `soup`.

    Returns:
        soup (obj): BeautifulSoup parsed html object
    """
    try:
        resp = session.get(f'https://intranet.hbtn.io/projects/{project}')
        soup = BeautifulSoup(resp.content, features='html.parser')
        return soup
    except AttributeError:
        print("[ERROR] Login failed (are your credentials correct?")
        return None


def find_directory(soup):
    """Method that scrapes for project's directory name

    Sets project's directory's name to `dir_name`
    """
    find_dir = soup.find(string=re.compile("Directory: "))
    find_dir_text = find_dir.next_element.text
    return find_dir_text


def create_directory(directory):
    """Method that creates appropriate directory"""
    sys.stdout.write("  -> Creating directory... ")
    try:
        os.mkdir(directory)
        os.chdir(directory)
    except OSError:
        print("[ERROR] Failed to create directory")


def project_type_check(soup):
    """Method that checks the project's type

    Checks for which scraper to use by scraping 'Github repository: '

    Returns:
        project (str): scraped project type
    """
    find_project = soup.find(string=re.compile("GitHub repository: "))
    project = find_project.next_sibling.text
    return project


def set_permissions():
    """Method that sets permissions on files
    """
    try:
        os.system("chmod u+x *")
        print("done")
    except OSError:
        print("[ERROR] Failed to set permissions")
