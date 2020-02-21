#!/usr/bin/env python3
"""
Run the project and README scrapers
"""
from . scrapers.read_scraper import ReadScraper


def rhinoread(soup, author, username):
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
