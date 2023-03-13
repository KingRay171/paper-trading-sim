import os
from bs4 import BeautifulSoup


def get_xml_data(file, keyword):
    """Returns a ResultSet containing all instances of the given keyword in the given file"""
    currentdir = os.getcwd()
    return BeautifulSoup(open(currentdir + '\\' + file, 'r').read(), "xml").find_all(keyword)
