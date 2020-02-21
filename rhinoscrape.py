#!/usr/bin/env python3
"""
Run the project and README scrapers
"""
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from rhinoscraper.rhinoscrape import create_session, get_soup
from rhinoscraper.rhinoproject import rhinoproject
from rhinoscraper.rhinoread import rhinoread


if __name__ == '__main__':
    sess = create_session(sys.argv[1], sys.argv[2])
    soup = get_soup(sess, sys.argv[3])
    rhinoproject(soup)
