#!/usr/bin/env python3
"""
Provides a class to scrape project data and create project files
"""
import os
import re
import stat as st
from bs4 import BeautifulSoup
from . scrapers.high_scraper import HighScraper
from . scrapers.low_scraper import LowScraper
from . scrapers.sys_scraper import SysScraper
from . scrapers.test_file_scraper import TestFileScraper



class RhinoProject:
    """
    Definition of a class to scrape project data and create project files
    """
    def __init__(self, soup):
        """
        Instantiate a RhinoProject with a BeautifulSoup object
        """
        if not isinstance(soup, BeautifulSoup):
            raise TypeError("'soup' must be a 'BeautifulSoup'")
        self.soup = soup
        self.project_name = self.scrape_name()
        self.project_type = self.scrape_type()

    def scrape_name(self):
        """
        Scrape the project directory name by locating 'Directory:'
        Return the project directory name
        """
        pattern = re.compile(r'^directory:\s+', flags=re.I)
        element = self.soup.find(string=pattern)
        if element is None:
            raise ValueError('Unable to determine project name')
        return element.next_element.text

    def scrape_type(self):
        """
        Scrape the project type by locating 'GitHub repository:'
        Return the project type
        """
        pattern = re.compile(r'^github\s+repository:\s+', flags=re.I)
        element = self.soup.find(string=pattern)
        if element is None:
            raise ValueError('Unable to determine project type')
        return element.next_sibling.text

    def run(self):
        """
        Scrape project data based on the project type and write project files
        Return an absolute path to the project directory
        """
        oldcwd = os.getcwd()
        os.mkdir(self.project_name)
        os.chdir(self.project_name)
        try:
            if re.match(r'\bhigh\b', self.project_type, flags=re.I):
                task_scraper = HighScraper(self.soup)
            elif re.match(r'\blow\b', self.project_type, flags=re.I):
                task_scraper = LowScraper(self.soup)
            elif re.match(r'\bsystem\b', self.project_type, flags=re.I):
                task_scraper = SysScraper(self.soup)
            else:
                raise ValueError("Project type must be high, low or system")
            test_scraper = TestFileScraper(self.soup)
            task_scraper.write_files()
            test_scraper.write_test_files()
            for name in os.listdir():
                try:
                    os.chmod(name, st.S_IRWXU | st.S_IRGRP | st.S_IROTH)
                except OSError:
                    pass
        except Exception:
            os.chdir(oldcwd)
            raise
        else:
            os.chdir(oldcwd)
