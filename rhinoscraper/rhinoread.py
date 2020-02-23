#!/usr/bin/env python3
"""
Provides a class to scrape project data and produce a README
"""
from . scrapers.read_scraper import ReadScraper


class RhinoRead(ReadScraper):
    """
    Definition of a class to scrape project data and create project files
    """
    def __init__(self, soup, user, name):
        """
        Instantiate a RhinoRead object
        """
        super().__init__(soup)
        if not isinstance(user, str):
            raise TypeError("'user' must be a 'str'")
        if not isinstance(name, str):
            raise TypeError("'name' must be a 'str'")
        self.user = user
        self.name = name

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
