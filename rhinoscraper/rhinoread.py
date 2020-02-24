#!/usr/bin/env python3
"""
Provides a class to scrape project data and produce a README
"""
from . scrapers.read_scraper import ReadScraper


class RhinoRead(ReadScraper):
    """
    Definition of a class to scrape project data and create project files
    """
    def __init__(self, soup, github_user, github_name):
        """
        Instantiate a RhinoRead object
        """
        super().__init__(soup)
        if not isinstance(github_user, str):
            raise TypeError("'user' must be a 'str'")
        if not isinstance(github_name, str):
            raise TypeError("'name' must be a 'str'")
        self.user = github_user
        self.name = github_name

    def run(self):
        """
        Scrape project data and create a README
        """
        # Write README.md with scraped data
        self.open_readme()
        self.write_title()
        self.write_info()
        self.write_tasks()
        profile = 'https://github.com/{}'.format(self.user)
        self.write_footer(self.name, self.user, profile)
