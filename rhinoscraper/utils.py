#!/usr/bin/env python3
"""
Run the project and README scrapers
"""
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from rhinoscraper.scrapers.high_scraper import HighScraper
from rhinoscraper.scrapers.low_scraper import LowScraper
from rhinoscraper.scrapers.read_scraper import ReadScraper
from rhinoscraper.scrapers.sys_scraper import SysScraper
from rhinoscraper.scrapers.test_file_scraper import TestFileScraper


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
