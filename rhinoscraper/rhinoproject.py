#!/usr/bin/env python3
"""
Run the project and README scrapers
"""
import os
import re
import sys
import stat as st
from . scrapers.high_scraper import HighScraper
from . scrapers.low_scraper import LowScraper
from . scrapers.sys_scraper import SysScraper
from . scrapers.test_file_scraper import TestFileScraper


def rhinoproject(soup):
    """Run the scrapers

    Scrapes project type (low level, high level, or system engineer),
    then it checks project type to execute appropriate scrapes.
    """
    mkcd(find_directory(soup))

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


def find_directory(soup):
    """Method that scrapes for project's directory name

    Sets project's directory's name to `dir_name`
    """
    find_dir = soup.find(string=re.compile("Directory: "))
    find_dir_text = find_dir.next_element.text
    return find_dir_text


def mkcd(directory):
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
    perms = st.S_IRWXU | st.S_IRGRP | st.S_IWGRP | st.S_IROTH | st.S_IWOTH
    for name in os.listdir():
        try:
            os.chmod(name, perms)
        except OSError:
            pass
