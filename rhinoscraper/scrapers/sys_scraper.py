#!/usr/bin/env python3
"""Module for SysScraper"""
import re
import sys


class SysScraper:
    """SysScraper class

    System-Engineering_Devops project scraper.

    Args:
        soup (obj): BeautifulSoup obj containing parsed link

    Attributes:
        ruby_check (str): if ruby exists, assign to 0. Else scrape empty list
        file_names (list): scraped file names from find_files()
    """

    def __init__(self, soup):
        self.soup = soup
        self.file_names = self.find_files()
        self.ruby_check = self.ruby_checker()

    def ruby_checker(self):
        """Method that checks for ruby files in project
        """
        tmp = self.soup.find_all(string=re.compile("env ruby"))
        if tmp != []:
            return 0
        return tmp

    def find_files(self):
        """Method that scrapes bash or ruby for file names"""
        return self.soup.find_all(string=re.compile("File: "))

    def write_files(self):
        """Method that writes/creates bash or ruby files"""
        print("> Creating task files...")
        for item in self.file_names:
            try:
                w_file_name = open(item.next_sibling.text, "w")
                if self.ruby_check == 0:
                    w_file_name.write("#!/usr/bin/env ruby\n")
                elif ".py" in item.next_sibling.text:
                    w_file_name.write("#!/usr/bin/python3\n")
                else:
                    w_file_name.write("#!/usr/bin/env bash\n")
                w_file_name.close()
            except (AttributeError, IndexError):
                try:
                    print("* [ERROR] Failed to write", item.next_sibling.text,
                          file=sys.stderr)
                except AttributeError:
                    print("* [ERROR] Failed to find task files",
                          file=sys.stderr)
                continue
