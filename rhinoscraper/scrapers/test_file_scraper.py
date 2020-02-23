#!/usr/bin/env python3
"""Module for TestFileScraper"""
import sys


class TestFileScraper:
    """TestFileScraper class

    Scrapes test files from any projects.

    Args:
        soup (obj): BeautifulSoup obj containing parsed link
    """
    def __init__(self, soup):
        """Initialize a test file scraper
        """
        self.soup = soup
        self.pre = self.find_test_files()

    def find_test_files(self):
        """Find test files
        """
        return self.soup.select("pre")

    def write_test_files(self):
        """Write test files
        """
        print("> Writing test files...")
        for item in self.pre:
            find_c = item.text.find("main.c")
            find_html = item.text.find(".html")
            find_js = item.text.find(".js")
            find_py = item.text.find(".py")
            find_sql = item.text.find(".sql")
            find_test = item.text.find("cat")

            # find_main checks if there are main files on project page
            if find_test != -1 and any([
                    i != -1 for i in
                    [find_c, find_html, find_js, find_py, find_sql]
            ]):
                try:
                    name = item.text.split("cat ", 1)[1]
                    user = item.text.split("$", 1)[0]
                    if find_c != -1:
                        name = name.split(".c", 1)[0] + ".c"
                    elif find_sql != -1:
                        name = name.split(".sql", 1)[0] + ".sql"
                    elif find_js != -1:
                        name = name.split(".js", 1)[0] + ".js"
                    else:
                        name = name.split(".py", 1)[0] + ".py"
                    # html edge case test text creation
                    if find_html != -1:
                        text = item.text.split(".html")[1]
                        text = str(text.split(user, 1)[0])
                        text = text.split("\n", 1)[1]
                        name = name.split(".html", 1)[0] + ".html"
                    else:
                        text = item.text.split(name, 1)[1]
                        text = text.split("\n", 1)[1]
                        text = text.split(user, 1)[0]
                        text = text.split("\n")
                    w_test_file = open(name, "w+")
                    for i in range(len(text) - 1):
                        if find_html != -1:
                            w_test_file.write(text[i])
                        else:
                            w_test_file.write(text[i] + '\n')
                    w_test_file.close()
                except (AttributeError, IndexError):
                    name = item.text
                    newlines = 0
                    # Checks if test file's name has more than 1 newline
                    for i in name:
                        if newlines > 1:
                            name = "[Not a test file]"
                            break
                        if i == "\n":
                            newlines += 1
                    print("* [ERROR] Could not create test file", name,
                          file=sys.stderr)
                    continue
                except IOError:
                    print("* [ERROR] Could not create a test file",
                          file=sys.stderr)
                    continue
            else:
                pass
