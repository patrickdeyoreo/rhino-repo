#!/usr/bin/env python3
"""
Provides a class for scraping low-level projects
"""
import re
import sys
from bs4 import BeautifulSoup

PUTCHAR = """
#include <unistd.h>

/**
 * _putchar - writes a character to stdout
 * @c: the character to print
 *
 * Return: On success, 1 is returned.
 * On error, -1 is returned, and errno is set appropriately.
 */
int _putchar(char c)
{
\treturn (write(1, &c, 1));
}
"""


class LowScraper:
    """
    Low-Level_Programming project scraper.
    Public instance methods:
        detect_putchar
        scrape_prototypes
        scrape_header
        write_putchar
        write_header
        write_files

    Public instance attributes:
        putchar_required: bool: requires custom '_putchar.c'
        header: str: C header content
        prototypes: list: function prototypes
        files: list: project files
    """
    def __init__(self, soup: BeautifulSoup):
        """
        Instantiate a LowScraper with a BeautifulSoup object
        Args:
            soup: BeautifulSoup: Parsed HTML from a Holberton project
        """
        if not isinstance(soup, BeautifulSoup):
            raise TypeError("'soup' must be a 'BeautifulSoup'")
        self.soup = soup
        self.detect_putchar()
        self.scrape_header()
        self.scrape_prototypes()
        self.scrape_files()

    def detect_putchar(self):
        """
        Check if custom '_putchar' is required
        Returns
        """
        print("> Checking if a custom '_putchar' is required...")
        regex = re.compile(r'^you\s+are\s+allowed\s+to\s+use\b', flags=re.I)
        match = self.soup.find(string=regex)
        try:
            self.putchar_required = match.next_sibling.text == '_putchar'
        except (TypeError, ValueError):
            self.putchar_required = False
        return self.putchar_required

    def scrape_header(self):
        """
        Scrape C header file name
        """
        print("> Scraping name of header file...")
        try:
            regex = re.compile(r'\bforget\s+to\s+push\s+your\s+header\s+file')
            match = self.soup.find(string=regex).previous_element
            self.header = match.previous_element.previous_element
        except AttributeError:
            self.header = None
        return self.header

    def scrape_prototypes(self):
        """
        Scrape C prototypes
        """
        print("> Scraping function prototypes...")
        if self.putchar_required:
            self.prototypes = ['int _putchar(char c)']
        else:
            self.prototypes = []
        regex = re.compile(r"\bprototype:\s", flags=re.I)
        self.prototypes.extend([element.next_sibling.text.replace(';', '') for
                                element in self.soup.find_all(string=regex)])
        return self.prototypes

    def scrape_files(self):
        """
        Scrape C file names
        """
        print("> Scraping file names...")
        regex = re.compile(r'\bfile: ', flags=re.I)
        self.files = self.soup.find_all(string=regex) or []
        return self.files

    def write_putchar(self):
        """
        Write '_putchar' if required
        """
        if self.putchar_required:
            print("> Writing '_putchar.c'...")
            try:
                with open('_putchar.c', 'w') as ofile:
                    print(PUTCHAR.strip(), file=ofile)
            except OSError:
                pass

    def write_header(self):
        """
        Write C header file (if required)
        """
        if self.header:
            print("> Writing header file... ")
            try:
                include_guard = self.header.replace('.', '_', 1).upper()
                prototypes = ['{};'.format(s) for s in self.prototypes]
                with open(self.header, 'w') as ofile:
                    print('#ifndef {}'.format(include_guard), file=ofile)
                    print('#define {}'.format(include_guard), file=ofile)
                    print('', file=ofile)
                    print('#include <stdio.h>', file=ofile)
                    print('#include <stdlib.h>', file=ofile)
                    print('', file=ofile)
                    print(*prototypes, sep='\n', file=ofile)
                    print('', file=ofile)
                    print('#endif /* {} */'.format(include_guard), file=ofile)
            except (AttributeError, OSError):
                print("* [ERROR] Failed to write header file", self.header,
                      file=sys.stderr)

    def write_files(self):
        """
        Write project files
        Handles multiple file names by searching for ','.
        """
        self.write_header()
        self.write_putchar()
        print("> Writing task files...")
        for element, prototype in zip(self.files, self.prototypes):
            try:
                filename = element.next_sibling.text.split(",")[0]
                funcname = prototype.split("(", maxsplit=1)[0].split(" ")
                funcname = funcname[len(funcname)-1].split("*")
                funcname = funcname[len(funcname)-1]
                if self.header is not None:
                    with open(filename, 'w') as ofile:
                        print('#include', self.header, file=ofile)
                        print('', file=ofile)
                        print('/**', file=ofile)
                        print(' *', funcname, '-', file=ofile)
                        print(' *', file=ofile)
                        print(' * Return:', file=ofile)
                        print(' */', file=ofile)
                        print(prototype, file=ofile)
                        print('{', file=ofile)
                        print('', file=ofile)
                        print('}', file=ofile)
            except (AttributeError, OSError):
                print("* [ERROR] Failed to write task file", filename,
                      file=sys.stderr)

    def write_checker(self):
        """
        Write betty style checker
        """
        try:
            line = ['betty']
            if self.header:
                line.append(self.header)
            if self.files:
                line.extend([item.next_sibling.text for item in self.files])
            with open('check.sh', 'w') as ofile:
                print('#!/usr/bin/env bash', file=ofile)
                print(*line, file=ofile)
        except (OSError, TypeError, ValueError):
            pass
